"""Tests de non-régression du routage et des compteurs des activités.

Contexte : /api/activities/ était capté par l'APIRootView du routeur des
catégories (DefaultRouter ajoute une racine sur ^$, et ce routeur est inclus
avant celui des activités, lui aussi sur ^$). Résultat en production :
GET renvoyait {"categories": "..."} au lieu de la liste, et POST tombait sur une
vue en lecture seule (405) — la table activities_activity est restée vide.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APITestCase

from social.models import Comment, Like

from .models import Activity, ActivityCategory


class ActivityRoutingTests(APITestCase):
    """Le préfixe vide du ActivityViewSet ne doit être masqué par rien."""

    @classmethod
    def setUpTestData(cls):
        # La migration 0006_seed_activity_categories a déjà inséré « sport » :
        # on la réutilise au lieu de violer la contrainte d'unicité du slug.
        cls.category, _ = ActivityCategory.objects.get_or_create(
            slug='sport', defaults={'name': 'Sport', 'color': 'orange'}
        )
        cls.staff = get_user_model().objects.create_user(
            username='staff', password='motdepasse-test', is_staff=True
        )

    def test_liste_renvoie_un_tableau_pas_la_racine_du_routeur(self):
        """GET /api/activities/ doit renvoyer la liste, pas {"categories": ...}."""
        Activity.objects.create(
            title='Tournoi de football',
            description='Finale inter-quartiers',
            activity_type='sport',
            author=self.staff,
            date_activite=date(2026, 5, 1),
            is_published=True,
        )

        response = self.client.get('/api/activities/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La régression se manifestait exactement ici : un dict sans 'results'.
        self.assertNotIn(
            'categories',
            response.data,
            "/api/activities/ renvoie l'APIRootView du routeur, pas la liste",
        )
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Tournoi de football')

    def test_staff_peut_creer_une_activite(self):
        """POST /api/activities/ doit créer, pas répondre 405."""
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            '/api/activities/',
            {
                'title': 'Atelier de médiation',
                'description': 'Formation à la résolution de conflits',
                'activity_type': 'sport',
                'date_activite': '2026-06-15',
                'is_published': True,
            },
            format='multipart',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f"creation refusee ({response.status_code}) : {response.data}",
        )
        activity = Activity.objects.get(title='Atelier de médiation')
        self.assertEqual(activity.author, self.staff)
        self.assertTrue(activity.is_published)

    def test_creation_sans_image_acceptee(self):
        """Le formulaire du back-office omet `image` quand aucun fichier n'est choisi."""
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            '/api/activities/',
            {
                'title': 'Sans visuel',
                'description': 'Activité sans image',
                'activity_type': 'sport',
                'date_activite': '2026-07-01',
                'is_published': False,
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertFalse(Activity.objects.get(title='Sans visuel').image)

    def test_anonyme_ne_peut_pas_creer(self):
        response = self.client.post(
            '/api/activities/',
            {
                'title': 'Interdit',
                'description': 'x',
                'activity_type': 'sport',
                'date_activite': '2026-07-01',
            },
            format='multipart',
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        self.assertFalse(Activity.objects.exists())

    def test_les_categories_restent_accessibles(self):
        """Le routeur des catégories doit continuer de passer avant le détail."""
        response = self.client.get('/api/activities/categories/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = [item['slug'] for item in response.data]
        self.assertIn('sport', slugs)

    def test_detail_accessible(self):
        activity = Activity.objects.create(
            title='Detail',
            description='x',
            activity_type='sport',
            author=self.staff,
            date_activite=date(2026, 5, 1),
            is_published=True,
        )

        response = self.client.get(f'/api/activities/{activity.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Detail')

    def test_brouillon_invisible_pour_le_public(self):
        Activity.objects.create(
            title='Brouillon',
            description='x',
            activity_type='sport',
            author=self.staff,
            date_activite=date(2026, 5, 1),
            is_published=False,
        )

        response = self.client.get('/api/activities/')

        self.assertEqual(response.data['count'], 0)


class ActivityCountAnnotationTests(APITestCase):
    """likes_count et comments_count ne doivent pas se multiplier entre eux."""

    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_user(
            username='staff2', password='motdepasse-test', is_staff=True
        )
        cls.activity = Activity.objects.create(
            title='Avec interactions',
            description='x',
            activity_type='sport',
            author=cls.staff,
            date_activite=date(2026, 5, 1),
            is_published=True,
        )

        content_type = ContentType.objects.get_for_model(Activity)
        users = [
            get_user_model().objects.create_user(
                username=f'u{index}', password='motdepasse-test'
            )
            for index in range(4)
        ]
        # 3 likes et 4 commentaires : sans distinct=True, les deux Count
        # remontent 12 au lieu de 3 et 4.
        for user in users[:3]:
            Like.objects.create(
                user=user, content_type=content_type, object_id=cls.activity.id
            )
        for user in users:
            Comment.objects.create(
                user=user,
                content_type=content_type,
                object_id=cls.activity.id,
                text='Bravo',
            )

    def test_compteurs_non_multiplies(self):
        response = self.client.get('/api/activities/')

        item = response.data['results'][0]
        self.assertEqual(item['likes_count'], 3)
        self.assertEqual(item['comments_count'], 4)
