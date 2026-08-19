from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
from .models import Member
from .serializers import (
    MemberSerializer,
    MemberRegistrationSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)

class IsSelfOrAdmin(BasePermission):
    """Un membre peut modifier son propre profil ; l'admin peut tout."""

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or obj.pk == request.user.pk)
        )

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.filter(is_active_member=True)
    serializer_class = MemberSerializer

    def get_permissions(self):
        if self.action in ['create', 'password_reset', 'password_reset_confirm']:
            return [AllowAny()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsSelfOrAdmin()]
        elif self.action == 'destroy':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return MemberRegistrationSerializer
        return MemberSerializer

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Profil de l'utilisateur connecté (lecture et mise à jour)."""
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Changement de mot de passe de l'utilisateur connecté."""
        serializer = PasswordChangeSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        return Response({'detail': 'Mot de passe modifié avec succès.'})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def password_reset(self, request):
        """Envoie un email avec un lien de réinitialisation de mot de passe.

        Répond toujours 200, même si l'email est inconnu, pour ne pas
        révéler quels emails sont enregistrés (anti-énumération).
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        member = Member.objects.filter(email__iexact=email, is_active=True).first()
        if member and member.email:
            uid = urlsafe_base64_encode(force_bytes(member.pk))
            token = default_token_generator.make_token(member)
            reset_url = f'{settings.FRONTEND_SITE_URL}/auth/reset-password?uid={uid}&token={token}'
            send_mail(
                subject='Réinitialisation de votre mot de passe — Centre Jeunes Kamenge',
                message=(
                    f'Bonjour {member.first_name or member.username},\n\n'
                    'Vous avez demandé la réinitialisation de votre mot de passe '
                    'sur le site du Centre Jeunes Kamenge.\n\n'
                    f'Cliquez sur ce lien pour choisir un nouveau mot de passe :\n{reset_url}\n\n'
                    'Ce lien est valable pendant 24 heures. Si vous n\'êtes pas à '
                    'l\'origine de cette demande, ignorez simplement cet email.\n\n'
                    'L\'équipe du Centre Jeunes Kamenge'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member.email],
                fail_silently=False,
            )
        return Response({
            'detail': 'Si cet email correspond à un compte, un lien de réinitialisation a été envoyé.'
        })

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def password_reset_confirm(self, request):
        """Valide le lien de réinitialisation et définit le nouveau mot de passe."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            member_pk = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            member = Member.objects.get(pk=member_pk, is_active=True)
        except (ValueError, OverflowError, Member.DoesNotExist):
            member = None

        if member is None or not default_token_generator.check_token(
            member, serializer.validated_data['token']
        ):
            return Response(
                {'detail': 'Lien invalide ou expiré. Refaites une demande de réinitialisation.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member.set_password(serializer.validated_data['new_password'])
        member.save(update_fields=['password'])
        return Response({'detail': 'Mot de passe réinitialisé avec succès. Vous pouvez vous connecter.'})
