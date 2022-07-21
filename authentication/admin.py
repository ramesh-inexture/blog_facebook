from django.contrib import admin
from authentication.models import RestrictedUsers
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
User = get_user_model()


class UserModelAdmin(BaseUserAdmin):

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserModelAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'email', 'user_name', 'first_name', 'last_name', 'date_of_birth', 'created_at', 'updated_at', 'is_admin', 'is_active')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('user_name', 'first_name', 'last_name', 'date_of_birth', 'profile_picture')}),
        ('Permissions', {'fields': ('is_admin','is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserModelAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_name', 'first_name', 'last_name', 'date_of_birth', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email', 'id')
    filter_horizontal = ()


class RestrictedUsersModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'blocked_user', 'blocked_by', 'created_at', 'updated_at')


# Now here we register the new ModelAdmin...
admin.site.register(User, UserModelAdmin)
admin.site.register(RestrictedUsers, RestrictedUsersModelAdmin)
