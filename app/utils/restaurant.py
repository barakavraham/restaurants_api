from app import db
from app.utils.data import restaurants, restaurant_dishes
from app.models.restaurant import Restaurant, RestaurantDish


def fill_database_resturants():
    if Restaurant.query.all():
        return
    for restaurant in restaurants:
        new_restaurant = Restaurant(name=restaurant['name'], address=restaurant['address'])
        db.session.add(new_restaurant)  
    db.session.commit()

def fill_database_dishes():
    if Restaurant.query.all():
        return
    for dish in restaurant_dishes:
        new_dish = RestaurantDish(name=dish['name'], price=dish["price"])
        db.session.add(new_dish)
    db.session.commit()
