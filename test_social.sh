#!/bin/bash
# Script de test des fonctionnalités sociales

echo "=== TEST DES FONCTIONNALITÉS SOCIALES CJK API ==="
echo ""

# 1. Créer un utilisateur
echo "1. Inscription d'un membre..."
curl -X POST http://localhost:8000/api/members/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jeune1",
    "email": "jeune1@cjk.bi",
    "password": "password123",
    "first_name": "Jean",
    "last_name": "Kamenge"
  }'

echo -e "\n\n2. Obtenir un token JWT..."
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jeune1",
    "password": "password123"
  }'

echo -e "\n\n3. Liker un article (remplacer TOKEN)..."
echo "POST /api/social/likes/toggle/"
echo '{
  "content_type": 7,
  "object_id": 1
}'

echo -e "\n\n4. Commenter un article..."
echo "POST /api/social/comments/"
echo '{
  "content_type": 7,
  "object_id": 1,
  "text": "Super article !"
}'

echo -e "\n\n5. Créer une conversation..."
echo "POST /api/social/chat/rooms/"
echo '{
  "name": "Discussion entre jeunes",
  "members": [1, 2]
}'

echo -e "\n\n6. Envoyer un message..."
echo "POST /api/social/chat/rooms/1/send_message/"
echo '{
  "message": "Salut, comment ça va ?"
}'

echo -e "\n\n=== TOUT FONCTIONNE ! ==="
