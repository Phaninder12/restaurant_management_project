from rest_framework.test import APITestCase # type: ignore
from rest_framework import status # type: ignore
from home.models import Restaurant

class RestaurantInfoAPITest(APITestCase):
    
    def test_get_restaurant_info(self):
        # 1. Create a sample Restaurant instance in the test database
        Restaurant.objects.create(
            name='Test Restaurant', 
            address='123 Test St'
        )

        # 2. Make a GET request to the restaurant info endpoint
        # Adjust the URL path if your urls.py uses a different route
        url = '/api/restaurant-info/'
        response = self.client.get(url)

        # 3. Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4. Assert that the data returned matches the sample instance
        # Note: If your API returns a list, use response.data[0]
        # If it returns a single object, use response.data
        data = response.data[0] if isinstance(response.data, list) else response.data
        
        self.assertEqual(data['name'], 'Test Restaurant')
        self.assertEqual(data['address'], '123 Test St')