import json
from app import db
from tests.api import APITestCase


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

        #Testing when database is empty
        res = self.test_client.get(f'{url}/1')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.delete(f'{url}/1')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.patch(f'{url}/1?name=yummi&address=Yad haamama')
        self.assertEqual(res.status_code, 404)

        #Testing after database is filled with data
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

        #Testing when database is empty
        res = self.test_client.get(f'{url}/1/menu')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.post(f'{url}/1/menu?name=Chicken&price=99')
        self.assertEqual(res.status_code, 404)
        
        #Testing after database is filled with data
        res = self.test_client.post(f'{url}s?name=Buger salon&address=zimbabwe')
        self.assertEqual(res.status_code, 201)
        res = self.test_client.post(f'{url}/1/menu?name=Chicken&price=900999')
        self.assertEqual(res.status_code, 400)
        res = self.test_client.post(f'{url}/1/menu?name=Chicken&price=20')
        self.assertEqual(res.status_code, 201)
        res = self.test_client.get(f'{url}/1/menu')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        assert data

    def test_restaurant_dish_info(self):
        url = '/api/restaurant'

        #Testing when database is empty
        res = self.test_client.get(f'{url}/1/menu/1')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.patch(f'{url}/1/menu/1?name=test&price=0')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.delete(f'{url}/1/menu/1')
        self.assertEqual(res.status_code, 404)

        self.fill_db_resturants()

        #Testing after database is filled with data
        res = self.test_client.get(f'{url}/1/menu/1')
        self.assertEqual(res.status_code, 200)
        res = self.test_client.get(f'{url}/2/menu/1')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.patch(f'{url}/2/menu/1?name=test&price=0')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.delete(f'{url}/2/menu/1')
        self.assertEqual(res.status_code, 404)
        res = self.test_client.patch(f'{url}/1/menu/1?name=test&price=0')
        self.assertEqual(res.status_code, 200)
        res = self.test_client.get(f'{url}/1/menu/1')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        assert data['name'] == 'test'
        res = self.test_client.delete(f'{url}/1/menu/1')
        self.assertEqual(res.status_code, 200)
        res = self.test_client.get(f'{url}/1/menu/1')
        self.assertEqual(res.status_code, 404)

        #Testing after deleting a restaurant
        res = self.test_client.get(f'{url}/1/menu/2')
        self.assertEqual(res.status_code, 200)
        self.test_client.delete(f'{url}/1')
        res = self.test_client.get(f'{url}/1/menu/2')
        self.assertEqual(res.status_code, 404)

    def test_restaurant_orders(self):
        url = '/api/restaurant'

        #Testing when database is empty
        res = self.test_client.get(f'{url}/1/orders')
        self.assertEqual(res.status_code, 404)

        self.fill_db_resturants()

        #Testing after database is filled with data
        res = self.test_client.post(f'{url}/1/orders', json={'dishes_id': [1, 2, 3]})
        self.assertEqual(res.status_code, 200)
        res = self.test_client.get(f'{url}/1/orders')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        assert len(data) == 1
        res = self.test_client.get(f'{url}/2/orders')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        assert not data
        res = self.test_client.post(f'{url}/1/orders', json={'dishes_id': [5]})
        self.assertEqual(res.status_code, 404)
        res = self.test_client.post(f'{url}/1/orders', json={'dishes_id': []})
        self.assertEqual(res.status_code, 404)

        #Testing orders after deleting menu item
        self.test_client.post(f'{url}/1/orders', json={'dishes_id': [1]})
        res = self.test_client.get(f'{url}/1/orders')
        data_orders = json.loads(res.data)
        res = self.test_client.delete(f'{url}/1/menu/1')
        self.assertEqual(res.status_code, 200)
        res = self.test_client.get(f'{url}/1/orders')
        data = json.loads(res.data)
        assert data == data_orders
