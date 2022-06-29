from rest_framework import serializers
from authentication.models import User
from django.utils.encoding import (smart_str, force_bytes, DjangoUnicodeDecodeError)
from django.utils.http import (urlsafe_base64_encode, urlsafe_base64_decode)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from authentication.utils import Util
from dotenv import load_dotenv
import os
import django.contrib.auth.password_validation as validators

load_dotenv()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """ we are writing this bcz we need confirm password """
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'date_of_birth', 'user_name', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only':True}
                       }

    def validate_password(self, data):
        validators.validate_password(password=data)
        return data

    """ validating password and confirm password """
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("password and confirm password doesn't match")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    """ Login Serializer used for Email and Password Serialization """
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']


class SendPasswordResetEmailSerializer(serializers.Serializer):
    """ Reset Password (forgot password) Serializer """
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        """ Validation on email and giving user_id and token through email """
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            """ we are Encoding UID when we get UID from database """

            uid = urlsafe_base64_encode(force_bytes((user.id)))
            token = PasswordResetTokenGenerator().make_token(user)

            """ creating a Link to reset password """

            link = f"{os.environ.get('HOST_LINK')}api/user/reset-password/{uid}/{token}/"
            # instance.request.build_absolute_uri(reverse('password-reset ')),
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


class UserPasswordResetSerializer(serializers.Serializer):
    """ Reset Password Serializer """

    password = serializers.CharField(min_length=4, max_length=255,
    style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(min_length=4, max_length=255,
    style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        """Validate password and password2 and raise error when both are not same and
        raise error when token is not given or expired
        """
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            validators.validate_password(password=password)

            """ uid get the user id """
            uid = self.context.get('uid', '')

            """ token is also passed through context from Views """
            token = self.context.get('token')

            """ checking Password and Password2 (confirm password) are same or not """
            if password != password2:
                raise serializers.ValidationError("Password and Confirm password doesn't match")
            id = smart_str(urlsafe_base64_decode(uid))

            """ Getting user from user id """
            user = User.objects.get(id=id)

            """ Checking that Token is Valid or Not """
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not Valid or Expired')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError:
            """ If any error in token generation or token validation then this Exception will raise error """
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not Valid or Expired')


class UserProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Profile gives field like id, user_name, first_name, last_name, email, profile_picture,
    date_of_birth, about_me """

    class Meta:
        model = User
        fields = ('id', 'user_name', 'first_name', 'last_name', 'email', 'profile_picture', 'date_of_birth', 'about_me')
        extra_kwargs = {
            'id': {'read_only': True},
        }


class UserChangePasswordSerializer(serializers.Serializer):
    """ Change password Serializer """

    old_password = serializers.CharField(max_length=255,
    style={'input_type': 'password'}, write_only=True)
    password = serializers.CharField(max_length=255,
    style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255,
    style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2', 'old_password']

    def validate(self, attrs):
        """ Validating Password And Confirm Password and raise error when both Doesn't match """
        password = attrs.get('password')
        password2 = attrs.get('password2')

        """ Taking Old Password For Validation """
        old_password = attrs.get('old_password')
        user = self.context.get('user')

        """ checking Old password is Correct or Not and if Not then Raise Error """
        if not user.check_password(old_password):
            raise serializers.ValidationError("Incorrect old password")

        """ 
        Validating All Password Condition to Create a New Password 
        It will Take Validate Password check from AUTH_PASSWORD_VALIDATION defined in Setting using
        import django.contrib.auth.password_validation as validator
        
        """
        validators.validate_password(password=password, user=User)

        """ checking Password and Password2 are same or Not """
        if password != password2:
            raise serializers.ValidationError("Password and Confirm password doesn't match")
        user.set_password(password)
        user.save()
        return attrs
