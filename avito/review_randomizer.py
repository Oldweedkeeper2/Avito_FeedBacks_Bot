import datetime
import random


def get_review_dates(num_reviews, num_days, max_per_day):
    if num_reviews > num_days * max_per_day:
        raise ValueError("Number of reviews exceeds maximum allowed")
    reviews_left = num_reviews
    dates = []
    for i in range(num_days):
        if i == num_days - 1 and reviews_left > 0:
            num_reviews_today = reviews_left
        else:
            num_reviews_today = random.randint(0, max_per_day) if reviews_left > max_per_day else reviews_left
        reviews_left -= num_reviews_today
        for j in range(num_reviews_today):
            review_time = datetime.time(hour=random.randint(9, 20), minute=random.randint(0, 59))
            review_date = datetime.date.today() + datetime.timedelta(days=i)
            review_datetime = datetime.datetime.combine(review_date, review_time)
            # dates.append(review_datetime)
            yield review_datetime
    # return dates


# dates = get_review_dates(num_reviews=23, num_days=10, max_per_day=4)
# for date in dates:
#     print(date.strftime("%Y-%m-%d %H:%M:%S"))
