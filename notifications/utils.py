from authentication.utils import Util
from .serializers import NotificationSerializer


def send_notification(**kwargs):
    """ This util send_notification Function is used to send notification through email
    it will take kwargs when it is called and then serialize them and save that notification in Notification table
    and also send notification through email to notified user"""

    notified_user = kwargs['notified_user']
    notified_by = kwargs['notified_by']
    user_name = kwargs['user_name']
    notification_receiver_email = kwargs['notification_receiver_email']
    header_message = kwargs['header_message']
    body_message = kwargs['body_message']

    notification_data = {'notified_user': notified_user, 'notified_by': notified_by, 'header': header_message,
                         'body': body_message.format(user_name)}
    data = {
        'subject': header_message,
        'body': body_message.format(user_name),
        'to_email': notification_receiver_email
    }
    notification_serializer = NotificationSerializer(data=notification_data)
    """ if serialized data is_valid then it will send the email and save in notification table and also this function
    returns True true if not valid then return False and Error"""
    if notification_serializer.is_valid():
        notification_serializer.save()
        """ After Saving Data on notification Table we Will Notify User Through Email"""
        Util.send_email(data)
        return True, True
    else:
        return False, notification_serializer.errors
