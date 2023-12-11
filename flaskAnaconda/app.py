from flask import Flask, redirect
from flask import render_template
from flask import request
from flask import session
import database as db
import authentication
import logging
import ordermanagement as om

app = Flask(__name__)

# Set the secret key to some random bytes. 
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return render_template('index.html', page = "Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page = "Products", product_list = product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code = code, product = product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page = "Branches", branch_list = branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))

    return render_template('branchdetails.html', code = code, branch = branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page = "About US")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        session["detailsError"] = False
        return redirect('/')
    else:
        session["detailsError"] = True
        return redirect('/login')


@app.route('/updatepasswordsubmit', methods = ['GET', 'POST'])
def updatepasswordsubmit():
    username = session["user"]["username"]
    password = request.form.get('oldpassword', '')
    new_password = request.form.get('newpassword', '')
    session["is_successful"], user = authentication.login(username, password)
    if(session["is_successful"]):
        db.update_password(username, new_password)
        return redirect('/')
    else:
        return redirect('/changepassword')
@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')


@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
    # A click to add a product translates to a 
    # quantity of 1 for now

    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]
    item["code"] = code

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/updatecart')
def updatecart():
    return render_template('updatecart.html')

@app.route('/updatecartsubmission', methods = ['GET', 'POST'])
def updatecartsubmission():
    cart = session["cart"]
    code = list(cart.keys())
    qty = request.form.getlist("qty")
    qty = list(map(int, qty))

    for index, x in enumerate(qty):
        product = db.get_product(int(code[index]))
        cart[code[index]]["qty"] = qty[index]
        cart[code[index]]["subtotal"] = qty[index] * product["price"]
        
    print(cart)
    session["cart"] = cart
    return redirect('/cart')

@app.route('/removeproduct')
def removeproduct():
    code = request.args.get('code', '')
    cart = session["cart"]
    print(code)
    try:
        del cart[code]
    except:
        print("code is: ",code)
    session["cart"] = cart
    return redirect('/cart')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/pastorders')
def pastorders():
    username = session["user"]["username"]
    pastorders = db.get_past_orders(username)
    return render_template('pastorders.html', pastorders = pastorders)

@app.route('/changepassword')
def changepassword():
    return render_template("changepassword.html")

@app.before_request
def reset_session_variable():
    session['is_successful'] = True