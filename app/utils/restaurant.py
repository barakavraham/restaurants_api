from app import db
from app.utils.data import restaurants, restaurant_dishes
from app.models.restaurant import Restaurant, RestaurantDish


# Changing this function might cause tests to fail
def fill_database_resturants():
    if Restaurant.query.all():
        return
    for restaurant in restaurants:
        new_restaurant = Restaurant(name=restaurant['name'], address=restaurant['address'])
        db.session.add(new_restaurant)
    db.session.commit()
    restaurant_id = Restaurant.query.all()[0].id
    for ind, dish in enumerate(restaurant_dishes):
        if ind == 3:
            restaurant_id += 1
        new_dish = RestaurantDish(name=dish['name'], price=dish['price'], restaurant_id=restaurant_id)
        db.session.add(new_dish)
    db.session.commit()
