# CJK API - Backend Django REST

API REST pour le Centre Jeunes Kamenge (CJK)

## Architecture du projet

### Partie INTERNE (Staff/Agents CJK)
- **News** : Actualités internes du centre (authentification requise)
- **Activités** : Gestion des activités du centre (authentification requise)
- Seuls les staff peuvent créer/modifier

### Partie PUBLIQUE (Jeunes membres)
- **Blog** : Articles avec interactions sociales
- **Likes** : Liker les articles
- **Comments** : Commenter les articles
- **Chat** : Messagerie entre jeunes membres
- Espace communautaire type Facebook

## Fonctionnalités

- **Blog** : Articles de blog pour les jeunes avec likes et comments
- **News** : Actualités internes du centre (staff uniquement)
- **Activités** : Gestion des activités (sport, culture, formation, paix)
- **Membres** : Système d'inscription et authentification des membres
- **Social** : Likes, Comments, Chat entre membres

## Installation

1. Créer l'environnement virtuel :
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Modifier .env selon vos besoins
```

4. Appliquer les migrations :
```bash
python manage.py migrate
```

5. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

6. Lancer le serveur :
```bash
python manage.py runserver
```

## Endpoints API

### Authentification
- `POST /api/auth/token/` - Obtenir un token JWT
- `POST /api/auth/token/refresh/` - Rafraîchir le token

### Membres
- `GET /api/members/` - Liste des membres
- `POST /api/members/` - Inscription d'un nouveau membre
- `GET /api/members/me/` - Profil du membre connecté
- `GET /api/members/{id}/` - Détails d'un membre
- `PUT /api/members/{id}/` - Modifier un membre
- `DELETE /api/members/{id}/` - Supprimer un membre

### Blog
- `GET /api/blog/posts/` - Liste des articles
- `POST /api/blog/posts/` - Créer un article (authentifié)
- `GET /api/blog/posts/{id}/` - Détails d'un article
- `GET /api/blog/posts/{id}/comments/` - Commentaires d'un article
- `PUT /api/blog/posts/{id}/` - Modifier un article
- `DELETE /api/blog/posts/{id}/` - Supprimer un article
- `GET /api/blog/categories/` - Liste des catégories

### Social (Interactions)
- `POST /api/social/likes/toggle/` - Liker/Unliker un contenu
- `GET /api/social/comments/?content_type=X&object_id=Y` - Liste des commentaires
- `POST /api/social/comments/` - Créer un commentaire
- `PUT /api/social/comments/{id}/` - Modifier un commentaire
- `DELETE /api/social/comments/{id}/` - Supprimer un commentaire

### Chat
- `GET /api/social/chat/rooms/` - Liste des conversations
- `POST /api/social/chat/rooms/` - Créer une conversation
- `GET /api/social/chat/rooms/{id}/messages/` - Messages d'une conversation
- `POST /api/social/chat/rooms/{id}/send_message/` - Envoyer un message
- `POST /api/social/chat/rooms/{id}/mark_read/` - Marquer comme lu

### News (Staff uniquement)
- `GET /api/news/` - Liste des actualités (authentifié)
- `POST /api/news/` - Créer une actualité (staff)
- `GET /api/news/{id}/` - Détails d'une actualité
- `PUT /api/news/{id}/` - Modifier une actualité (staff)
- `DELETE /api/news/{id}/` - Supprimer une actualité (staff)

### Activités (Staff uniquement)
- `GET /api/activities/` - Liste des activités (authentifié)
- `POST /api/activities/` - Créer une activité (staff)
- `GET /api/activities/{id}/` - Détails d'une activité
- `PUT /api/activities/{id}/` - Modifier une activité (staff)
- `DELETE /api/activities/{id}/` - Supprimer une activité (staff)

## Filtres disponibles

- Blog : `?category=1&is_published=true`
- News : `?is_published=true`
- Activités : `?activity_type=sport&is_published=true`

## Types d'activités

- `sport` - Sport
- `culture` - Culture
- `formation` - Formation
- `paix` - Paix et Réconciliation
- `autre` - Autre

## Administration

Accéder à l'interface d'administration Django : `http://localhost:8000/admin/`
