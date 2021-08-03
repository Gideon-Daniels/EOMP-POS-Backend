import hmac
import sqlite3
import datetime

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, id, name, surname, username, password, email):
        self.id = id
        self.name = name
        self.surname = surname
        self.username = username
        self.password = password
        self.email = email


def fetch_users():
    with sqlite3.connect('POS.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users_ = cursor.fetchall()

        new_data = []

        for data in users_:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


users = fetch_users()


# Creating database and tables
def init_user_table():
    conn = sqlite3.connect('POS.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS users("
                 "user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "surname TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL,"
                 "email TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


def init_product_table():
    with sqlite3.connect("POS.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS products("
                     "product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "title TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "image TEXT NOT NULL,"
                     "price INTEGER NOT NULL,"
                     "type TEXT NOT NULL"
                     ")")
    print("Table products created successfully")


init_user_table()
init_product_table()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode("utf-8"), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


# CREATING FLASK
app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


# Inserting information into Database
@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        first_name = request.form['first_name']
        surname = request.form['surname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        with sqlite3.connect('POS.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "surname,"
                           "username,"
                           "password"
                           "email) VALUES(?, ?, ?, ?, ?)", (first_name, surname, username, password, email))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/create-product/', methods=["POST"])
@jwt_required()
def create_product():
    response = {}

    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        image = request.form['image']
        price = request.form['price']
        type = request.form['type']

        with sqlite3.connect('POS.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products("
                           "title"
                           "description"
                           "image"
                           "price"
                           "type) VALUE(?, ?, ?, ?, ?)", (title, description, image, price, type))
            conn.commit()
            response['status_code'] = 201
            response['description'] = "Product added successfully"
        return response


@app.route('/get-product/', methods=["GET"])
def get_products():
    response = {}
    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")

        product = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = product
    return response


@app.route("/delete-product/<int:product_id>")
@jwt_required()
def delete_post(product_id):
    response = {}
    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product deleted successfully."
    return response


@app.route('/edit-post/<int:post_id>', methods=["PUT"])
@jwt_required
def edit_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('POST.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("title") is not None:
                put_data["title"] = incoming_data.get("title")
                with sqlite3.connect('POS.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET title =? WHERE id=?", (put_data["title"], product_id))

            if incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")

                with sqlite3.connect("POS.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET description =? WHERE id=?", (put_data["content"], product_id))
                    conn.commit()

                    response["description"] = "Description Updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")

                with sqlite3.connect("POS.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET price =? WHERE id=?", (put_data["price"], product_id))
                    conn.commit()

                    response["Price"] = "Price Updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("image") is not None:
                put_data["image"] = incoming_data.get("image")

                with sqlite3.connect("POS.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET image =? WHERE id=?", (put_data["image"], product_id))
                    conn.commit()

                    response["image"] = "Images Updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("type") is not None:
                put_data["type"] = incoming_data.get("type")

                with sqlite3.connect("POS.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET type =? WHERE id=?", (put_data["type"], product_id))
                    conn.commit()

                    response["type"] = "Type Updated successfully"
                    response["status_code"] = 200
    return response


@app.route('/get-product/<int:post_id>/', methods=["GET"])
def get_one_product(post_id):
    response = {}

    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products where id=" + str(post_id))

        response["status_code"] = 200
        response["description"] = "Product retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)
