from rest_framework import serializers
from .models import BlogPost, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'author', 'author_name', 'category', 'category_name', 'content', 'image', 'is_published', 'created_at', 'updated_at', 'likes_count', 'comments_count', 'is_liked', 'content_type']
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
    
    def get_content_type(self, obj):
        return 'blogpost'
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
