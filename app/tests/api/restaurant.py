import json
from app import db
from app.tests.api import APITestCase


class RestaurantAPITestCase(APITestCase):
    def test_restaurant(self):
        url = '/api/restaurants'

        res = self.test_client.get(f'{url}')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        assert not data
        res = self.test_client.post(f'{url}?name=Buger salon&address=zimbabwe')
        self.assertEqual(res.status_code, 201)
        res = self.test_client.get(f'{url}')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        assert data


    def test_restaurants_info(self):
        url = '/api/restaurant'

        res = self.test_client.get(f'{url}/1')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.delete(f'{url}/1')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.patch(f'{url}/1?name=yummi&address=Yad haamama')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.post(f'{url}s?name=Buger salon&address=zimbabwe')
        res = self.test_client.patch(f'{url}/1?name=yummi&address=Yasu')
        self.assertEqual(res.status_code, 200)
        res = self.test_client.get(f'{url}/1')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        assert data['name'] == 'yummi' and data['address'] == 'Yasu'
        res = self.test_client.patch(f'{url}/1?name=yummi&address=Y')
        self.assertEqual(res.status_code, 400)
        res = self.test_client.delete(f'{url}/1')
        self.assertEqual(res.status_code, 200)
        res = self.test_client.get(f'{url}/1')
        self.assertEqual(res.status_code, 404)


    def test_restaurant_dish(self):
        url = '/api/restaurant'

        res = self.test_client.get(f'{url}/1/menu')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.post(f'{url}/1/menu?name=Chicken&price=99')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.post(f'{url}s?name=Buger salon&address=zimbabwe')
        res = self.test_client.post(f'{url}/1/menu?name=Chicken&price=900999')
        self.assertEqual(res.status_code, 400)
        res = self.test_client.post(f'{url}/1/menu?name=Chicken&price=20')
        self.assertEqual(res.status_code, 201)
        res = self.test_client.get(f'{url}/1/menu')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        assert data

