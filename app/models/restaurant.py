import datetime
from app import db
from sqlalchemy.orm import backref


class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(100), unique=False, nullable=False)
    deleted = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    dish = db.relationship('RestaurantDish', backref=backref('restaurant', uselist=False))
    order = db.relationship('Order', backref=backref('restaurant', uselist=False))

    def get_dict(self):
        return {'id': self.id, 'name': self.name, 'address': self.address}


class RestaurantDish(db.Model):
    __tablename__ = 'restaurant_dishes'
 
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    name = db.Column(db.String(20), unique=False, nullable=False)
    price = db.Column(db.Integer, unique=False, nullable=False)
    deleted = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    order_dish = db.relationship('OrderDish', backref=backref('restaurant_dish', uselist=False))

    def get_dict(self):
        return {'id': self.id, 'name': self.name, 'price': self.price, 'restaurant': self.restaurant.name}


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    order_dish = db.relationship('OrderDish', backref=backref('order', uselist=False))

    def get_dict(self):
        return {
            'order_id': self.id,
            'order_date': self.date.strftime('%B %d %Y - %H:%M:%S'),
            'restaurant': self.restaurant.name,
            'dishes': [dish.get_dict() for dish in self.order_dish]
        }


class OrderDish(db.Model):
    __tablename__ = 'order_dishes'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    restaurant_dish_id = db.Column(db.Integer, db.ForeignKey('restaurant_dishes.id'))
    price = db.Column(db.Integer, unique=False, nullable=False)

    def get_dict(self):
        return {'dish_name': self.restaurant_dish.name, 'price': self.price}