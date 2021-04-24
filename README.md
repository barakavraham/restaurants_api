
# Restaurants api

  

Restaurants api is a system that offering restaurant ordering service,
By using the api you can manage the restaurants, the restaurant dishes and the restaurant orders.

## List of the apis :
**/restaurants**

-   POST - Add a new restaurant
-   GET - Get list of all restaurants with their info

**/restaurant/{restaurant_id}**

-   GET - Get restaurant info
-   DELETE - Delete a restaurant and their menu/orders
-   PATCH - Update restaurant info

**/restaurant/{restaurant_id}/menu**

-   POST - Create a new menu item for this restaurant
-   GET - Get menu list for this restaurant

**/restaurant/{restaurant_id}/menu/{item_id}**  

-   GET - Get item info
-   DELETE - Delete item from the menu of this restaurant
-   PATCH - Update item info

**/restaurant/{restaurant_id}/orders**  

-   GET - Get orders list and their products
-   POST - Create a new order by passing list menu items' id

## Tests
>pytest tests/api/restaurant