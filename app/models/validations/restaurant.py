from app import ma
from app.models.restaurant import Restaurant
from marshmallow import fields, validate, ValidationError


def validate_unique_name(name):
    if Restaurant.query.filter_by(name=name).first():
        raise ValidationError('Restaurant name must be unique')

class RestaurantSchema(ma.SQLAlchemyAutoSchema):
    name = fields.Str(required=True, validate=[validate.Length(min=3, max=20), validate_unique_name])
    address = fields.Str(validate=[validate.Length(min=3, max=50)])


class RestaurantDishSchema(ma.SQLAlchemyAutoSchema):
    name = fields.Str(required=True, validate=[validate.Length(min=3, max=20)])
    price = fields.Float(required=True, validate=[validate.Range(min=0, max=99999)])
