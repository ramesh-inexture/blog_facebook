from .models import Friends


def check_is_friend(user_id_1, user_id_2):
    """This is A Method to find that the two users user_id_1 and user_id_2 are friends,
    or user_id_1 have sent any Friend request to user_id_2,
    or user_id_1 have any Pending Friend request from user_id_2 from Friends Table
    it will return friend status and sender_id (who have sent Friend Request) if Data is Available in Friends Table,
    or It will Return None
    """
    user_sender_obj = Friends.objects.filter(sender_id_id=user_id_1, receiver_id_id=user_id_2).first()
    user_receiver_obj = Friends.objects.filter(sender_id_id=user_id_2, receiver_id_id=user_id_1).first()

    if user_sender_obj:
        """ checking condition For user_sender_obj """
        return user_sender_obj.is_friend, user_sender_obj.sender_id_id
    elif user_receiver_obj:
        """ checking condition For user_receiver_obj """
        return user_receiver_obj.is_friend, user_receiver_obj.sender_id_id
    else:
        """ if Data Not Available then it will return None"""
        return None
