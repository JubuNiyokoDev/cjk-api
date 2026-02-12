from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    content_type = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'author', 'author_name', 'image', 'is_published', 'created_at', 'updated_at', 'content_type', 'likes_count', 'comments_count', 'is_liked']
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
    
    def get_content_type(self, obj):
        return 'news'
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
