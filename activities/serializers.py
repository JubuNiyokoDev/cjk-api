from rest_framework import serializers
from core.serializers import BaseContentImageSerializer
from .models import Activity, ActivityImage

class ActivityImageSerializer(BaseContentImageSerializer):
    class Meta(BaseContentImageSerializer.Meta):
        model = ActivityImage

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
