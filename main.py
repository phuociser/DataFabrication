from datetime import date

import faker
import mysql.connector
from flask import Flask, jsonify, Response
import json
fake = faker.Faker()

app = Flask(__name__)


def db_connect():
    conn = mysql.connector.connect(
        database='test',  # Replace 'your_database_name' with your actual database name
        user='root',
        password='root',
        host='localhost'
    )
    return conn


def create_table():
    """
    Customer table
    :return:
    """
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customer (
        customer_id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        last_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        address VARCHAR(255) NOT NULL,
        phone_number VARCHAR(255) NOT NULL,
        date_of_birth DATE NOT NULL,
        date_created DATE NOT NULL DEFAULT CURRENT_DATE,
        date_updated DATE NOT NULL DEFAULT CURRENT_DATE
    )
    """)
    conn.commit()
    cur.close()
    conn.close()


customer = []


def populate_table_with_fake_data():
    conn = db_connect()
    cur = conn.cursor()
    for i in range(21, 100):
        customer.append(
            (i,
             fake.first_name(),
             fake.last_name(),
             fake.email(),
             fake.address(),
             fake.phone_number(),
             fake.date_of_birth(minimum_age=18, maximum_age=70)))
    cur.executemany(
        """ insert into customer (
        customer_id,first_name,last_name,email,address,phone_number,date_of_birth) values (%s,%s,%s,%s,%s,%s,%s)
        """, customer
    )
    cur.close()
    conn.commit()
    conn.close()

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat() # serialize date as a string in ISO format
        return super().default(obj)

@app.route('/customer', methods=['GET'])
def customer():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute('SELECT * FROM customer')

    customers = cur.fetchall()

    cur.close()
    conn.close()

    column_names = [desc[0] for desc in cur.description]
    customers_list = [dict(zip(column_names, customer)) for customer in customers]

    json_data = json.dumps(customers_list, indent=2, cls=CustomJSONEncoder)
    return  Response(json_data, content_type='application/json')



if __name__ == '__main__' :
    populate_table_with_fake_data()


