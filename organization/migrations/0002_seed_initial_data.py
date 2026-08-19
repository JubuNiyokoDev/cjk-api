# Data migration : pré-remplit les partenaires, valeurs, équipe et
# distinctions avec le contenu actuellement affiché sur le site, afin
# que la bascule vers des sections dynamiques soit transparente.
from django.db import migrations

PARTNERS = [
    {'name': 'MISEREOR', 'country': 'Allemagne', 'order': 1},
    {'name': 'Manos Unidas', 'country': 'Espagne', 'order': 2},
    {'name': 'Fondazione Peppino Vismara', 'country': 'Italie', 'order': 3},
    {'name': 'Caritas Italiana', 'country': 'Italie', 'order': 4},
]

VALUES = [
    {'name': 'Vérité', 'description': "Nous prônons l'honnêteté et la transparence dans toutes nos actions", 'icon': 'shield', 'color': 'blue', 'order': 1},
    {'name': 'Tolérance', 'description': "Nous accueillons tous les jeunes sans distinction d'ethnie, de religion ou d'origine", 'icon': 'message-circle', 'color': 'green', 'order': 2},
    {'name': 'Justice sociale', 'description': "Nous œuvrons pour l'égalité des chances et la dignité de chaque jeune", 'icon': 'scale', 'color': 'orange', 'order': 3},
    {'name': 'Intégrité', 'description': 'Nous agissons avec droiture et cohérence entre nos paroles et nos actes', 'icon': 'check-circle', 'color': 'purple', 'order': 4},
    {'name': 'Écoute', 'description': 'Nous accordons une attention sincère aux besoins et aux idées des jeunes', 'icon': 'ear', 'color': 'yellow', 'order': 5},
    {'name': 'Respect', 'description': 'Nous cultivons le respect mutuel comme fondement du vivre-ensemble', 'icon': 'users', 'color': 'cyan', 'order': 6},
]

TEAM = [
    {'name': 'Jean-Baptiste NDAYIZEYE', 'role': 'Directeur du centre', 'description': "Coordonne l'ensemble des activités et assure la vision stratégique du CJK", 'email': 'director@cjk.bi', 'phone': '+257 XX XX XX XX', 'order': 1},
    {'name': 'Marie NIYONKURU', 'role': 'Coordinatrice jeunesse', 'description': 'Encadre les programmes de formation et accompagne les jeunes membres', 'email': 'coordinator@cjk.bi', 'phone': '+257 XX XX XX XX', 'order': 2},
    {'name': 'Pierre HAKIZIMANA', 'role': 'Responsable activités sportives', 'description': 'Organise et supervise les activités sportives et les compétitions', 'email': 'sports@cjk.bi', 'phone': '+257 XX XX XX XX', 'order': 3},
    {'name': 'Claudine UWIMANA', 'role': 'Responsable activités culturelles', 'description': 'Développe les programmes culturels et artistiques du centre', 'email': 'culture@cjk.bi', 'phone': '+257 XX XX XX XX', 'order': 4},
    {'name': 'Emmanuel NKURUNZIZA', 'role': 'Formateur principal', 'description': 'Anime les sessions de formation et développe les contenus pédagogiques', 'email': 'formation@cjk.bi', 'phone': '+257 XX XX XX XX', 'order': 5},
    {'name': 'Sylvie IRAKOZE', 'role': 'Responsable administrative', 'description': 'Gère les aspects administratifs et financiers du centre', 'email': 'admin@cjk.bi', 'phone': '+257 XX XX XX XX', 'order': 6},
]

AWARDS = [
    {'name': 'Prix Bonaventure de la Paix', 'description': 'Reconnaissance de notre engagement pour la paix et la réconciliation au Burundi', 'year': '', 'icon': 'star', 'color': 'yellow', 'order': 1},
    {'name': 'Prix Right Livelihood', 'description': 'Le « Nobel Alternatif » décerné pour notre travail exemplaire auprès de la jeunesse', 'year': '2000', 'icon': 'globe', 'color': 'blue', 'order': 2},
    {'name': 'Prix Takunda', 'description': 'Distinction reçue pour notre contribution au développement communautaire', 'year': '2010', 'icon': 'sun', 'color': 'green', 'order': 3},
]


def seed(apps, schema_editor):
    Partner = apps.get_model('organization', 'Partner')
    CoreValue = apps.get_model('organization', 'CoreValue')
    TeamMember = apps.get_model('organization', 'TeamMember')
    Award = apps.get_model('organization', 'Award')

    # Ne rien écraser si l'admin a déjà saisi des données.
    if not Partner.objects.exists():
        Partner.objects.bulk_create(Partner(**data) for data in PARTNERS)
    if not CoreValue.objects.exists():
        CoreValue.objects.bulk_create(CoreValue(**data) for data in VALUES)
    if not TeamMember.objects.exists():
        TeamMember.objects.bulk_create(TeamMember(**data) for data in TEAM)
    if not Award.objects.exists():
        Award.objects.bulk_create(Award(**data) for data in AWARDS)


def unseed(apps, schema_editor):
    # Suppression volontairement non destructive : on ne retire que les
    # entrées seedées identifiables par leur nom.
    Partner = apps.get_model('organization', 'Partner')
    CoreValue = apps.get_model('organization', 'CoreValue')
    TeamMember = apps.get_model('organization', 'TeamMember')
    Award = apps.get_model('organization', 'Award')
    Partner.objects.filter(name__in=[p['name'] for p in PARTNERS]).delete()
    CoreValue.objects.filter(name__in=[v['name'] for v in VALUES]).delete()
    TeamMember.objects.filter(name__in=[t['name'] for t in TEAM]).delete()
    Award.objects.filter(name__in=[a['name'] for a in AWARDS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
