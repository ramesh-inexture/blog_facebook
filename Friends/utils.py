from .models import Friends


def check_is_friend(user_id_1, user_id_2):
    """
    This is A Method to find that the two users user_id_1 and user_id_2 are friends,
    or user_id_1 have sent any Friend request to user_id_2,
    or user_id_1 have any Pending Friend request from user_id_2 from Friends Table
    it will return friend status and sender_id (who have sent Friend Request) if Data is Available in Friends Table,
    or It will Return None
    """
    query1 = Friends.objects.filter(sender_id_id=user_id_1, receiver_id_id=user_id_2).first()
    query2 = Friends.objects.filter(sender_id_id=user_id_2, receiver_id_id=user_id_1).first()

    if query1 is not None:
        """ checking condition For query1 """
        return query1.is_friend, query1.sender_id_id
    elif query2 is not None:
        """ checking condition For query2 """
        return query2.is_friend, query2.sender_id_id
    else:
        """ if Data Not Available then it will return None"""
        return None




