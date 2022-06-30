from django.urls import path
from .views import SeeNotificationsView

urlpatterns = [
    path('', SeeNotificationsView.as_view(), name='create-post'),

]
