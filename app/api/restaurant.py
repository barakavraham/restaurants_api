from app import db
from app.api import base_api, SubpathApi
from app.models.restaurant import Restaurant, RestaurantDish, OrderDish, Order
from app.models.validations.restaurant import RestaurantSchema, RestaurantDishSchema
from flask import jsonify, make_response
from flask_restful import Resource, reqparse


subpath_api = SubpathApi(base_api, '/restaurant', 'restaurant')

class RestaurantAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('address', type=str, required=True)
        super(RestaurantAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        schema = RestaurantSchema()
        validate = schema.validate(args)
        if validate:
            return make_response(jsonify(validate), 400)
        new_restaurant = Restaurant(name=args['name'], address=args['address'])
        db.session.add(new_restaurant)
        db.session.commit()
        return new_restaurant.get_dict(), 201

    @staticmethod
    def get():
        restaurants = [restaurant.get_dict() for restaurant in Restaurant.query.all()]
        return jsonify(restaurants)


base_api.add_resource(RestaurantAPI, '/restaurants', endpoint='restaurants')

class RestaurantInfoAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('address', type=str, required=True)
        super(RestaurantInfoAPI, self).__init__()

    @staticmethod
    def get(restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        return restaurant.get_dict(), 200

    @staticmethod
    def delete(restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        results = {**restaurant.get_dict(), 'msg': 'The restaurant has been deleted.'}
        db.session.delete(restaurant)
        db.session.commit()
        return results, 200

    def patch(self, restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        args = self.reqparse.parse_args()
        schema = RestaurantSchema()
        validate = schema.validate(args)
        if validate:
            return make_response(jsonify(validate), 400)
        restaurant.name = args['name']
        restaurant.address = args['address']
        db.session.commit()
        return {**restaurant.get_dict(), 'msg': 'The dish has been patched'}, 200


subpath_api.add_resource(RestaurantInfoAPI, '/<int:restaurant_id>', endpoint='<int:restaurant_id>')

class RestaurantDishAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('price', type=float, required=True)
        super(RestaurantDishAPI, self).__init__()

    @staticmethod
    def get(restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        dishes = [dish.get_dict() for dish in restaurant.dish if not dish.deleted]
        return jsonify(dishes)

    def post(self, restaurant_id):
        Restaurant.query.get_or_404(restaurant_id)
        args = self.reqparse.parse_args()
        schema = RestaurantDishSchema()
        validate = schema.validate(args)
        if validate:
            return make_response(jsonify(validate), 400)
        new_dish = RestaurantDish(restaurant_id=restaurant_id, name=args['name'], price=args['price'])
        db.session.add(new_dish)
        db.session.commit()
        return new_dish.get_dict(), 201


subpath_api.add_resource(RestaurantDishAPI, '/<int:restaurant_id>/menu', endpoint='menu')

class RestaurantDishInfoAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('price', type=float, required=True)
        super(RestaurantDishInfoAPI, self).__init__()

    @staticmethod
    def find_dish(restaurant_id, dish_id):
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return {'dish': None, 'err': 'Restaurant not found'}
        dish = RestaurantDish.query.filter_by(restaurant_id=restaurant_id).\
            filter_by(id=dish_id).filter_by(deleted=False).first()
        return {'dish': dish, 'err': ''} if dish else {'dish': None, 'err': 'Dish not found in the restaurant menu'}

    @staticmethod
    def update_order_dishes(dish, new_dish_id):
        for order_dish in dish.order_dish:
            order_dish.restaurant_dish_id = new_dish_id
        db.session.commit()

    def get(self, restaurant_id, dish_id):
        results = self.find_dish(restaurant_id, dish_id)
        return results['dish'].get_dict() if results['dish'] else (results['err'], 404)

    def delete(self, restaurant_id, dish_id):
        results = self.find_dish(restaurant_id, dish_id)
        if not results['dish']:
            return results['err'], 404
        results['dish'].deleted = True
        db.session.commit()
        return {**results['dish'].get_dict(), 'msg': 'The dish has been deleted'}, 200

    def patch(self, restaurant_id, dish_id):
        args = self.reqparse.parse_args()
        results = self.find_dish(restaurant_id, dish_id)
        if not results['dish']:
            return results['err'], 404

        schema = RestaurantDishSchema()
        validate = schema.validate(args)
        if validate:
            return make_response(jsonify(validate), 400)
        dish = results['dish']
        dish_copy = RestaurantDish(name=dish.name, restaurant_id=dish.restaurant_id, price=dish.price, deleted=True)
        db.session.add(dish_copy)
        db.session.commit()
        self.update_order_dishes(dish, dish_copy.id)
        dish.name = args['name']
        dish.price = args['price']
        db.session.commit()
        return {**dish.get_dict(), 'msg': 'The dish has been patched'}, 200


subpath_api.add_resource(RestaurantDishInfoAPI, '/<int:restaurant_id>/menu/<int:dish_id>', endpoint='<int:dish_id>')

class OrderAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('dishes_id', type=list, required=True, location='json')
        super(OrderAPI, self).__init__()

    @staticmethod
    def find_dish(restaurant_id, dish_id):
        dish = RestaurantDish.query.filter_by(restaurant_id=restaurant_id).\
            filter_by(id=dish_id).filter_by(deleted=False).first()
        return dish

    @staticmethod
    def get(restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        orders_dict = [order.get_dict() for order in restaurant.order]
        return jsonify(orders_dict)

    def post(self, restaurant_id):
        Restaurant.query.get_or_404(restaurant_id)
        args = self.reqparse.parse_args()
        if not args['dishes_id']:
            return 'You must enter 1 or more dishes to make an order', 404
        order_dishes = [self.find_dish(restaurant_id, dish_id) for dish_id in args['dishes_id']]
        if not all(dish for dish in order_dishes):
            return 'You must enter only dishes that appears in the restaurant menu', 404
        new_order = Order(restaurant_id=restaurant_id)
        db.session.add(new_order)
        db.session.commit()
        for dish in order_dishes:
            order_dish = OrderDish(order_id=new_order.id,
                                   restaurant_dish_id=dish.id,
                                   price=dish.price)
            db.session.add(order_dish)
        db.session.commit()
        return new_order.get_dict(), 200


subpath_api.add_resource(OrderAPI, '/<int:restaurant_id>/orders', endpoint='orders')
