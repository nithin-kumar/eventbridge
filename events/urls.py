from django.urls import path

from events.views import handle_event, retry_event_connection

urlpatterns = [
    path('<str:id>/', handle_event, name='handle_event'),
    path('event_connection/<str:event_connection_id>/retry', retry_event_connection, name='retry_event_connection'),
]
