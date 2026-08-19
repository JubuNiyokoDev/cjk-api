from django.db import models


class Partner(models.Model):
    """Partenaire du CJK (bailleur, ONG, institution…)."""
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')
    logo = models.ImageField(upload_to='organization/partners/', blank=True, null=True)
    website = models.URLField(max_length=500, blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class CoreValue(models.Model):
    """Valeur fondamentale du CJK (Vérité, Tolérance…)."""
    ICON_CHOICES = [
        ('shield', 'Bouclier'),
        ('message-circle', 'Bulle de dialogue'),
        ('scale', 'Balance'),
        ('check-circle', 'Coche'),
        ('ear', 'Oreille'),
        ('users', 'Personnes'),
        ('heart', 'Coeur'),
        ('star', 'Étoile'),
        ('handshake', 'Poignée de main'),
        ('globe', 'Globe'),
        ('sun', 'Soleil'),
        ('book-open', 'Livre'),
    ]
    COLOR_CHOICES = [
        ('blue', 'Bleu'),
        ('green', 'Vert'),
        ('orange', 'Orange'),
        ('purple', 'Violet'),
        ('yellow', 'Jaune'),
        ('cyan', 'Cyan'),
        ('red', 'Rouge'),
        ('pink', 'Rose'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default='star')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='orange')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """Membre de l'équipe affiché sur la page « Notre équipe »."""
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    photo = models.ImageField(upload_to='organization/team/', blank=True, null=True)
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} — {self.role}'


class Award(models.Model):
    """Distinction / prix reçu par le CJK."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    year = models.CharField(max_length=10, blank=True, default='')
    icon = models.CharField(max_length=30, choices=CoreValue.ICON_CHOICES, default='star')
    color = models.CharField(max_length=20, choices=CoreValue.COLOR_CHOICES, default='orange')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
