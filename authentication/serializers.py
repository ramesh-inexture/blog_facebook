from rest_framework import serializers
from authentication.models import User
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from authentication.utils import Util


#Registration Serializer
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


#Login Serializer
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']


#Reset Password (forgot password) Serializer
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # we are Encoding UID when we get UID from database
            uid = urlsafe_base64_encode(force_bytes((user.id)))
            print('Encoded UID', uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print('Token',token)
            #creating a Link to reset password
            link = 'http://localhost:3000/api/user/reset/'+uid+'/'+token
            print('password reset link', link)
            #Send Email
            body = f'Click Following Link to Reset your Password {link}'
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError('You are not a Registered User')


#Reset Password Serializer
class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=4, max_length=255,
    style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(min_length=4, max_length=255,
    style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Password and Confirm password doesn't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not Valid or Expired')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not Valid or Expired')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile """

    class Meta:
        model = User
        fields = ('id', 'user_name', 'first_name', 'last_name', 'email', 'profile_picture', 'date_of_birth', 'about_me')
        extra_kwargs = {
            'id': {'read_only': True},

        }


# class UpdateProfileSerializer(serializers.ModelSerializer):
#     # email = serializers.EmailField(required=True)
#
#     class Meta:
#         model = User
#         fields = ('id', 'user_name', 'first_name', 'last_name', 'email', 'profile_picture', 'date_of_birth', 'about_me')

    # def update(self, instance, validated_data):
    #     user = self.context.get('user')
    #
    #     if user.pk != instance.pk:
    #         raise serializers.ValidationError({"authorize": "You dont have permission for this user."})
    #
    #     instance.first_name = validated_data['first_name']
    #     instance.last_name = validated_data['last_name']
    #     instance.email = validated_data['email']
    #     instance.username = validated_data['username']
    #
    #     instance.save()
    #
    #     return instance


''' Change password Serializer'''
class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=4, max_length=255,
    style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(min_length=4, max_length=255,
    style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm password doesn't match")
        user.set_password(password)
        user.save()
        return attrs
