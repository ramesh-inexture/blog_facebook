from django.contrib import admin
from .models import *


class PostsAdmin(admin.ModelAdmin):
    list_display = ('id', 'posted_by', 'title', 'is_public', 'category_id', 'created_on', 'updated_on')


admin.site.register(Posts, PostsAdmin)
admin.site.register(UploadedFiles)
admin.site.register(PostCategories)
admin.site.register(Likes)
admin.site.register(Comments)
