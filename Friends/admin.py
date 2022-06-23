from django.contrib import admin
from .models import *


class FriendAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_id', 'receiver_id', 'is_friend', 'is_blocked', 'created_on', 'updated_on')


admin.site.register(Friends, FriendAdmin)
