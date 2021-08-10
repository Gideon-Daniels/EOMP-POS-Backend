import hmac
import smtplib
import sqlite3
import datetime
from flask import Flask, request, jsonify, url_for
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message


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
            new_data.append(User(data[0], data[1], data[2], data[3], data[4], data[5]))
    return new_data


def validation_user_registration(name, surname, username, password, email):
    name = name
    surname = surname
    username = username
    password = password
    email = email
    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        new_data = []

        validation_passed = False

        for data in users:
            new_data.append(data)
    if username in new_data and password in new_data and email in new_data:
        return validation_passed
    elif name == " " or surname == " " or username == " " or password == " " or \
            email == " ":
        return validation_passed
    elif len(name) == 12 and len(surname) == 12:
        return validation_passed
    elif '@' not in email:
        return validation_passed
    else:
        validation_passed = True
        return validation_passed


class Products(object):
    def __init__(self, id, title, description, image, price, type):
        self.id = id
        self.title = title
        self.description = description
        self.image = image
        self.price = price
        self.type = type


def fetch_products():
    with sqlite3.connect('POS.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products_ = cursor.fetchall()

        new_data = []

        for data in products_:
            new_data.append(Products(data[0], data[1], data[2], data[3], data[4], data[5]))
        return new_data


users = fetch_users()
product = fetch_products()


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
    conn.close()


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
CORS(app)  # cross platform connection to netlify
app.debug = True
# authenticate a token , making my app secure
app.config['SECRET_KEY'] = 'super-secret'
jwt = JWT(app, authenticate, identity)
# configuration for sending emails
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ashwinjansen.dragoonix@gmail.com'
app.config['MAIL_PASSWORD'] = 'ashwinjansen9x#'  # enter password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


# Inserting information into Database
@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        first_name = request.json['first_name']
        surname = request.json['surname']
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']
        if not validation_user_registration(first_name, surname, username, password, email):
            response["message"] = "User Already Exist"
            response["status_code"] = 201
        else:
            with sqlite3.connect('POS.db') as conn:
                cursor = conn.cursor()
                try :
                    cursor.execute("INSERT INTO users("
                                   "first_name,"
                                   "surname,"
                                   "username,"
                                   "password,"
                                   "email) VALUES(?, ?, ?, ?, ?)", (first_name, surname, username, password, email))
                    conn.commit()
                    response["message"] = "success"
                    response["status_code"] = 201

                except :
                    response["status_code"] = 401
                    response['message'] = "Database failed"
        return response


# Show all the users
@app.route('/show-users/', methods=["GET"])
@jwt_required()
def show_users():
    response = {}
    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")

        all_users = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = all_users
    return response


@app.route('/add-product/', methods=["POST"])
@jwt_required()
def add_product():
    response = {}

    if request.method == "POST":
        title = request.json['title']
        description = request.json['description']
        image = request.json['image']
        price = request.json['price']
        type = request.json['type']

        with sqlite3.connect('POS.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products("
                           "title,"
                           "description,"
                           "image,"
                           "price,"
                           "type) VALUES(?, ?, ?, ?, ?)", (title, description, image, price, type))
            conn.commit()
            response['status_code'] = 201
            response['description'] = "Product added successfully"
        return response


# show all the products
@app.route('/show-products/', methods=["GET"])
def show_products():
    response = {}
    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        counter = 0

    for count in products:
        counter += 1

    response['status_code'] = 200
    response['data'] = products
    response['total'] = counter
    return response


@app.route("/delete-product/<int:product_id>")
@jwt_required()
def delete_product(product_id):
    response = {}
    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product deleted successfully."
    return response


@app.route('/edit-product/<int:product_id>/', methods=["PUT"])
@jwt_required()
def edit_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('POS.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("title") is not None:
                put_data["title"] = incoming_data.get("title")
                with sqlite3.connect('POS.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET title =? WHERE product_id=?", (put_data["title"], product_id))

                    conn.commit()

                    response["description"] = "Description Updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")

                with sqlite3.connect("POS.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET description =? WHERE product_id=?", (put_data["content"],
                                                                                             product_id))
                    conn.commit()

                    response["description"] = "Description Updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")

                with sqlite3.connect("POS.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET price =? WHERE product_id=?", (put_data["price"], product_id))
                    conn.commit()

                    response["Price"] = "Price Updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("image") is not None:
                put_data["image"] = incoming_data.get("image")

                with sqlite3.connect("POS.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET image =? WHERE product_id=?", (put_data["image"], product_id))
                    conn.commit()

                    response["image"] = "Images Updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("type") is not None:
                put_data["type"] = incoming_data.get("type")

                with sqlite3.connect("POS.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET type =? WHERE product_id=?", (put_data["type"], product_id))
                    conn.commit()

                    response["type"] = "Type Updated successfully"
                    response["status_code"] = 200
    return response


# Show only only one product
@app.route('/show-product/<int:post_id>/', methods=["GET"])
def show_product(post_id):
    response = {}

    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products where product_id=" + str(post_id))

        response["status_code"] = 200
        response["description"] = "Product retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


@app.route('/total-price')
def calculating_total():
    response = {}

    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(price) from products")
        total = cursor.fetchall()
        response["status_code"] = 200
        response["description"] = "Total price received"
        response["data"] = total

    return response


@app.route('/category/<string:types>/')
def category(types):
    response = {}

    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products where type=?", [types])
        total = cursor.fetchall()
        response["status_code"] = 200
        response["description"] = "Type received"
        response["data"] = total
    return response


@app.route('/mailed/<int:id>', methods=['GET', 'POST'])
def sending_mails(id):
    response = {}

    with sqlite3.connect("POS.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE user_id=" + str(id))
        users_email = cursor.fetchone()
        if request.method == 'POST':
            try:
                msg = Message('Hello', sender='ashwinjansen.dragoonix@gmail.com', recipients=[users_email])
                msg.body = "Your username and email have been confirmed."
                mail.send(msg)
                response['status_code'] = 200
                response['description'] = "Email have been send"
                response['data'] = users_email
            except smtplib.SMTPAuthenticationError:
                response["ERROR"] = "Username and Password not accepted"
        return response


if __name__ == "__main__":
    app.run()
    app.debug = True
