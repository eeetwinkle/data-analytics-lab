import time
import random
import psycopg2
import os
from datetime import datetime
from faker import Faker

fake = Faker('ru_RU')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'database': os.getenv('POSTGRES_DB', 'ecommerce'),
    'user': os.getenv('POSTGRES_USER', 'user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password'),
    'port': 5432
}

PRODUCTS = [
    ("Ноутбук", "Электроника", 30000, 89900),
    ("Смартфон", "Электроника", 15000, 79900),
    ("Книга", "Книги", 300, 2500),
    ("Футболка", "Одежда", 500, 3500),
    ("Кофеварка", "Бытовая техника", 2000, 15000),
    ("Стул", "Мебель", 1500, 12000),
    ("Наушники", "Электроника", 1500, 25000),
    ("Часы", "Аксессуары", 2000, 50000),
    ("Рюкзак", "Аксессуары", 1000, 8000),
    ("Коврик для мыши", "Электроника", 200, 1500)
]

CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург",
          "Казань", "Нижний Новгород", "Челябинск", "Самара", "Омск",
          "Ростов-на-Дону", "Уфа", "Красноярск", "Пермь", "Воронеж",
          "Волгоград"]


def connect_db():
    return psycopg2.connect(**DB_CONFIG)


def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        order_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        product_name VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        quantity INTEGER NOT NULL,
        city VARCHAR(50) NOT NULL,
        customer_name VARCHAR(100),
        total_amount DECIMAL(10, 2) GENERATED ALWAYS AS (price * quantity) STORED
    )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_order_timestamp ON orders(order_timestamp)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_category ON orders(category)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_city ON orders(city)")

    conn.commit()
    cur.close()
    conn.close()


def generate_order():
    product, category, min_price, max_price = random.choice(PRODUCTS)
    price = random.uniform(min_price, max_price)
    quantity = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
    city = random.choice(CITIES)

    hour = datetime.now().hour
    if 9 <= hour <= 12:
        price_multiplier = random.uniform(0.95, 1.05)
    elif 19 <= hour <= 23:
        price_multiplier = random.uniform(1.05, 1.15)
        quantity = min(quantity + 1, 5)
    else:
        price_multiplier = random.uniform(0.9, 1.1)

    price *= price_multiplier
    price = round(price, 2)

    return {
        'product_name': product,
        'category': category,
        'price': price,
        'quantity': quantity,
        'city': city,
        'customer_name': fake.name(),
        'order_timestamp': datetime.now()
    }


def save_order(order):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(f"""
    INSERT INTO orders (product_name, category, price, quantity, city, customer_name, order_timestamp)
    VALUES ({order['product_name']}, {order['category']}, {order['price']}, {order['quantity']}, {order['city']}, 
            {order['customer_name']}, {order['order_timestamp']})""")

    conn.commit()
    cur.close()
    conn.close()

create_tables()
for i in range(100):
    try:
        order = generate_order()
        save_order(order)

        time.sleep(random.uniform(0.5, 2))

    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)


