import hmac
import smtplib
import sqlite3
import datetime
from flask import Flask, request, jsonify, url_for
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message


# Global functions
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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
                     "user_id INTEGER NOT NULL,"
                     "title TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "image TEXT NOT NULL,"
                     "price INTEGER NOT NULL,"
                     "type TEXT NOT NULL,"
                     "quantity INTEGER NOT NULL,"
                     "FOREIGN KEY (user_id) REFERENCES users(user_id))")
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


# Users ENDPOINT
@app.route('/users/', methods=["GET", "POST", "POST"])
def user_registration():
    response = {}
    # Get Users
    if request.method == "GET":
        try:
            with sqlite3.connect("POS.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")

                all_users = cursor.fetchall()

            response['status_code'] = 201
            response['data'] = all_users
            response['status_code'] = 401
            response['message'] = "Successfully to retrieved users"
        except:
            response['status_code'] = 401
            response['message'] = "Failed to retrieve users"

    # Register User
    elif request.method == "POST":
        first_name = request.json['first_name']
        surname = request.json['surname']
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']
        try:
            with sqlite3.connect('POS.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users("
                               "first_name,"
                               "surname,"
                               "username,"
                               "password,"
                               "email) VALUES(?, ?, ?, ?, ?)", (first_name, surname, username, password, email))
                conn.commit()
                response["message"] = "successfully added User"
                response["status_code"] = 201
        except:
            response["message"] = "Failed to register user"
            response["status_code"] = 401

    #   Login Details
    elif request.method == "PATCH":
        username = request.json["username"]
        password = request.json["password"]
        try:
            with sqlite3.connect("SMP.db") as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE users=? AND password=?", (username, password))
        except:
            response["message"] = "Failed to retrieve user details"
            response["status_code"] = 401
    else:
        response["status_code"] = 402
        response['message'] = "Wrong method selected"
    return response


# PRODUCTS ENDPOINTS
@app.route('/products/', methods=["GET", "POST"])
# @jwt_required()
def add_product():
    response = {}
    # display products
    if request.method == "GET":
        try:
            with sqlite3.connect("POS.db") as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM products")
                products = cursor.fetchall()
                counter = 0

            for count in products:
                counter += 1

            response['status_code'] = 201
            response['data'] = products
            response['total'] = counter
            response['description'] = "Product to retrieved succesffuly"
        except :
            response['status_code'] = 401
            response['description'] = "Failed to retrieve product"

    # Add products
    elif request.method == "POST":
        title = request.json['title']
        description = request.json['description']
        image = request.json['image']
        price = request.json['price']
        type = request.json['type']
        user_id = request.json['user_id']
        quantity = request.json['quantity']
        try:
            with sqlite3.connect('POS.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products("
                               "user_id,"
                               "title,"
                               "description,"
                               "image,"
                               "price,"
                               "quantity,"
                               "type) VALUES(?, ?, ?, ?, ?, ?, ?)", (user_id, title, description, image, price,
                                                                     quantity, type))
                conn.commit()
                response['status_code'] = 201
                response['description'] = "Product added successfully"
        except:
            response['status_code'] = 401
            response['description'] = "Failed to add product"
    return response


@app.route("/product/<int:product_id>", methods=["GET", "PUT", "DELETE"])
# @jwt_required()
def product(product_id):
    response = {}
    # retrieves product based on id given
    if request.method == "GET":
        try:
            with sqlite3.connect("POS.db") as conn:
                cursor = conn.cursor()
                conn.row_factory = dict_factory
                cursor.execute("SELECT * FROM products where product_id=" + str(product_id))

                response["status_code"] = 201
                response["description"] = "Product retrieved successfully"
                response["data"] = cursor.fetchone()
        except:
            response["status_code"] = 401
            response["description"] = "Failed to retrieve product"

    # deletes product based on id given
    elif request.method == "DELETE":
        try:
            with sqlite3.connect("POS.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE product_id=" + str(product_id))
                conn.commit()
                response['status_code'] = 201
                response['message'] = "Product deleted successfully."
        except:
            response['status_code'] = 401
            response['message'] = "Failed to delete product."

    # updates product information based on id given
    elif request.method == "PUT":
        with sqlite3.connect('POS.db') as conn:
            incoming_data = dict(request.json)  # put request inside and dictionary
            put_data = {}
            # updates title
            if incoming_data.get("title") is not None:
                put_data["title"] = incoming_data.get("title")
                try:
                    with sqlite3.connect('POS.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE products SET title =? WHERE product_id=?", (put_data["title"], product_id))

                        conn.commit()

                        response["title"] = "title Updated successfully"
                        response["status_code"] = 201
                except:
                    response["title"] = "title Updated unsuccessfully"
                    response["status_code"] = 401
            # updates description
            if incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")
                try:
                    with sqlite3.connect("POS.db") as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE products SET description =? WHERE product_id=?", (put_data["content"],
                                                                                                 product_id))
                        conn.commit()

                        response["description"] = "Description Updated successfully"
                        response["status_code"] = 201
                except:
                    response["description"] = "Description Updated unsuccessfully"
                    response["status_code"] = 401
            # updates price
            if incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")
                try:
                    with sqlite3.connect("POS.db") as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE products SET price =? WHERE product_id=?",
                                       (put_data["price"], product_id))
                        conn.commit()

                        response["Price"] = "Price Updated successfully"
                        response["status_code"] = 201
                except :
                    response["Price"] = "Price Updated unsuccessfully"
                    response["status_code"] = 401
            # updates image
            if incoming_data.get("image") is not None:
                put_data["image"] = incoming_data.get("image")
                try:
                    with sqlite3.connect("POS.db") as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE products SET image =? WHERE product_id=?", (put_data["image"], product_id))
                        conn.commit()

                        response["image"] = "Images Updated successfully"
                        response["status_code"] = 201
                except:
                    response["image"] = "Images Updated unsuccessfully"
                    response["status_code"] = 401

            # updates type
            if incoming_data.get("type") is not None:
                put_data["type"] = incoming_data.get("type")
                try:
                    with sqlite3.connect("POS.db") as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE products SET type =? WHERE product_id=?", (put_data["type"], product_id))
                        conn.commit()

                        response["type"] = "Type Updated successfully"
                        response["status_code"] = 201
                except:
                    response["type"] = "Type updated unsuccessfully"
                    response["status_code"] = 401

            # updates quantity
            if incoming_data.get("quantity") is not None:
                put_data["type"] = incoming_data.get("type")
                try :
                    with sqlite3.connect("POS.db") as conn:
                        cursor =conn.cursor()
                        cursor.execute("UPDATE products SET quantity=? WHERE product_id=?", (put_data["type"],
                                                                                             product_id))
                        conn.commit()

                        response["quantity"] = "Quantity updated successfully"
                        response["status_code"] = 201
                except:
                    response["quantity"] = "Quantity updated unsuccessfully"
                    response["status_code"] = 401

    return response
# return jsonify(response)


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
