from app import db
from app.api import base_api, SubpathApi
from app.models.restaurant import Restaurant, RestaurantDish, OrderDish, Order
from flask import jsonify
from flask_restful import Resource, reqparse


subpath_api = SubpathApi(base_api, '/restaurant', 'restaurant')

class RestaurantApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('restaurant_name', type=str, required=True)
        self.reqparse.add_argument('restaurant_address', type=str, required=True)
        super(RestaurantApi, self).__init__()


    def post(self):
        args = self.reqparse.parse_args()
        restaurant_name = args['restaurant_name']
        restaurant_address = args['restaurant_address']
        new_restaurant = Restaurant(name=restaurant_name, address=restaurant_address)
        db.session.add(new_restaurant)
        db.session.commit()

        return {
            'restaurant_name': restaurant_name,
            'restaurant_address': restaurant_address,
            'success': True
        }, 201
    
    @staticmethod
    def get():
        restaurants = [restaurant.get_dict() for restaurant in Restaurant.query.filter_by(deleted=False).all()]
        return jsonify(restaurants)

base_api.add_resource(RestaurantApi, '/restaurants', endpoint='restaurants')


class RestaurantInfoApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('restaurant_name', type=str, required=False)
        self.reqparse.add_argument('restaurant_address', type=str, required=False)
        super(RestaurantInfoApi, self).__init__()

    def soft_delete(self, dishes):
        for dish in dishes:
            dish.deleted = True
        db.session.commit()

    @staticmethod
    def get(restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        return restaurant.get_dict(), 200

    def delete(self, restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        if restaurant.deleted:
            return {"message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}, 404
        self.soft_delete(restaurant.dish) #Soft delete restaurant dishes to keep their data.
        restaurant.deleted = True #Soft delete restaurant to keep their data.
        db.session.commit()
        return {'deleted': True}, 200

    def patch(self, restaurant_id):
        args = self.reqparse.parse_args()
        restaurant = Restaurant.query.get_or_404(restaurant_id)

        if args['restaurant_name'] or args['restaurant_address']:
            if args['restaurant_name']:
                restaurant.name = args['restaurant_name']
            if args['restaurant_address']:
                restaurant.address = args['restaurant_address']
            db.session.commit()
            return restaurant.get_dict(), 200
        else:
            return 'You must send a new info in order to update the restaurant!', 400

subpath_api.add_resource(RestaurantInfoApi, '/<int:restaurant_id>', endpoint='<int:restaurant_id>')


class RestaurantDishApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True)
        self.reqparse.add_argument('price', type=str, required=True)
        super(RestaurantDishApi, self).__init__()

    @staticmethod
    def get(restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        dishes = [dish.get_dict() for dish in restaurant.dish if not dish.deleted]
        return jsonify(dishes)

    def post(self, restaurant_id):
        args = self.reqparse.parse_args()
        Restaurant.query.get_or_404(restaurant_id)

        new_dish = RestaurantDish(restaurant_id=restaurant_id, name=args['name'], price=args['price'])
        db.session.add(new_dish)
        db.session.commit()

        return {}, 200

subpath_api.add_resource(RestaurantDishApi, '/<int:restaurant_id>/menu', endpoint='menu')


class RestaurantDishInfoApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=False)
        self.reqparse.add_argument('price', type=str, required=False)
        super(RestaurantDishInfoApi, self).__init__()
    
    @staticmethod
    def find_dish(restaurant_id, dish_id):
        dish = RestaurantDish.query.filter_by(restaurant_id=restaurant_id).filter_by(id=dish_id).filter_by(deleted=False).first()
        return dish      

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
        
        dish_copy = RestaurantDish(name=dish.name, restaurant_id=dish.restaurant_id, price=dish.price)

        if args['name'] or args['price']:
            if args['name']:
                dish_copy.name = args['name']
            if args['price']:
                dish_copy.price = args['price']
            dish.deleted = True #Soft delete to keep the dish data.
            db.session.add(dish_copy)
            db.session.commit()
            return dish_copy.get_dict(), 200
        else:
            return 'You must enter new values to update a dish'

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
            return 'You must enter at least 1 dish to send an order!'
        if not all(self.find_dish(restaurant_id, dish_id) for dish_id in args['dishes_id']):
            return 'You must enter only dishes that the restaurant sells!'
        new_order = Order(restaurant_id=restaurant_id)
        db.session.add(new_order)
        db.session.commit()
        print(restaurant_id)
        for dish_id in args['dishes_id']:
            dish = self.find_dish(restaurant_id, dish_id)
            if dish:
                order_dish = OrderDish(order_id=new_order.id, restaurant_dish_id=dish.id, price=dish.price)
                db.session.add(order_dish)
        db.session.commit()
        return 'Ordered'


subpath_api.add_resource(OrdersApi, '/<int:restaurant_id>/orders', endpoint='orders')
