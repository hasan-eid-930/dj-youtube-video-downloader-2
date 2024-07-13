from django.test import TestCase
from django.urls import reverse

class HomeTest(TestCase):
    def test_index_page_exists(self):
        response = self.client.get(reverse('youtube'))
        self.assertEqual(response.status_code, 200)
