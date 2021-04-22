import json
from app import db
from app.api import base_api, SubpathApi
from app.models.restaurant import Restaurant, RestaurantDish, OrderDish, Order
from app.models.validations.restaurant import RestaurantSchema, RestaurantDishSchema
from app.utils.restaurant import fill_database_dishes, fill_database_resturants
from flask import jsonify, make_response
from flask_restful import Resource, reqparse


subpath_api = SubpathApi(base_api, '/restaurant', 'restaurant')

class RestaurantApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('address', type=str, required=True)
        super(RestaurantApi, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        schema = RestaurantSchema()
        restaurant_name = args['name']
        restaurant_address = args['address']
        try:
            schema.load(args)
        except Exception as err:
            return make_response(jsonify(err.messages), 400)
        new_restaurant = Restaurant(name=restaurant_name, address=restaurant_address)
        db.session.add(new_restaurant)
        db.session.commit()
        return {
            'restaurant_id': new_restaurant.id,
            'restaurant_name': new_restaurant.name,
            'restaurant_address': new_restaurant.address,
            'success': True
        }, 201

    @staticmethod
    def get():
        restaurants = [restaurant.get_dict() for restaurant in Restaurant.query.all()]
        return jsonify(restaurants)

base_api.add_resource(RestaurantApi, '/restaurants', endpoint='restaurants')


class RestaurantInfoApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('address', type=str, required=True)
        super(RestaurantInfoApi, self).__init__()

    @staticmethod
    def get(restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        return restaurant.get_dict(), 200

    def delete(self, restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        db.session.delete(restaurant)
        db.session.commit()
        return 'Restaurant deleted.', 200

    def patch(self, restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        args = self.reqparse.parse_args()
        schema = RestaurantSchema()
        try:
            schema.load(args)
        except Exception as err:
            return make_response(jsonify(err.messages), 400)
        restaurant.name = args['name']
        restaurant.address = args['address']
        db.session.commit()
        return restaurant.get_dict(), 200

subpath_api.add_resource(RestaurantInfoApi, '/<int:restaurant_id>', endpoint='<int:restaurant_id>')


class RestaurantDishApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('price', type=int, required=True)
        super(RestaurantDishApi, self).__init__()

    @staticmethod
    def get(restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        dishes = [dish.get_dict() for dish in restaurant.dish if not dish.deleted]
        return jsonify(dishes)

    def post(self, restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        args = self.reqparse.parse_args()
        schema = RestaurantDishSchema()
        try:
            schema.load(args)
        except Exception as err:
            return make_response(jsonify(err.messages), 400)
        new_dish = RestaurantDish(restaurant_id=restaurant_id, name=args['name'], price=args['price'])
        db.session.add(new_dish)
        db.session.commit()
        return new_dish.get_dict(), 201

subpath_api.add_resource(RestaurantDishApi, '/<int:restaurant_id>/menu', endpoint='menu')


class RestaurantDishInfoApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('price', type=int, required=True)
        super(RestaurantDishInfoApi, self).__init__()
    
    @staticmethod
    def find_dish(restaurant_id, dish_id):
        dish = RestaurantDish.query.filter_by(restaurant_id=restaurant_id).filter_by(id=dish_id).filter_by(deleted=False).first()
        return dish

    def update_order_dishes(self, dish, new_dish_id):
        for order_dish in dish.order_dish:
            order_dish.restaurant_dish_id = new_dish_id
        db.session.commit()

    def get(self, restaurant_id, dish_id):
        dish = self.find_dish(restaurant_id, dish_id)
        if not dish:
            return 'The restaurant id or the dish id that you entered is not found!'
        return dish.get_dict()

    def delete(self, restaurant_id, dish_id):
        dish = self.find_dish(restaurant_id, dish_id)
        if not dish:
            return 'The restaurant id or the dish id that you entered is not found!'
        dish.deleted = True
        db.session.commit()
        return 'Dish deleted'

    def patch(self, restaurant_id, dish_id):
        args = self.reqparse.parse_args()  
        dish = self.find_dish(restaurant_id, dish_id)
        if not dish:
            return 'The restaurant id or the dish id that you entered is not found!'
        schema = RestaurantDishSchema()

        try:
            schema.load(args)
        except Exception as err:
            return make_response(jsonify(err.messages), 400)

        dish_copy = RestaurantDish(name=dish.name, restaurant_id=dish.restaurant_id, price=dish.price, deleted=True)
        db.session.add(dish_copy)
        db.session.commit()
        self.update_order_dishes(dish, dish_copy.id)
        dish.name = args['name']
        dish.price = args['price']
        db.session.commit()
        return dish.get_dict(), 200

subpath_api.add_resource(RestaurantDishInfoApi, '/<int:restaurant_id>/menu/<int:dish_id>', endpoint='<int:dish_id>')


class OrdersApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('dishes_id', type=list, required=True, location='json')
        super(OrdersApi, self).__init__()

    @staticmethod
    def find_dish(restaurant_id, dish_id):
        dish = RestaurantDish.query.filter_by(restaurant_id=restaurant_id).filter_by(id=dish_id).filter_by(deleted=False).first()
        return dish

    @staticmethod
    def get(restaurant_id):
        orders = Order.query.join(Restaurant, Order.restaurant_id==restaurant_id).all()
        orders_dict = [order.get_dict() for order in orders]
        return jsonify(orders_dict)

    def post(self, restaurant_id):
        args = self.reqparse.parse_args()
        if not args['dishes_id']:
            return 'You must enter at least 1 dish to send an order!', 404
        if not all(self.find_dish(restaurant_id, dish_id) for dish_id in args['dishes_id']):
            return 'You must enter only dishes that the restaurant sells!', 404
        new_order = Order(restaurant_id=restaurant_id)
        db.session.add(new_order)
        db.session.commit()
        for dish_id in args['dishes_id']:
            dish = self.find_dish(restaurant_id, dish_id)
            if dish:
                order_dish = OrderDish(order_id=new_order.id, restaurant_dish_id=dish.id, price=dish.price)
                db.session.add(order_dish)
        db.session.commit()
        return new_order.get_dict(), 200


subpath_api.add_resource(OrdersApi, '/<int:restaurant_id>/orders', endpoint='orders')
