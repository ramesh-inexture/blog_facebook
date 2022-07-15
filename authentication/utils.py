from django.core.mail import EmailMessage
import os
from Friends.models import Friends
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """ Generate Token """

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class Util:
    """ Send Mail through this Util function"""
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=os.environ.get('EMAIL_FROM'),
            to=[data['to_email']]
        )
        email.send()


def get_friend_object(user_id, friend_id):
    user_sender_obj = Friends.objects.filter(sender_id_id=user_id, receiver_id_id=friend_id).first()
    user_receiver_obj = Friends.objects.filter(sender_id_id=friend_id, receiver_id_id=user_id).first()

    if user_sender_obj:
        """ checking condition For user_sender_obj """
        return user_sender_obj
    elif user_receiver_obj:
        """ checking condition For user_receiver_obj """
        return user_receiver_obj
    else:
        """ if Data Not Available then it will return None"""
        return None
