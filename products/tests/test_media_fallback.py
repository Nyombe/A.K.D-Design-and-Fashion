from django.test import TestCase, Client

class MediaFallbackTests(TestCase):
    def test_media_fallback_redirects_for_missing_file(self):
        client = Client()
        # Request a non-existent shoe image file
        response = client.get('/media/products/some_non_existent_shoe.jpg')
        # It should redirect (302) to the Unsplash shoe placeholder
        self.assertEqual(response.status_code, 302)
        self.assertIn('unsplash.com', response['Location'])
        self.assertIn('photo-1549298916-b41d501d3772', response['Location'])

    def test_media_fallback_redirects_for_missing_clothing_file(self):
        client = Client()
        # Request a non-existent clothing image file
        response = client.get('/media/products/some_non_existent_trouser.jpg')
        # It should redirect (302) to the Unsplash clothing placeholder
        self.assertEqual(response.status_code, 302)
        self.assertIn('unsplash.com', response['Location'])
        self.assertIn('photo-1479064555552-3ef4979f8908', response['Location'])

    def test_media_fallback_redirects_for_general_file(self):
        client = Client()
        # Request a non-existent general image file
        response = client.get('/media/products/some_random_thing.jpg')
        # It should redirect (302) to the Unsplash general placeholder
        self.assertEqual(response.status_code, 302)
        self.assertIn('unsplash.com', response['Location'])
        self.assertIn('photo-1441986300917-64674bd600d8', response['Location'])
