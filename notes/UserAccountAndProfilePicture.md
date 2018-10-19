# User Account and Profile Picture

## Adding Profile Picture Path

In _routes.py_
```python
@app.route('/account')
@login_required
def account():
    # ---------- added ----------
    # In the User model, image_file has a default filename
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    # ---------------------------
    return render_template('account.html', title='Account', image_file=image_file)

```

Modified _account.html_
```html
{% extends "layout.html" %}
{% block content %}
	<div class="content-section">
		<div class="media">
			<img class="rounded-circle account-img" src="{{ image_file }}">
			<div class="media-body">
				<h2 class="account-heading">{{ current_user.username }}</h2>
				<p class="text-secondary">{{ current_user.email }}</p>
			</div>
		</div>
		<!-- FORM HERE -->
	</div>
{% endblock content %}
```
## Adding a Form to Update Account Information
Within the Account page, we also want to be able to to update our username email address and also upload a custom profile picture so we need to create forms for that.

_forms.py_
```python
...
from flask_login import current_user

...

# Add a new form for uclass RegistrationForm(FlaskForm):
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
    	
    	# If the user enters a username that is different from the current one.
    	if username.data != current_user.username:
    		
    		# Then check if the new username is already taken 
	        user = User.query.filter_by(username=username.data).first()
	        
	        if user:  # If it already exists
	            raise ValidationError(
	                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
    	if email.data != current_user.email:
	        user = User.query.filter_by(email=email.data).first()
	        if user:
	            raise ValidationError(
	                'That e-mail is taken. Please choose a different one.')
```
In _routes.py_, we need to include the new form:
```python
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm

...


@app.route('/account')
@login_required
def account():
    # Create an instance of that form
    form = UpdateAccountForm()

    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)

    # Pass in the form to the template
    return render_template('account.html', title='Account', image_file=image_file, form=form)
```
Insert the form with username and email fields into _account.html_
```html
{% extends "layout.html" %}
{% block content %}
	<div class="content-section">
		<div class="media">
			<img class="rounded-circle account-img" src="{{ image_file }}">
			<div class="media-body">
				<h2 class="account-heading">{{ current_user.username }}</h2>
				<p class="text-secondary">{{ current_user.email }}</p>
			</div>
		</div>
		<form method="POST" action="">
			{{ form.hidden_tag() }}  <!-- Adding CSRF token -->
			<fieldset class="form-group">
				<legend class="border-bottom mb-4">Account Info</legend>
				<div class="form-group">
					{{ form.username.label(class="form-control-label") }}
					{% if form.username.errors %}
						{{ form.username(class="form-control form-control-lg is-invalid") }}
						<div class="invalid-feedback">
							{% for error in form.username.errors %}
								<span>{{ error }}</span>
							{% endfor %}
						</div>
					{% else %}
						{{ form.username(class="form-control form-control-lg") }}
					{% endif %}
				</div>
				<div class="form-group">
					{{ form.email.label(class="form-control-label") }}
					{% if form.email.errors %}
						{{ form.email(class="form-control form-control-lg is-invalid") }}
						<div class="invalid-feedback">
							{% for error in form.email.errors %}
								<span>{{ error }}</span>
							{% endfor %}
						</div>
					{% else %}
						{{ form.email(class="form-control form-control-lg") }}
					{% endif %}
				</div>
			</fieldset>
			<div class="form-group">
				{{ form.submit(class="btn btn-outline-info") }}
			</div>
		</form>
	</div>
{% endblock content %}
```
## Showing Current User's Information
It would be nice that the Account Info form can show the user's current data, and we need to also implement the POST and GET methods so the route knows where to redirect after the user submits the form.

_routs.py_
```python
...

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # We can simply change the values of our current_user variable and then
        # commit those.
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        # Tells the user that the account information has been updated.
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
```
## Adding FileField to the Form
To allow the user to change the profile picture, we will need to add a new filed to our form that has an input type of "file".

_forms.py_
```python
...
from flask_wtf.file import FileField, FileAllowed

...

class UpdateAccountForm(FlaskForm):
    ...
    
    picture = FileField('Update Profile Picure', validators=[
                        FileAllowed(['jpg', 'png'])])
    ...

```
Upate the template for the FileField:

Note that we need to add a **special encoding type** to our form. We have to do this in order for our form to pass our image data properly. Be sure you put that in because **the errors aren't entirely obvious if you forget to do this.**

_account.html_
```html
...

	<form method="POST" action="" enctype="multipart/form-data">

...

		<div class="form-group">
			{{ form.picture.label() }}
			{{ form.picture(class="form-control-file") }}
			{% if form.picture.errors %}
				{% for error in form.picture.errors %}
					<span class="text-danger">{{ error }}</span><br>
				{% endfor %}
			{% endif %}
		</div>

...

```
## Using OS Module
Now let's add the logic to our route to actually save this profile picture for our user.

_routs.py_
```python
import os
import secrets

...

def save_picture(form_picture):
    # We don't want to keep the name of the file that they uploaded because it
    # might collide with the name of the image that's already in our folder.
    # Randomize the name of this image:
    random_hex = secrets.token_hex(8)  # eight bytes

    # Grab the file extension with os module
    # Use underscore because we won't be using the returned value filename.
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    # Use root_path attribute of app to get the root path of this project
    picture_path = os.path.join( app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
    	# ---------------------- Added ----------------------
        
        # Check if there is any picture data. We have to make this check
        # because that's not a required field.
        if form.picture.data:
            # Save the image to the profile_pics folder and get the image path
            picture_file = save_picture(form.picture.data)
            
            # Ser the current user's image to that picture file
            current_user.image_file = picture_file

        # ---------------------------------------------------

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')

    ...

```

## Resize Images
The largest image on our site right now is just set in CSS to 125 pixels so there would be no use in having 4000-pixel that just gets scaled down to 125 pixels in CSS. Let's resize the images before they actually get saved to the file system. We are going to be using a package called **Pillow**. 

- Install the package
```
$ pip install Pillow
```
_routes.py_
```python
from PIL import Image

...

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)

    # ------------------ Added------------------
    # Resize the image before we save it
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    # ------------------------------------------

    return picture_fn
```


