from db.orders import *

reviews_db = ReviewsDB()

async def start_reviews(order_id):
    order_reviews = await reviews_db.get_reviews(order_id=order_id)

