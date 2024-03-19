import sqlite3
DB_FILE = "Restaurant_system.db"

# Define the connection and cursor variables
CONNECTION = sqlite3.connect(DB_FILE)
CURSOR = CONNECTION.cursor()

class Review:
    def __init__(self, restaurant_id, customer_id, star_rating, id=None):
        self.id = id
        self.restaurant_id = restaurant_id
        self.customer_id = customer_id
        self.star_rating = star_rating

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                restaurant_id INTEGER,
                customer_id INTEGER,
                star_rating INTEGER,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        CONNECTION.commit()
        print("Review table created successfully.")

    def customer(self):
        CURSOR.execute("SELECT * FROM customers WHERE id=?", (self.customer_id,))
        customer_data = CURSOR.fetchone()
        if customer_data:
            return Customer(*customer_data)
        return None

    def restaurant(self):
        CURSOR.execute("SELECT * FROM restaurants WHERE id=?", (self.restaurant_id,))
        restaurant_data = CURSOR.fetchone()
        if restaurant_data:
            return Restaurant(*restaurant_data)
        return None

class Restaurant:
    def __init__(self, name, price, id=None):
        self.id = id
        self.name = name
        self.price = price

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price INTEGER
            )
        """)
        CONNECTION.commit()
        print("Restaurant table created successfully.")

    def add_review(self, customer, star_rating):
        review = Review(self.id, customer.id, star_rating)
        CURSOR.execute("""
            INSERT INTO reviews (restaurant_id, customer_id, star_rating) 
            VALUES (?, ?, ?)
        """, (review.restaurant_id, review.customer_id, review.star_rating))
        CONNECTION.commit()
        print(f"Review by {customer.full_name()} added successfully.")

    def reviews(self):
        CURSOR.execute("SELECT * FROM reviews WHERE restaurant_id=?", (self.id,))
        reviews_data = CURSOR.fetchall()
        return [Review(*review_data) for review_data in reviews_data]

    def customers(self):
        CURSOR.execute("""
            SELECT customers.* 
            FROM customers
            INNER JOIN reviews ON reviews.customer_id = customers.id
            WHERE reviews.restaurant_id=?
        """, (self.id,))
        customers_data = CURSOR.fetchall()
        return [Customer(*customer_data) for customer_data in customers_data]

    def count_reviews(self):
        CURSOR.execute("SELECT COUNT(*) FROM reviews WHERE restaurant_id=?", (self.id,))
        count = CURSOR.fetchone()[0]
        return count

    @classmethod
    def fanciest(cls):
        CURSOR.execute("SELECT * FROM restaurants ORDER BY price DESC LIMIT 1")
        fanciest_data = CURSOR.fetchone()
        if fanciest_data:
            return cls(*fanciest_data)
        return None

    def all_reviews(self):
        reviews = self.reviews()
        return [f"Review for {self.name} by {review.customer().full_name()}: {review.star_rating} stars." for review in reviews]

class Customer:
    def __init__(self, first_name, last_name, id=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT
            )
        """)
        CONNECTION.commit()
        print("Customer table created successfully.")

    def reviews(self):
        CURSOR.execute("SELECT * FROM reviews WHERE customer_id=?", (self.id,))
        reviews_data = CURSOR.fetchall()
        return [Review(*review_data) for review_data in reviews_data]

    def restaurants(self):
        CURSOR.execute("""
            SELECT restaurants.* 
            FROM restaurants
            INNER JOIN reviews ON reviews.restaurant_id = restaurants.id
            WHERE reviews.customer_id=?
        """, (self.id,))
        restaurants_data = CURSOR.fetchall()
        return [Restaurant(*restaurant_data) for restaurant_data in restaurants_data]

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        reviews = self.reviews()
        if reviews:
            max_rating = max(reviews, key=lambda x: x.star_rating)
            return max_rating.restaurant()
        return None

def create_tables():
    Customer.create_table()
    Restaurant.create_table()
    Review.create_table()
create_tables()

# Adding customers
customer1 = Customer("Llyod", "Nyabuto")
customer2 = Customer("Larry", "Mmbiso")
customer3 = Customer("Meshack", "Omondi")

# Adding restaurants
restaurant1 = Restaurant("CJ,s", 50)
restaurant2 = Restaurant("Black Tavern", 40)
restaurant3 = Restaurant("Hilton", 30)

# Add reviews by customers for specific restaurants
restaurant1.add_review(customer1, 4)
restaurant1.add_review(customer2, 5)
restaurant2.add_review(customer1, 3)
restaurant3.add_review(customer3, 4.5)

# Fetch  reviews for each restaurant
for restaurant in [restaurant1, restaurant2, restaurant3]:
    print(f"\nReviews for {restaurant.name} ({restaurant.count_reviews()} reviews):")
    reviews = restaurant.all_reviews()
    for review in reviews:
        print(review)

# Commit changes to the database
CONNECTION.commit()

# Close the database connection
CONNECTION.close()
