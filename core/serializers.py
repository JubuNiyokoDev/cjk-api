from rest_framework import serializers


class BaseContentImageSerializer(serializers.ModelSerializer):
    """Sérialiseur commun des images de galerie (sous-classer avec `Meta.model`)."""

    class Meta:
        fields = ['id', 'image', 'caption', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
