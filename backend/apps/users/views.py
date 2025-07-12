from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone

from .models import User, UserVerification
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, UserVerificationSerializer,
    AdminUserVerificationSerializer
)


class UserRegistrationView(APIView):
    """View for user registration."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User registered successfully',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """View for user login."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for user profile."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    """View for updating user profile."""
    
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        # Extract location data from request
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            context={'latitude': latitude, 'longitude': longitude}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Profile updated successfully',
            'user': UserProfileSerializer(self.get_object()).data
        })


class PasswordChangeView(APIView):
    """View for password change."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserVerificationView(generics.CreateAPIView):
    """View for submitting user verification."""
    
    serializer_class = UserVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserVerificationListView(generics.ListAPIView):
    """View for listing user verifications."""
    
    serializer_class = UserVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserVerification.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """View for user logout."""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


# Admin views for verification management
class AdminUserVerificationListView(generics.ListAPIView):
    """Admin view for listing all verifications."""
    
    serializer_class = AdminUserVerificationSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = UserVerification.objects.all().order_by('-created_at')


class AdminUserVerificationUpdateView(generics.UpdateAPIView):
    """Admin view for updating verification status."""
    
    serializer_class = AdminUserVerificationSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = UserVerification.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "verification_id"
    
    def perform_update(self, serializer):
        verification = serializer.save(
            verified_by=self.request.user,
            verified_at=timezone.now()
        )
        
        # Update user verification status
        user = verification.user
        if verification.verification_type == 'email':
            user.email_verified = verification.status == 'approved'
        elif verification.verification_type == 'phone':
            user.phone_verified = verification.status == 'approved'
        user.save() 