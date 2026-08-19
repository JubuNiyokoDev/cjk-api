from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Member

class MemberSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'quartier', 'date_naissance', 'photo', 'date_inscription', 'is_staff', 'is_superuser', 'is_active_member']
        # username et is_active_member ne sont pas modifiables par le membre
        # lui-même (l'admin gère ces champs via le back-office Django).
        read_only_fields = ['id', 'username', 'date_inscription', 'is_staff', 'is_superuser', 'is_active_member']

class MemberRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Member
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'quartier', 'date_naissance']
    
    def create(self, validated_data):
        member = Member.objects.create_user(**validated_data)
        return member

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Mot de passe actuel incorrect.')
        return value

    def validate_new_password(self, value):
        validate_password(value, user=self.context['request'].user)
        return value
