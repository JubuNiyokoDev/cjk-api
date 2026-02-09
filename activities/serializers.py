from rest_framework import serializers
from .models import Activity

class ActivitySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = Activity
        fields = ['id', 'title', 'description', 'activity_type', 'author', 'author_name', 'image', 'date_activite', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
