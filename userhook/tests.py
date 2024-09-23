from django.test import Client
from django.urls import reverse


class TestStatusAPI:

    def setup_method(self):
        self.client = Client()
        self.url = reverse('status')  # Ensure this matches your URL pattern

    def test_status_success(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.json() == {'status': 'success', 'message': 'Userhook is running'}

    def test_status_invalid_method(self):
        response = self.client.post(self.url)
        assert response.status_code == 405
        assert response.json() == {'status': 'error', 'message': 'Invalid request method'}