########################################################
# Sample customers blueprint of endpoints
# Remove this file if you are not using it in your project
########################################################

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of 
# routes.
tech_support_analyst = Blueprint('tech_support_analyst', __name__)

#------------------------------------------------------------
# Get all the products from the database, package them up,
# and return them to the client
@tech_support_analyst.route('/tickets', methods=['GET'])
def get_tickets():
    query = '''
        SELECT  TicketID, 
                UserID, 
                IssueType, 
                Status, 
                Priority,
                ReceivedDate,
                ResolvedDate 
        FROM ticket
    '''
    
    # get a cursor object from the database
    cursor = db.get_db().cursor()

    # use cursor to query the database for a list of products
    cursor.execute(query)

    # fetch all the data from the cursor
    # The cursor will return the data as a 
    # Python Dictionary
    theData = cursor.fetchall()

    # Create a HTTP Response object and add results of the query to it
    # after "jasonify"-ing it.
    response = make_response(jsonify(theData))
    # set the proper HTTP Status code of 200 (meaning all good)
    response.status_code = 200
    # send the response back to the client
    return response

# ------------------------------------------------------------
# get product information about a specific product
# notice that the route takes <id> and then you see id
# as a parameter to the function.  This is one way to send 
# parameterized information into the route handler.
@tech_support_analyst.route('/product/<id>', methods=['GET'])
def get_product_detail (id):

    query = f'''SELECT id, 
                       product_name, 
                       description, 
                       list_price, 
                       category 
                FROM products 
                WHERE id = {str(id)}
    '''
    
    # logging the query for debugging purposes.  
    # The output will appear in the Docker logs output
    # This line has nothing to do with actually executing the query...
    # It is only for debugging purposes. 
    current_app.logger.info(f'GET /product/<id> query={query}')

    # get the database connection, execute the query, and 
    # fetch the results as a Python Dictionary
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    
    # Another example of logging for debugging purposes.
    # You can see if the data you're getting back is what you expect. 
    current_app.logger.info(f'GET /product/<id> Result of query = {theData}')
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response
    
# ------------------------------------------------------------
# Get the top 5 most expensive products from the database
@products.route('/mostExpensive')
def get_most_pop_products():

    query = '''
        SELECT product_code, 
               product_name, 
               list_price, 
               reorder_level
        FROM products
        ORDER BY list_price DESC
        LIMIT 5
    '''
    
    # Same process as handler above
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
 
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# Route to get the 10 most expensive items from the 
# database.
@products.route('/tenMostExpensive', methods=['GET'])
def get_10_most_expensive_products():
    
    query = '''
        SELECT product_code, 
               product_name, 
               list_price, 
               reorder_level
        FROM products
        ORDER BY list_price DESC
        LIMIT 10
    '''
    
    # Same process as above
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response
    

# ------------------------------------------------------------
# This is a POST route to add a new product.
# Remember, we are using POST routes to create new entries
# in the database. 
@tech_support_analyst.route('/chats', methods=['POST'])
def add_new_chats():
    
    # In a POST request, there is a 
    # collecting data from the request object 
    the_data = request.json
    current_app.logger.info(the_data)

    #extracting the variable
    name = the_data['product_name']
    content = the_data['chat_content']
    time = the_data['chat_time']
    category = the_data['product_category']
    
    query = f'''
        INSERT INTO products (product_name,
                              description,
                              category, 
                              list_price)
        VALUES ('{name}', '{content}', '{category}', {str(time)})
    '''
    # TODO: Make sure the version of the query above works properly
    # Constructing the query
    # query = 'insert into products (product_name, description, category, list_price) values ("'
    # query += name + '", "'
    # query += description + '", "'
    # query += category + '", '
    # query += str(price) + ')'
    current_app.logger.info(query)

    # executing and committing the insert statement 
    cursor = db.get_db().cursor()
    cursor.execute(query)
    db.get_db().commit()
    
    response = make_response("Successfully initiated chat")
    response.status_code = 200
    return response

# ------------------------------------------------------------
### Get all product categories
@products.route('/categories', methods = ['GET'])
def get_all_categories():
    query = '''
        SELECT DISTINCT category AS label, category as value
        FROM products
        WHERE category IS NOT NULL
        ORDER BY category
    '''

    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
        
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# This is a stubbed route to update a log in the catalog
# The SQL query would be an UPDATE. 
@tech_support_analyst.route('/logs/{user_id}', methods = ['PUT'])
def update_logs():
    logs_info = request.json
    if not logs_info:
        return {"error": "Invalid JSON payload"}, 400
    current_app.logger.info(f"Updating logs for user {user_id}: {logs_info}")
    return {"message": "Logs updated successfully"}, 200

# -------------------------------------------------------------
# This is a DELETE statement 
@tech_support_analyst.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def archive_ticket(ticket_id):
    ticket = TicketModel.query.filter_by(id=ticket_id, status="completed").first()
    if not ticket:
        return {"error": "Ticket not found or not completed"}, 404
    db.session.delete(ticket)
    db.session.commit()

    return {"message": "Ticket archived successfully"}, 200