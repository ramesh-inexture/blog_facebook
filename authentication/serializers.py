from rest_framework import serializers
from authentication.models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    #we are writing this bcz we need confirm password
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'date_of_birth', 'user_name', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only':True},
        }

    #validating password and confirm password

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("password and confirm password doesn't match")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']