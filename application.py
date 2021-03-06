from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   jsonify,
                   make_response,
                   session as login_session)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from functools import wraps
import random
import string
import httplib2
import json
import requests


"""
Create a session and connect to a database.
Using check_same_thread to avoid the exception thrown
because using the same DBSession
"""
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

# Initiate flask app instance
app = Flask(__name__)

# Start the DB session
DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    """Function decorator to avoid unautheticated users"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


# Start of HTML endpoints
# Categories
@app.route('/')
@app.route('/catalog')
@app.route('/catalog/')
def showCategories():
    """Definining catalog home that shows all categories"""
    categories = session.query(Category).all()

    # Show different if user is logged in
    if 'username' not in login_session:
        return render_template('publiccategories.html', categories=categories)
    else:
        return render_template('categories.html', categories=categories)


@app.route('/categories/new', methods=['GET', 'POST'])
@login_required
def newCategory():
    """Adding a new category"""
    # Looks for a post request
    if request.method == 'POST':
        # Checks the creator information
        user_id = getUserId(login_session['email'])

        # Extracts the name field from my form using request.form
        newCategory = Category(name=request.form['name'], user_id=user_id)
        session.add(newCategory)
        session.commit()
        flash("New category created!")
        return redirect(url_for('showCategories'))

    # If it's a get request
    else:
        return render_template('newcategory.html')


@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """Editing an existing category"""
    # Get the category information
    editedCategory = (session.query(Category).
                      filter_by(id=category_id).one_or_none())

    # Looks for a post request
    if request.method == 'POST':

        # Checks if the user is the owner of the item
        user_id = getUserId(login_session['email'])
        if user_id == editedCategory.user_id:

            # Performs the edit action
            if request.form['name']:
                editedCategory.name = request.form['name']
            session.add(editedCategory)
            session.commit()
            flash("Category has been edited!")
            return redirect(url_for('showCategories'))

        # User is not the owner of the category
        else:
            flash("You don't have authorization to edit this category!")
            return redirect(url_for('showCategories'))

    # If it's a get request
    else:
        return render_template('editcategory.html',
                               category_id=category_id,
                               category=editedCategory)


@app.route('/categories/<int:category_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    """Deleting an existing category"""
    # Get the category information
    deletedCategory = (session.query(Category)
                       .filter_by(id=category_id).one_or_none())

    # Looks for a post request
    if request.method == 'POST':

        # Checks if the user is the owner of the item
        user_id = getUserId(login_session['email'])
        if user_id == deletedCategory.user_id:

            # Performs the delete action
            session.delete(deletedCategory)
            session.commit()
            flash("Category has been deleted!")
            return redirect(url_for('showCategories'))

        # User is not the owner of the category
        else:
            flash("You don't have authorization to delete this category!")
            return redirect(url_for('showCategories'))

    # If it's a get request
    else:
        return render_template(
            'deletecategory.html', category=deletedCategory)


# Items
@app.route('/categories/<int:category_id>')
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/all')
def showCategory(category_id):
    """Shows items within a category"""
    # Get the category and item information
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    items = session.query(CategoryItem).filter_by(category_id=category.id)

    # Show different if user is logged in
    if 'username' not in login_session:
        return render_template('publicitems.html',
                               category=category, items=items)
    else:
        return render_template('items.html', category=category, items=items)


@app.route('/categories/<int:category_id>/new', methods=['GET', 'POST'])
@login_required
def newCategoryItem(category_id):
    """Create new items for category"""
    # Get the item information
    newItemCategory = (session.query(Category)
                       .filter_by(id=category_id).one_or_none())

    # Looks for a post request
    if request.method == 'POST':

        # checks the creator information
        user_id = getUserId(login_session['email'])

        # extracts the name field from my form using request.form
        newItem = CategoryItem(name=request.form['name'],
                               description=request.form['description'],
                               category_id=category_id,
                               user_id=user_id)
        session.add(newItem)
        session.commit()
        flash("New category item created!")
        return redirect(url_for('showCategory', category_id=category_id))

    # If it's a get request
    else:
        return render_template('newcategoryitem.html',
                               category_id=category_id,
                               category=newItemCategory)


@app.route('/categories/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editCategoryItem(category_id, item_id):
    """Edit items in category"""
    # Get the category and item information
    editItemCategory = (session.query(Category)
                        .filter_by(id=category_id).one_or_none())
    editedItem = (session.query(CategoryItem)
                  .filter_by(id=item_id).one_or_none())

    # Looks for a post request
    if request.method == 'POST':

        # Checks if the user is the owner of the item
        user_id = getUserId(login_session['email'])
        if user_id == editedItem.user_id:

            # Performs the edit action
            if request.form['name']:
                editedItem.name = request.form['name']
            if request.form['description']:
                editedItem.description = request.form['description']
            session.add(editedItem)
            session.commit()
            flash("Category item has been edited!")
            return redirect(url_for('showCategory', category_id=category_id))

        # User is not the owner of the item
        else:
            flash("You don't have authorization to edit this item!")
            return redirect(url_for('showCategory', category_id=category_id))

    # If it's a get request
    else:
        return render_template(
            'editcategoryitem.html', category_id=category_id,
            item_id=item_id, item=editedItem, category=editItemCategory)


@app.route('/categories/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteCategoryItem(category_id, item_id):
    """Delete a category item"""
    # Get the category and item information
    delItemCategory = session.query(Category).filter_by(id=category_id).one()
    deletedItem = session.query(CategoryItem).filter_by(id=item_id).one()

    # Looks for a post request
    if request.method == 'POST':

        # Checks if the user is the owner of the item
        user_id = getUserId(login_session['email'])
        if user_id == deletedItem.user_id:

            # Performs the delete action
            session.delete(deletedItem)
            session.commit()
            flash("Category item has been deleted!")
            return redirect(url_for('showCategory', category_id=category_id))

        # User is not the owner of the item
        else:
            flash("You don't have authorization to delete this item!")
            return redirect(url_for('showCategory', category_id=category_id))

    # If it's a get request
    else:
        return render_template(
            'deletecategoryitem.html', item=deletedItem,
            category=delItemCategory)


# Start of JSON endpoints
@app.route('/categories/JSON')
def allCategoriesJSON():
    """Making an API Endpoint for getting all the categories"""
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/categories/<int:category_id>/JSON')
def categoryItemsJSON(category_id):
    """Making an API Endpoint for seeing items in a category"""
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    items = session.query(CategoryItem).filter_by(category_id=category.id)
    return jsonify(CategoryItems=[i.serialize for i in items])


@app.route('/categories/<int:category_id>/<int:item_id>/JSON')
def categoryItemJSON(category_id, item_id):
    """Making an API Endpoint for seeing info about a particular item"""
    item = session.query(CategoryItem).filter_by(id=category_id)
    return jsonify(CategoryItem=[i.serialize for i in item])


# Next: the code for login/logout users
# Declaring Client ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """Store state token in the session for later validation"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))

    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


# Functions for user management
def createUser(login_session):
    """Helper function for creating user"""
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit
    user = (session.query(User)
            .filter_by(email=login_session['email']).one_or_none())
    return user.id


def getUserInfo(user_id):
    """Helper function for getting the user information"""
    user = session.query(User).filter_by(id=user_id).one_or_none()
    return user


def getUserId(email):
    """Helper function for getting the user ID"""
    try:
        user = session.query(User).filter_by(email=email).one_or_none()
        if user:
            return user.id
        else:
            return None
    except ImportError:
        return None


# Functions for login, logout
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Endpoint for login using Google"""
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
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
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

    login_session['username'] = data.get('name', '')
    login_session['picture'] = data.get('picture', '')
    login_session['email'] = data.get('email', '')
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
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


@app.route('/disconnect')
def disconnect():
    """Disconnect - Revoke a current user's token
    and reset their login_session"""
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


@app.route("/gdisconnect")
def gdisconnect():
    """Disconnect a login session from Google"""
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
        response = make_response(json.dumps
                                 ('Failed to revoke token for given user.',
                                  400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    # This is for keeping sessions for showing a flash message
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
