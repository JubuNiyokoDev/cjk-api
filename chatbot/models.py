from django.db import models
from django.conf import settings


class ChatbotConversation(models.Model):
    """Conversation avec l'assistant CJK.

    `user` est renseigné quand le visiteur est connecté (historique
    consultable) ; sinon la conversation reste anonyme, rattachée
    uniquement à sa `session_key`.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chatbot_conversations',
        blank=True,
        null=True,
    )
    session_key = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title or f'Conversation {self.pk}'


class ChatbotMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'Utilisateur'),
        ('bot', 'Assistant'),
    ]

    conversation = models.ForeignKey(
        ChatbotConversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.get_role_display()}: {self.content[:50]}'
