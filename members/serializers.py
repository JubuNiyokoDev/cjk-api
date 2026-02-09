from rest_framework import serializers
from .models import Member

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'quartier', 'date_naissance', 'photo', 'date_inscription']
        read_only_fields = ['id', 'date_inscription']

class MemberRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Member
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'quartier', 'date_naissance']
    
    def create(self, validated_data):
        member = Member.objects.create_user(**validated_data)
        return member
