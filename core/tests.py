"""Tests de MediaRouterStorage.

Enjeu : la bascule vers S3 ne doit pas changer l'URL d'un seul fichier deja
televerse. Les 46 fichiers de production sont references en base et leurs liens
https://api.cjkamenge.com/media/... sont publies.
"""

import shutil
import tempfile
from pathlib import Path

from django.core.files.base import ContentFile
from django.test import SimpleTestCase, override_settings

from core.storages import MediaRouterStorage


class FakeRemoteStorage:
    """Backend distant en memoire, pour ne pas dependre d'un vrai S3."""

    def __init__(self, base_url='https://cdn.example.test/bucket/'):
        self.files = {}
        self.base_url = base_url

    def exists(self, name):
        return name in self.files

    def save(self, name, content):
        data = content.read() if hasattr(content, 'read') else content
        self.files[name] = data
        return name

    def open(self, name, mode='rb'):
        return ContentFile(self.files[name])

    def delete(self, name):
        self.files.pop(name, None)

    def size(self, name):
        return len(self.files[name])

    def url(self, name):
        return f'{self.base_url}{name}'

    def listdir(self, path):
        return [], [n for n in self.files if n.startswith(path)]


class MediaRouterStorageTests(SimpleTestCase):
    def setUp(self):
        self.media_root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)

        patcher = override_settings(
            MEDIA_ROOT=str(self.media_root), MEDIA_URL='media/'
        )
        patcher.enable()
        self.addCleanup(patcher.disable)

        self.storage = MediaRouterStorage()
        self.remote = FakeRemoteStorage()
        # cached_property : on injecte le faux backend sans toucher au reseau.
        self.storage.__dict__['remote'] = self.remote

    def _write_legacy(self, name, data=b'ancien'):
        path = self.media_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    # -- lecture -----------------------------------------------------------

    def test_fichier_existant_garde_son_url_disque(self):
        self._write_legacy('news/at7.png')

        self.assertEqual(self.storage.url('news/at7.png'), '/media/news/at7.png')

    def test_fichier_absent_du_disque_est_servi_par_s3(self):
        self.remote.save('activities/nouveau.jpg', b'neuf')

        self.assertEqual(
            self.storage.url('activities/nouveau.jpg'),
            'https://cdn.example.test/bucket/activities/nouveau.jpg',
        )

    def test_le_disque_gagne_quand_le_fichier_existe_des_deux_cotes(self):
        """Garantie centrale : un lien publie ne doit jamais changer."""
        self._write_legacy('news/at7.png', b'disque')
        self.remote.save('news/at7.png', b's3')

        self.assertEqual(self.storage.url('news/at7.png'), '/media/news/at7.png')
        with self.storage.open('news/at7.png') as handle:
            self.assertEqual(handle.read(), b'disque')

    # -- ecriture ----------------------------------------------------------

    def test_nouvelle_ecriture_part_sur_s3_et_pas_sur_le_disque(self):
        self.storage.save('activities/photo.jpg', ContentFile(b'contenu'))

        self.assertTrue(self.remote.exists('activities/photo.jpg'))
        self.assertFalse((self.media_root / 'activities/photo.jpg').exists())

    def test_nom_disponible_tient_compte_des_deux_backends(self):
        """Un nouveau fichier ne doit pas pouvoir masquer un fichier du disque."""
        self._write_legacy('news/at7.png')

        name = self.storage.save('news/at7.png', ContentFile(b'neuf'))

        self.assertNotEqual(name, 'news/at7.png')
        # L'ancien est intact et garde son URL.
        self.assertEqual((self.media_root / 'news/at7.png').read_bytes(), b'ancien')
        self.assertEqual(self.storage.url('news/at7.png'), '/media/news/at7.png')

    def test_suppression_cible_le_bon_backend(self):
        self._write_legacy('news/ancien.png')
        self.remote.save('news/recent.png', b'x')

        self.storage.delete('news/ancien.png')
        self.storage.delete('news/recent.png')

        self.assertFalse((self.media_root / 'news/ancien.png').exists())
        self.assertFalse(self.remote.exists('news/recent.png'))

    def test_exists_est_l_union_des_deux(self):
        self._write_legacy('a.png')
        self.remote.save('b.png', b'x')

        self.assertTrue(self.storage.exists('a.png'))
        self.assertTrue(self.storage.exists('b.png'))
        self.assertFalse(self.storage.exists('c.png'))

    def test_path_refuse_pour_un_objet_s3(self):
        self.remote.save('activities/sur-s3.jpg', b'x')

        with self.assertRaises(NotImplementedError):
            self.storage.path('activities/sur-s3.jpg')

    # -- S3 non configure ---------------------------------------------------

    def test_sans_s3_tout_reste_sur_le_disque(self):
        storage = MediaRouterStorage()
        storage.__dict__['remote'] = None

        storage.save('activities/local.jpg', ContentFile(b'x'))

        self.assertTrue((self.media_root / 'activities/local.jpg').exists())
        self.assertEqual(
            storage.url('activities/local.jpg'), '/media/activities/local.jpg'
        )


@override_settings(AWS_STORAGE_BUCKET_NAME='')
class MediaRouterStorageInerteTests(SimpleTestCase):
    def test_bucket_vide_implique_aucun_backend_distant(self):
        self.assertIsNone(MediaRouterStorage().remote)
