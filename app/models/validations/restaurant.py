from app import ma
from app.models.restaurant import Restaurant, RestaurantDish, OrderDish

from marshmallow import fields, validate


class RestaurantSchema(ma.SQLAlchemyAutoSchema):
    name = fields.Str(required=True, validate=[validate.Length(min=3, max=20)])
    address = fields.Str(validate=[validate.Length(min=3, max=50)])


class RestaurantDishSchema(ma.SQLAlchemyAutoSchema):
    name = fields.Str(required=True, validate=[validate.Length(min=3, max=20)])
    price = fields.Integer(required=True, validate=[validate.Range(min=0, max=99999)])
