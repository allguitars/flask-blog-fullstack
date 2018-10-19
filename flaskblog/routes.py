import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog.models import User, Post
# To login the user
from flask_login import login_user, current_user, logout_user, login_required

# dummy data
posts = [
    {
        'author': 'Neo Li',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'October 13, 2018'
    },
    {
        'author': 'Jane doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'October 14, 2018'
    }
]


@app.route('/')
@app.route('/home')
def home():
    # You can the second argument wahtever you want.
    # The name will be used in the template as a variable name.
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Create an instance for the form with the class we have defined
    form = RegistrationForm()
    # Check validation
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Create an instance for the form with the class we have defined
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # If we are trying to restricted page before we are logged in, then we
            # should be redirected to that page after we are logged in.
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    # It doesn't take any arguments because it already knows what user is
    # logged in.
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)

    # Resize the image before we save it
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # Check if there is any picture data. We have to make this check
        # because that's not a required field.
        if form.picture.data:
            # Save the image to the profile_pics folder and get the image path
            picture_file = save_picture(form.picture.data)
            # Ser the current user's image to that picture file
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')

        # Invoke a GET request on account route
        return redirect(url_for('account'))

    # Show the current_user's values before the user attempts to change
    # something.
    elif request.method == 'GET':
        # Populate the fields with our current user's data
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static',
                         filename='profile_pics/' + current_user.image_file)

    # The condition when this route is requested with GET method
    return render_template('account.html', title='Account', image_file=image_file,
                           form=form)
