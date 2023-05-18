import hashlib
import os
from datetime import timedelta

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
# from app import app
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User, Product
from store_functions import check_login

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)


@app.route('/about')
def about_page():
    return "This is the about page"
@app.route('/home')
def detail():
    return render_template('detail.html')

@app.route('/try')
def domie():
    
    return render_template('domie.html')

@app.route('/add-new-product')
def add_product_page():
    user = check_login()
    if user is None:
        return redirect(url_for('login'))

    return render_template('add-product.html', user=user)


@app.route('/add-product', methods=['POST', 'GET'])
def add_product():
    user = check_login()
    if user is None:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return redirect(url_for('add_product_page'))
    else:
        title = request.form['title']
        category = request.form['category']
        price = request.form['price']
        description = request.form['description']

        # create product object
        product = Product(title=title, category=category,
                          price=price, description=description)
        db.session.add(product)
        db.session.commit()
        flash('{} added successfully.'.format(title))
        return redirect(url_for('home'))


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_product(id):
    user = check_login()
    if user is None:
        return redirect(url_for('login'))

    # check database for the product with that id.
    product = Product.query.filter(Product.id == id).one()
    if product is None:
        # if the product was not found send msg and redirect
        flash('Product not found')
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('edit.html', product=product)
    else:
        # update the product
        if request.form['title'] == '':
            flash('Please enter product title.')
            return render_template('edit.html', product=product)

        product.title = request.form['title']
        product.price = request.form['price']
        product.category = request.form['category']
        product.description = request.form['description']


        # upload image
        image = request.files['image']
        if image is None or image.filename is None:
            flash('Please select product image!')
            return render_template('edit.html')
            print(image.filename)
            filename = secure_filename(image.filename)
            picture.save(os.path.join('uploads', filename))
            image = filename
            product.image = filename

            db.session.commit()
            flash('Product updated successfully')
            return redirect(url_for('home'))



@app.route('/delete/<id>')
def delete_product(id):
    user = check_login()
    if user is None:
        return redirect(url_for('login'))

    # check database for the product with that id.
    product = Product.query.filter(Product.id == id).one()
    if product is None:
        # if the product was not found send msg and redirect
        flash('Product not found')
        return redirect(url_for('home'))
    else:
        db.session.delete(product)
        db.session.commit()
        flash('{} deleted successfully'.format(product.title))
        return redirect(url_for('home'))


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if username == '':
            flash('Please enter username!')
        elif password == '':
            flash('Please enter password')
        elif len(password) < 6:
            flash('Password must be more than 6 characters.')
        elif email == '':
            flash('Please enter email')
        else:
            exists = User.query.filter_by(email=email).first()
            if exists is not None:
                flash('Email address has been used for another account.')
                return render_template('signup.html')
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            user = User(username=username, email=email, password_hash=password_hash)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            session['email'] = email
            flash('Registration successful!')
            resp = redirect(url_for('home'))
            resp.set_cookie('id', str(user.id), max_age=timedelta(hours=24))
            resp.set_cookie('password', password_hash, max_age=timedelta(hours=24))
            print('USer id is', user.id)
            return resp
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        pw = hashlib.sha256(password.encode()).hexdigest()
        user = User.query.filter_by(email=email).first()
        if user is not None:
            if user.password_hash == pw:
                # logged in successfully
                session['username'] = user.username
                session['email'] = user.email
                resp = redirect(url_for('home'))
                resp.set_cookie('id', str(user.id), max_age=timedelta(hours=24))
                resp.set_cookie('password', pw, max_age=timedelta(hours=24))
                return resp
        flash('Invalid username or password!')
        return render_template('login.html')


@app.route('/logout')
def logout():
    # sessions
    session['username'] = None
    session['email'] = None
    # remove cookies
    resp = redirect(url_for('login'))
    resp.set_cookie('id', expires=0)
    resp.set_cookie('password', expires=0)
    return resp


@app.route('/uploads/<filename>')
def view_file(filename):
    return send_from_directory('static/uploads', filename)