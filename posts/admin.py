from django.contrib import admin
from .models import *

admin.site.register(Posts)
admin.site.register(UploadedFiles)
admin.site.register(PostCategories)
admin.site.register(Likes)
admin.site.register(Comments)
