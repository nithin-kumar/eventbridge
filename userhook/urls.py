from django.urls import path

from . import views
from .views import  status

urlpatterns = [
    path('status/', status, name='status'),
]
