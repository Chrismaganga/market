from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserVerification


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    full_address = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'bio', 'avatar', 'date_of_birth',
            'address', 'city', 'state', 'country', 'postal_code',
            'full_address', 'email_verified', 'phone_verified',
            'is_seller', 'verification_status', 'created_at'
        ]
        read_only_fields = ['id', 'username', 'email_verified', 'phone_verified', 'created_at']
    
    def get_full_address(self, obj):
        return obj.get_full_address()
    
    def get_verification_status(self, obj):
        verifications = obj.verifications.all()
        status = {}
        for verification in verifications:
            status[verification.verification_type] = verification.status
        return status


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'bio',
            'avatar', 'date_of_birth', 'address', 'city',
            'state', 'country', 'postal_code'
        ]
    
    def update(self, instance, validated_data):
        # Handle location update if coordinates are provided
        latitude = self.context.get('latitude')
        longitude = self.context.get('longitude')
        if latitude and longitude:
            instance.set_location(latitude, longitude)
        
        return super().update(instance, validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value


class UserVerificationSerializer(serializers.ModelSerializer):
    """Serializer for user verification."""
    
    class Meta:
        model = UserVerification
        fields = [
            'id', 'verification_type', 'status', 'document',
            'notes', 'verified_at', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'verified_at', 'created_at']


class AdminUserVerificationSerializer(serializers.ModelSerializer):
    """Serializer for admin to update verification status."""
    
    class Meta:
        model = UserVerification
        fields = [
            'id', 'user', 'verification_type', 'status', 'document',
            'notes', 'verified_by', 'verified_at', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'verification_type', 'document', 'created_at'] 