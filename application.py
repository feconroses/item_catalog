from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User

# Imports for creating a visitor session
from flask import session as login_session
import random, string

# Imports for the GConnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Create a session and connect to a database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Initiate flask app instance
app = Flask(__name__)

# Start of HTML endpoints

# Categories
# Definining catalog home that shows all categories
@app.route('/')
@app.route('/catalog')
@app.route('/catalog/')
def showCategories():
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	categories = session.query(Category).all()
	session.close()

	# Show different if user is logged in
	if 'username' not in login_session:
		return render_template('publiccategories.html', categories = categories)
	else: 
		return render_template('categories.html', categories = categories)

# Adding a new category
@app.route('/categories/new', methods=['GET', 'POST'])
def newCategory():
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	# looks for a post request
	if request.method == 'POST':
		# extracts the name field from my form using request.form
		newCategory = Category(name = request.form['name'])
		session.add(newCategory)
		session.commit()
		session.close()
		flash("New category created!")
		return redirect(url_for('showCategories'))
	else:
		session.close()
		return render_template('newcategory.html')

# Editing an existing category
@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	editedCategory = session.query(Category).filter_by(id=category_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedCategory.name = request.form['name']
		session.add(editedCategory)
		session.commit()
		session.close()
		flash("Category has been edited!")
		return redirect(url_for('showCategories'))
	else:
		session.close()
		return render_template('editcategory.html', category_id = category_id, category = editedCategory)

# Deleting an existing category
@app.route('/categories/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	deletedCategory = session.query(Category).filter_by(id = category_id).one()
	if request.method == 'POST':
		session.delete(deletedCategory)
		session.commit()
		session.close()
		flash("Category has been deleted!")
		return redirect(url_for('showCategories'))
	else:
		session.close()
		return render_template(
			'deletecategory.html', category = deletedCategory)

# Items
# Shows items within a category
@app.route('/categories/<int:category_id>')
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/all')
def showCategory(category_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(CategoryItem).filter_by(category_id = category.id)
	session.close()

	# Show different if user is logged in
	if 'username' not in login_session:
		return render_template('publicitems.html', category = category, items = items)
	else: 
		return render_template('items.html', category = category, items = items)

# Create new items for category
@app.route('/categories/<int:category_id>/new', methods=['GET', 'POST'])
def newCategoryItem(category_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	# looks for a post request
	newItemCategory = session.query(Category).filter_by(id = category_id).one()
	if request.method == 'POST':
		# extracts the name field from my form using request.form
		newItem = CategoryItem(name = request.form['name'], description = request.form['description'], category_id = category_id)
		session.add(newItem)
		session.commit()
		session.close()
		flash("New category item created!")
		return redirect(url_for('showCategory', category_id = category_id))
	else:
		session.close()
		return render_template('newcategoryitem.html', category_id = category_id, category = newItemCategory)

# Edit items in category
@app.route('/categories/<int:category_id>/<int:item_id>/edit',
			methods=['GET', 'POST'])
def editCategoryItem(category_id, item_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	editedItemCategory = session.query(Category).filter_by(id = category_id).one()
	editedItem = session.query(CategoryItem).filter_by(id = item_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['description']:
			editedItem.description = request.form['description']
		session.add(editedItem)
		session.commit()
		session.close()
		flash("Category item has been edited!")
		return redirect(url_for('showCategory', category_id = category_id))
	else:
		session.close()
		return render_template(
			'editcategoryitem.html', category_id = category_id, item_id = item_id, item = editedItem, category = editedItemCategory)

# Delete a category item
@app.route('/categories/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(category_id, item_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	deletedItemCategory = session.query(Category).filter_by(id = category_id).one()
	deletedItem = session.query(CategoryItem).filter_by(id =  item_id).one()
	if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		flash("Category item has been deleted!")
		session.close()
		return redirect(url_for('showCategory', category_id = category_id))
	else:
		session.close()
		return render_template(
			'deletecategoryitem.html', item = deletedItem, category = deletedItemCategory)

# Start of JSON endpoints
# Making an API Endpoint for getting all the categories (Get Request)
@app.route('/categories/JSON')
def allCategoriesJSON():
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	categories = session.query(Category).all()
	session.close()
	return jsonify(Categories = [i.serialize for i in categories])

# Making an API Endpoint for seeing items in a category (Get Request)
@app.route('/categories/<int:category_id>/JSON')
def categoryItemsJSON(category_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(CategoryItem).filter_by(category_id = category.id)
	session.close()
	return jsonify(CategoryItems = [i.serialize for i in items])

# Making an API Endpoint for seeing info about a particular item (Get Request)
@app.route('/categories/<int:category_id>/<int:item_id>/JSON')
def categoryItemJSON(category_id, item_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	item = session.query(CategoryItem).filter_by(id=category_id)
	session.close()
	return jsonify(CategoryItem = [i.serialize for i in item])

# Next: the code for login/logout users

# Declaring Client ID
CLIENT_ID = json.loads(
  open('client_secrets.json', 'r').read())['web']['client_id']

# Create anti-forgery state token
# #Store it in the session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)for x in range(32))

    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

def createUser(login_session):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit
    user = session.query(User).filter_by(email = login_session['email']).one()
    session.close()
    return user.id

def getUserInfo(user_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    user = session.query(User).filter_by(id = user_id).one()
    session.close()
    return user

def getUserId(email):
    try:
        DBSession = sessionmaker(bind=engine)
        session = DBSession()

        user = session.query(User).filter_by(email = email).one()
        session.close()
        return user.id
    except:
        return None

# Endpoint for login using Google
@app.route('/gconnect', methods = ['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserId(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# Disconnect - Revoke a current user's token and reset their login_session.
@app.route("/gdisconnect")
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in to begin with!")
        redirect(url_for('showCategories'))


if __name__ == '__main__':
	app.secret_key = 'super_secret_key' #this is for keeping sessions for showing a flash message
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)

