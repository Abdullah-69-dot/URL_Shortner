from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from urls_app.models import URL
from urls_app.utils import get_unique_short_code
from core.consistent_hash import hash_ring

class URLAPITests(APITestCase):
    databases = {'default', 'shard_1', 'shard_2', 'shard_3'}
    """
    Comprehensive tests for the URL Shortener API.
    Note: These tests run against the default 'test_default' DB.
    Since we are testing API logic, we mock the sharding behavior 
    or rely on the default DB routing for unit tests.
    """

    def setUp(self):
        self.url_data = {"url": "https://www.google.com"}
        self.short_code = "test12"
        # Determine the correct shard and save there
        shard = hash_ring.get_node(self.short_code)
        self.url_obj = URL.objects.using(shard).create(
            url=self.url_data['url'], 
            short_code=self.short_code
        )

    def test_shorten_url(self):
        """Test creating a shortened URL."""
        response = self.client.post(reverse('url-shorten'), self.url_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('shortCode', response.data)
        self.assertEqual(response.data['url'], self.url_data['url'])

    def test_get_url(self):
        """Test retrieving a URL by short code."""
        response = self.client.get(reverse('url-detail', args=[self.short_code]))
        # Note: If the shard router is active, it might try to query shard_X.
        # In tests, we usually mock the router or ensure shards are aliased to the test DB.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['url'], self.url_data['url'])
        self.assertNotIn('accessCount', response.data)

    def test_get_url_not_found(self):
        """Test 404 for non-existent short code."""
        response = self.client.get(reverse('url-detail', args=['nonexistent']))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_url_stats(self):
        """Test the stats endpoint."""
        response = self.client.get(reverse('url-stats', args=[self.short_code]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessCount', response.data)

    def test_update_url(self):
        """Test updating a URL."""
        updated_data = {"url": "https://www.bing.com"}
        response = self.client.put(reverse('url-detail', args=[self.short_code]), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['url'], updated_data['url'])

    def test_delete_url(self):
        """Test deleting a URL."""
        response = self.client.delete(reverse('url-detail', args=[self.short_code]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class URLModelTests(APITestCase):
    databases = {'default', 'shard_1', 'shard_2', 'shard_3'}
    def test_short_code_uniqueness(self):
        """Verify that short codes generated are unique."""
        code1 = get_unique_short_code()
        URL.objects.create(url="https://test1.com", short_code=code1)
        code2 = get_unique_short_code()
        self.assertNotEqual(code1, code2)
