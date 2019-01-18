from flask import Flask, render_template, url_for, request, Response, flash, redirect, session
from fishshop import app
from fishshop.forms import LoginForm
from fishshop.data import db_connection

import xml.etree.ElementTree as et


db_con = db_connection()

# B2C Webshop


@app.route('/')
@app.route('/home')
def home():
    '''
    This is the start page of our webshop.
    '''

    return render_template('home.html', title='Home', authorized=checkSession())


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Login page so the use can login to the system. Get session for a user
    '''
    form = LoginForm()
    if form.validate_on_submit():

        # check if user is in the database
        customer = db_con.authorize(
            int(form.customer_id.data), password=form.password.data)

        if customer:

            flash('You have been logged in!', 'success')

            # Create a sesssion
            # session['customer_id'] = customer['customer_id']
            session['customer'] = customer

            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check id and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():

    session.pop('customer_id', None)
    return redirect(url_for('home'))


@app.route('/products')
def products():
    '''
    Here the user can see all products which are available.
    '''
    # TODO: Modify the template to check some products to buy. Use a Button to proceed with purchasing.
    products = db_con.get_products()  # get products from the database
    return render_template('products.html', title='Products', products=products, authorized=checkSession())


@app.route('/search')
def search():
    '''
    Here the user can search for a sepcific product
    '''

    return render_template('search.html', title='Search', authorized=checkSession())


@app.route('/cart')
def cart():

    return 'your shopping cart'


@app.route('/dashboard')
def dashboard():
    '''
    If a user is logged in, he or she can manage the orders here. If the user is an admin the user has additional
    functions.

    UC: storno / administration
    '''
    return "dashboard"


# B2B Webshop
# Here the EDI is implemented. All methods must have some authorization mechanism.

@app.route('/api/products')
def api_products():
    '''
    Get a list of all Products
    '''

    products = db_con.get_products()

    # building xml
    root = et.Element('products')

    for p in products:
        product = et.SubElement(root, 'product')
        product_id = et.SubElement(product, 'id')
        product_id.text = str(p['product_id'])
        title = et.SubElement(product, 'title')
        title.text = str(p['title'])
        price = et.SubElement(product, 'price')
        price.text = str(p['price'])
        available = et.SubElement(product, 'available')
        available.text = str(p['available'])

    xml_str = et.tostring(root, encoding='utf8', method='xml')

    return Response(xml_str, mimetype='text/xml')


@app.route('/api/search', methods=['GET', 'PUT'])
def api_search():
    # TODO
    if request.method == 'PUT':
        return "XML with list of search results"
    else:
        # Return schema of search
        return 'Schema'


@app.route('/api/orders', methods=['GET', 'PUT'])
def cancellation():
    '''
    FINISHED
    Customer must be authorized.

    GET: Get a list of all orders of a user
    PUT: Cancel a specific order
    '''
    # Authorization
    customer = authorize(request)

    if request.method == 'PUT':
        # cancel order and send back confirmation.

        # reading the xml from the request
        root = et.fromstring(request.data)

        # get order id from request
        order_id = root.findall(".//bestellungid")  # returns a list

        # cancel order
        return db_con.cancel_order(customer['customer_id'], int(order_id[0].text))

    else:
        # return a list of orders from a user
        orders = db_con.get_orders(customer['customer_id'])

        # building xml
        root = et.Element('orders')

        for o in orders:
            order = et.SubElement(root, 'order')
            order_id = et.SubElement(order, 'id')
            order_id.text = str(o['order_id'])
            customer_id = et.SubElement(order, 'customer_id')
            customer_id.text = str(o['customer_id'])
            payment_id = et.SubElement(order, 'payment_id')
            payment_id.text = str(o['payment_id'])

            # build all products in an order
            products = et.SubElement(order, 'products')
            for p in o['products']:
                product = et.SubElement(products, 'product')
                product_id = et.SubElement(product, 'product_id')
                product_id.text = str(p['product_id'])
                quantity = et.SubElement(product, 'quantity')
                quantity.text = str(p['quantity'])

            bought = et.SubElement(order, 'bought')
            bought.text = str(o['bought'])
            canceled = et.SubElement(order, 'canceled')
            canceled.text = str(o['canceled'])

    # creating from a string
    xml_str = et.tostring(root, encoding='utf8', method='xml')

    return Response(xml_str, mimetype='text/xml')


def authorize(request):
    '''
    This is a method to authorize a customer. If login is missing or is wrong response with error message will sent. Else this
    method returns the customer object.
    '''
    auth = request.authorization

    if not auth:
        return "You are not authorized!"

    customer = db_con.authorize(int(auth.username), auth.password)

    if not customer:
        return "Wrong customer id or password!"

    # if authorization is ok return object of customer
    return customer


def checkSession():
    '''
    This method checks if a session exists
    '''
    if 'customer' in session:
        return True
    else:
        return False


if __name__ == '__main__':
    app.run(debug=True)