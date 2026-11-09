"""Stockage des médias : écriture sur S3, lecture rétrocompatible sur le disque.

Problème à résoudre
-------------------
Les 46 fichiers déjà téléversés (≈64 Mio) sont servis par nginx depuis
``/home/cjk-api.io/media/`` sous ``https://api.cjkamenge.com/media/...``. Ces
liens sont deja publies : ils figurent dans la base (``ImageField.name``), dans
les pages indexees et dans les partages. Basculer purement et simplement le
stockage par defaut vers S3 reecrirait l'URL de **tous** ces fichiers, y compris
ceux qui ne sont pas sur S3, et casserait chaque image existante.

Solution
--------
``MediaRouterStorage`` compose deux backends et arbitre fichier par fichier :

* **ecriture** : tout nouveau fichier part sur S3 (RustFS, s3.rundinova.com) ;
* **lecture** : un fichier present sur le disque local est servi depuis le
  disque, avec exactement son URL d'origine ; tout le reste vient de S3.

Le critere est la presence du fichier dans ``MEDIA_ROOT``, c'est-a-dire un
simple ``stat()`` local, sans appel reseau. Aucun changement de schema, aucune
table de correspondance a maintenir, et aucun fichier existant n'est deplace ni
reecrit : la migration ne peut pas perdre de donnees.

Inerte tant que S3 n'est pas configure
--------------------------------------
Si ``AWS_STORAGE_BUCKET_NAME`` est vide, il n'y a pas de backend distant et
*tout* (lecture comme ecriture) reste sur le disque : le comportement est
identique a l'actuel. Le code peut donc etre deploye avant que les identifiants
S3 ne soient en place, et l'activation se fait ensuite par la seule variable
d'environnement.
"""

from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.functional import cached_property


class MediaRouterStorage(Storage):
    """Écrit les nouveaux médias sur S3, sert les anciens depuis le disque."""

    @cached_property
    def legacy(self):
        """Fichiers deja televerses, servis par nginx sous MEDIA_URL."""
        return FileSystemStorage(
            location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL
        )

    @cached_property
    def remote(self):
        """Backend S3, ou None tant que le bucket n'est pas configure."""
        if not getattr(settings, 'AWS_STORAGE_BUCKET_NAME', ''):
            return None
        # Import tardif : django-storages/boto3 ne sont pas requis pour faire
        # tourner le projet sans S3 (developpement local, CI).
        from storages.backends.s3boto3 import S3Boto3Storage

        return S3Boto3Storage()

    # -- arbitrage ---------------------------------------------------------

    def _backend_for(self, name):
        """Le disque fait foi pour tout fichier qui s'y trouve deja."""
        if self.remote is None:
            return self.legacy
        if self.legacy.exists(name):
            return self.legacy
        return self.remote

    @property
    def _write_backend(self):
        return self.remote or self.legacy

    # -- API Storage -------------------------------------------------------

    def _open(self, name, mode='rb'):
        return self._backend_for(name).open(name, mode)

    def _save(self, name, content):
        return self._write_backend.save(name, content)

    def delete(self, name):
        return self._backend_for(name).delete(name)

    def exists(self, name):
        """Vrai si le fichier existe dans l'un ou l'autre backend.

        L'union est indispensable : ``get_available_name`` s'appuie dessus pour
        trouver un nom libre. Sans elle, un nouveau fichier envoye sur S3
        pourrait porter le nom d'un fichier deja present sur le disque, et
        ``url()`` servirait alors l'ancien a la place du nouveau.
        """
        if self.legacy.exists(name):
            return True
        if self.remote is not None and self.remote.exists(name):
            return True
        return False

    def listdir(self, path):
        legacy_dirs, legacy_files = self.legacy.listdir(path)
        if self.remote is None:
            return legacy_dirs, legacy_files
        remote_dirs, remote_files = self.remote.listdir(path)
        return (
            sorted(set(legacy_dirs) | set(remote_dirs)),
            sorted(set(legacy_files) | set(remote_files)),
        )

    def size(self, name):
        return self._backend_for(name).size(name)

    def url(self, name):
        return self._backend_for(name).url(name)

    def path(self, name):
        """Chemin local, uniquement pour un fichier reellement sur le disque."""
        if self.legacy.exists(name):
            return self.legacy.path(name)
        raise NotImplementedError(
            f"{name} est stocke sur S3 : aucun chemin local n'existe."
        )

    def get_accessed_time(self, name):
        return self._backend_for(name).get_accessed_time(name)

    def get_created_time(self, name):
        return self._backend_for(name).get_created_time(name)

    def get_modified_time(self, name):
        return self._backend_for(name).get_modified_time(name)
