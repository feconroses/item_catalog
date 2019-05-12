from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

# Create a session and connect to a database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Initiate flask app instance
app = Flask(__name__)

# Start of HTML endpoints

# Categories
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
		flash("Category has been deleted!")
		return redirect(url_for('showCategories'))
	else:
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
	return render_template('items.html', category = category, items = items)

# Create new items for category
@app.route('/categories/<int:category_id>/new', methods=['GET', 'POST'])
def newCategoryItem(category_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	# looks for a post request
	if request.method == 'POST':
		# extracts the name field from my form using request.form
		newItem = CategoryItem(name = request.form['name'], description = request.form['description'], category_id = category_id)
		session.add(newItem)
		session.commit()
		flash("New category item created!")
		return redirect(url_for('showCategory', category_id = category_id))
	else:
		return render_template('newcategoryitem.html', category_id = category_id)

# Edit items in category
@app.route('/categories/<int:category_id>/<int:item_id>/edit',
			methods=['GET', 'POST'])
def editCategoryItem(category_id, item_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	editedItem = session.query(CategoryItem).filter_by(id = item_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['description']:
			editedItem.description = request.form['description']
		session.add(editedItem)
		session.commit()
		flash("Category item has been edited!")
		return redirect(url_for('showCategory', category_id = category_id))
	else:
		return render_template(
			'editcategoryitem.html', category_id = category_id, item_id = item_id, item = editedItem)

# Delete a category item
@app.route('/categories/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(category_id, item_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	deletedItem = session.query(CategoryItem).filter_by(id =  item_id).one()
	if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		flash("Category item has been deleted!")
		return redirect(url_for('showCategory', category_id = category_id))
	else:
		return render_template(
			'deletecategoryitem.html', item = deletedItem)

# Start of JSON endpoints
# Making an API Endpoint for getting all the categories (Get Request)
@app.route('/categories/JSON')
def allCategoriesJSON():
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	categories = session.query(Category).all()
	return jsonify(Categories = [i.serialize for i in categories])

# Making an API Endpoint for seeing items in a category (Get Request)
@app.route('/categories/<int:category_id>/JSON')
def categoryItemsJSON(category_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(CategoryItem).filter_by(category_id = category.id)
	return jsonify(CategoryItems = [i.serialize for i in items])

# Making an API Endpoint for seeing info about a particular item (Get Request)
@app.route('/categories/<int:category_id>/<int:item_id>/JSON')
def categoryItemJSON(category_id, item_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	item = session.query(CategoryItem).filter_by(id=category_id)
	return jsonify(CategoryItem = [i.serialize for i in item])

if __name__ == '__main__':
	app.secret_key = 'super_secret_key' #this is for keeping sessions for showing a flash message
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)

