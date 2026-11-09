"""Audit du stockage des médias : où chaque fichier référencé en base est servi.

Parcourt tous les FileField/ImageField de tous les modèles et classe chaque
fichier référencé :

  disque   le fichier est dans MEDIA_ROOT -> servi sous https://api.cjkamenge.com/media/...
  s3       absent du disque, présent sur S3 -> servi sous le domaine CDN
  MANQUANT référencé en base mais introuvable des deux côtés (lien mort)

Usage :
    python manage.py media_audit
    python manage.py media_audit --urls      # affiche l'URL resolue de chaque fichier
"""

from django.apps import apps
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    help = "Indique, pour chaque media reference en base, s'il est servi depuis le disque ou depuis S3."

    def add_arguments(self, parser):
        parser.add_argument(
            '--urls',
            action='store_true',
            help="Affiche l'URL resolue de chaque fichier.",
        )

    def handle(self, *args, **options):
        show_urls = options['urls']
        storage = default_storage

        remote = getattr(storage, 'remote', None)
        legacy = getattr(storage, 'legacy', None)
        if legacy is None:
            self.stdout.write(
                self.style.WARNING(
                    "Le stockage par defaut n'est pas MediaRouterStorage : "
                    'audit limite.'
                )
            )
            return

        if remote is None:
            self.stdout.write(
                self.style.WARNING(
                    'S3 non configure (AWS_STORAGE_BUCKET_NAME vide) : '
                    'tous les medias, anciens comme nouveaux, sont sur le disque.'
                )
            )

        counts = {'disque': 0, 's3': 0, 'MANQUANT': 0}
        missing = []

        for model in apps.get_models():
            file_fields = [
                field
                for field in model._meta.get_fields()
                if isinstance(field, models.FileField)
            ]
            if not file_fields:
                continue

            names = [field.name for field in file_fields]
            rows = model._default_manager.all().only('pk', *names)

            for row in rows.iterator():
                for field_name in names:
                    file_obj = getattr(row, field_name, None)
                    if not file_obj or not file_obj.name:
                        continue

                    name = file_obj.name
                    if legacy.exists(name):
                        where = 'disque'
                    elif remote is not None and remote.exists(name):
                        where = 's3'
                    else:
                        where = 'MANQUANT'
                        missing.append(f'{model._meta.label}#{row.pk}.{field_name} -> {name}')

                    counts[where] += 1

                    if show_urls:
                        try:
                            url = storage.url(name)
                        except Exception as exc:  # noqa: BLE001
                            url = f'<erreur: {exc}>'
                        self.stdout.write(f'  [{where:8}] {name}\n             {url}')

        self.stdout.write('')
        self.stdout.write(f"  sur le disque (URL /media/ inchangee) : {counts['disque']}")
        self.stdout.write(f"  sur S3 (URL CDN)                      : {counts['s3']}")
        if counts['MANQUANT']:
            self.stdout.write(
                self.style.ERROR(f"  INTROUVABLES (liens morts)            : {counts['MANQUANT']}")
            )
            for item in missing:
                self.stdout.write(self.style.ERROR(f'    {item}'))
        else:
            self.stdout.write('  introuvables                          : 0')
