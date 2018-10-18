# flaskblog is the package name.
# app will be imported from the __init__.py file within that package.
from flaskblog import app

if __name__ == '__main__':
    app.run(debug=True)
