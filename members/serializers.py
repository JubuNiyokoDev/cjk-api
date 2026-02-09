from rest_framework import serializers
from .models import Member

class MemberSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Member
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'quartier', 'date_naissance', 'photo', 'date_inscription', 'is_staff', 'is_superuser', 'is_active_member']
        read_only_fields = ['id', 'date_inscription', 'is_staff', 'is_superuser']

class MemberRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Member
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'quartier', 'date_naissance']
    
    def create(self, validated_data):
        member = Member.objects.create_user(**validated_data)
        return member
