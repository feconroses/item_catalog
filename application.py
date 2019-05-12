from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Create a session and connect to a database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Initiate flask app instance
app = Flask(__name__)

# Start of HTML endpoints
# Definining catalog home that shows all categories
@app.route('/')
@app.route('/catalog/')
def showCategories():
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	categories = session.query(Category).all()
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
		flash("New category created!")
		return redirect(url_for('showCategories'))
	else:
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
		flash("Category has been edited!")
		return redirect(url_for('showCategories'))
	else:
		return render_template('editcategory.html', category_id = category_id, item=editedCategory)

# Deleting an existing category
@app.route('/categories/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	deletedCategory = session.query(Category).filter_by(id=category_id).one()
	if request.method == 'POST':
		session.delete(deletedCategory)
		session.commit()
		flash("Category has been deleted!")
		return redirect(url_for('showCategories'))
	else:
		return render_template(
			'deletecategory.html', item=deletedCategory)

# Shows items within a category
@app.route('/categories/<int:category_id>')
@app.route('/restaurants/<int:category_id>/')
@app.route('/restaurants/<int:category_id>/all')
def showMenu(restaurant_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
	return render_template('menu.html', restaurant = restaurant, items = items)

# Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	# looks for a post request
	if request.method == 'POST':
		# extracts the name field from my form using request.form
		newItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id)
		session.add(newItem)
		session.commit()
		flash("new menu item created!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant_id = restaurant_id)

# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
			methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		session.add(editedItem)
		session.commit()
		flash("menu item has been edited!")
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		# USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
		# SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
		return render_template(
			'editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	deletedItem = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		flash("menu item has been deleted!")
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		# USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
		# SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
		return render_template(
			'deletemenuitem.html', item=deletedItem)

# Start of JSON endpoints
# Making an API Endpoint for Restaurants (Get Request)
@app.route('/restaurants/JSON')
def allRestaurantsJSON():
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants = [i.serialize for i in restaurants])

# Making an API Endpoint for Restaurant Menu (Get Request)
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
	return jsonify(RestaurantMenu = [i.serialize for i in items])

# Making an API Endpoint (Get Request)
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	item = session.query(MenuItem).filter_by(id=menu_id)
	return jsonify(MenuItem = [i.serialize for i in item])

if __name__ == '__main__':
	app.secret_key = 'super_secret_key' #this is for keeing sessions for showing a flash message
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)

