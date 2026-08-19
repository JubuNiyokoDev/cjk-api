from django.db import migrations

# Catégories historiquement codées en dur dans Activity.ACTIVITY_TYPES.
# Les couleurs reprennent les dégradés déjà utilisés côté site public.
SEED_CATEGORIES = [
    ('sport', 'Sport', 'emerald', 1),
    ('culture', 'Culture', 'orange', 2),
    ('formation', 'Formation', 'blue', 3),
    ('paix', 'Paix & Réconciliation', 'red', 4),
    ('autre', 'Autre', 'slate', 5),
]


def create_categories(apps, schema_editor):
    """Crée les catégories existantes + toute valeur déjà utilisée en base."""
    ActivityCategory = apps.get_model('activities', 'ActivityCategory')
    Activity = apps.get_model('activities', 'Activity')

    for slug, name, color, order in SEED_CATEGORIES:
        ActivityCategory.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'color': color, 'order': order},
        )

    # Filet de sécurité : une activité dont le type ne correspond à aucune
    # catégorie connue garde une catégorie visible dans le back-office.
    known = set(ActivityCategory.objects.values_list('slug', flat=True))
    used = set(Activity.objects.values_list('activity_type', flat=True))
    for index, slug in enumerate(sorted(used - known - {''}), start=len(SEED_CATEGORIES) + 1):
        ActivityCategory.objects.create(
            slug=slug,
            name=slug.replace('-', ' ').replace('_', ' ').capitalize(),
            color='slate',
            order=index,
        )


def remove_categories(apps, schema_editor):
    ActivityCategory = apps.get_model('activities', 'ActivityCategory')
    ActivityCategory.objects.filter(slug__in=[s for s, _, _, _ in SEED_CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0005_activitycategory_alter_activity_activity_type'),
    ]

    operations = [
        migrations.RunPython(create_categories, remove_categories),
    ]
