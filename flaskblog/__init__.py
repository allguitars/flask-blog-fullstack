from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '9c84f73a51cdafc0ad8eae0e5be9ac43'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
login_manager = LoginManager(app)
# Set the login route
login_manager.login_view = 'login'   # function name of the route
login_manager.login_message_category = 'info'  # Bootstrap class

# Create the database instance
db = SQLAlchemy(app)

# Create the instance for hashing
bcrypt = Bcrypt(app)

# For the app to run the routes properly, we need to import the routes, but we still
# need to be careful with the circular import problem.
# The routes.py is also importing the app. We can't import the routes at the top of
# this file because at that point, the app hasn't been created yet.
from flaskblog import routes
