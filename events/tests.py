import os

import django
import pytest
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.test import Client
from events.models import EventConnection
os.environ['DJANGO_SETTINGS_MODULE'] = 'webflow.settings'
django.setup()


@pytest.fixture
def client():
    return Client()

@pytest.fixture
def retry_url():
    return reverse('retry_event_connection', kwargs={'event_connection_id': 1})  # Adjust the URL if necessary


class TestRetryEventConnectionView:
    @patch('events.views.update_event_connection_retry_count')
    @patch('events.views.get_event_connection_by_id')
    @patch('events.views.producer')
    def test_retry_event_connection_success(self, mock_producer, mock_get_event_connection_by_id,
                                            mock_update_event_connection_retry_count, client, retry_url):
        mock_event_connection_dto = MagicMock()
        mock_event_connection_dto.get.return_value = 'test_account_id'
        mock_get_event_connection_by_id.return_value = mock_event_connection_dto
        response = client.post(retry_url, content_type='application/json')
        assert response.status_code == 200
        assert 'Event Connection retried successfully' in response.json()['message']

    def test_retry_event_connection_missing_id(self, client):
        url = reverse('retry_event_connection', kwargs={'event_connection_id': ''})
        response = client.post(url, content_type='application/json')
        assert response.status_code == 400
        assert 'Missing event_connection_id' in response.json()['message']

    @patch('events.views.get_event_connection_by_id', side_effect=EventConnection.DoesNotExist)
    def test_retry_event_connection_not_found(self, mock_get_event_connection_by_id, client, retry_url):
        response = client.post(retry_url, content_type='application/json')
        assert response.status_code == 404
        assert 'Event connection not found' in response.json()['message']

    def test_retry_event_connection_invalid_method(self, client, retry_url):
        response = client.get(retry_url)
        assert response.status_code == 405
        assert 'Invalid request method' in response.json()['message']