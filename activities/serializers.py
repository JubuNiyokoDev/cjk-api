from django.utils.text import slugify
from rest_framework import serializers
from core.serializers import BaseContentImageSerializer
from .models import Activity, ActivityCategory, ActivityImage

class ActivityImageSerializer(BaseContentImageSerializer):
    class Meta(BaseContentImageSerializer.Meta):
        model = ActivityImage

class ActivityCategorySerializer(serializers.ModelSerializer):
    # Le staff saisit un nom : le slug est dérivé automatiquement à la création.
    # Il est ensuite figé (read-only) car c'est lui qui est stocké dans
    # Activity.activity_type — le renommer orphelinerait les activités.
    slug = serializers.SlugField(max_length=50, required=False, read_only=True)

    class Meta:
        model = ActivityCategory
        fields = ['id', 'name', 'slug', 'color', 'order', 'is_active']

    def validate(self, attrs):
        if self.instance is None and attrs.get('name'):
            attrs['slug'] = self._unique_slug(slugify(attrs['name'])[:50])
        return attrs

    def _unique_slug(self, base):
        """Évite la collision d'unicité quand deux noms donnent le même slug."""
        slug, suffix = base or 'categorie', 2
        queryset = ActivityCategory.objects.all()
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        while queryset.filter(slug=slug).exists():
            slug = f'{base[:47]}-{suffix}'
            suffix += 1
        return slug

class ActivitySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    content_type = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    images = ActivityImageSerializer(many=True, read_only=True)
    hashtag_list = serializers.ListField(child=serializers.CharField(), read_only=True)

    class Meta:
        model = Activity
        fields = ['id', 'title', 'description', 'activity_type', 'author', 'author_name', 'image', 'images', 'hashtags', 'hashtag_list', 'external_link', 'date_activite', 'is_published', 'created_at', 'updated_at', 'content_type', 'likes_count', 'comments_count', 'is_liked']
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
    
    def get_content_type(self, obj):
        return 'activity'
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
