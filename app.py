from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import mysql.connector
app = Flask(__name__)

db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="dbchat"
)
    # Create a cursor object to execute queries
cursor = db_connection.cursor()

model_path = 'gaussalgo/T5-LM-Large-text2sql-spider'
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

prompt = """
you are a bot to assist in creating MySQL commands, all your answers should start with \
this is your MySQL, and after that MySQL that can do what the user requests. \
Give the answer relevant to the schema only, otherwise prompt "Irrelevant query". \
Generate the queries containing the columns strictly present in the schema, otherwise prompt "Error!". \
Try to maintain the MySQL order simple. \
Put the MySQL command in white letters with a black background, and just after \
a simple and concise text explaining how it works. \
If the user asks for something that cannot be solved with a MySQL Order, \
just answer something nice and simple, maximum 10 words, asking him for something that \
can be solved with MySQL.
When receiving a request, begin the response with "This is your SQL:". Follow with an SQL command that fulfills the user's specified need, presented in white text on a black background. Directly after, offer a concise explanation of how the command works, tailored for users with basic SQL knowledge.

Ensure SQL commands accurately handle data types, especially boolean values, which should only use 'TRUE' or 'FALSE'. If a user's query is not solvable by SQL, respond politely, urging a SQL-solvable question, limited to 10 words.

Keep SQL commands simple for ease of understanding and execution. This ensures that the commands are accessible and executable by users with basic MySQL knowledge, avoiding complex syntax or advanced features unless specifically requested by the user.
The boolean values have the values either T or F. T means True and F means False.
"""

schema = """
CREATE TABLE products (
  product_id INTEGER PRIMARY KEY, -- Unique ID for each product
  name VARCHAR(50), -- Name of the product
  price DECIMAL(10,2), -- Price of each unit of the product
  quantity INTEGER  -- Current quantity in stock
);

CREATE TABLE customers (
   customer_id INTEGER PRIMARY KEY, -- Unique ID for each customer
   name VARCHAR(50), -- Name of the customer
   address VARCHAR(100) -- Mailing address of the customer
);

CREATE TABLE salespeople (
  salesperson_id INTEGER PRIMARY KEY, -- Unique ID for each salesperson 
  name VARCHAR(50), -- Name of the salesperson
  region VARCHAR(50) -- Geographic sales region 
);

CREATE TABLE sales (
  sale_id INTEGER PRIMARY KEY, -- Unique ID for each sale
  product_id INTEGER, -- ID of product sold
  customer_id INTEGER,  -- ID of customer who made purchase
  salesperson_id INTEGER, -- ID of salesperson who made the sale
  sale_date DATE, -- Date the sale occurred 
  quantity INTEGER -- Quantity of product sold
);

CREATE TABLE product_suppliers (
  supplier_id INTEGER PRIMARY KEY, -- Unique ID for each supplier
  product_id INTEGER, -- Product ID supplied
  supply_price DECIMAL(10,2) -- Unit price charged by supplier
);

-- sales.product_id can be joined with products.product_id
-- sales.customer_id can be joined with customers.customer_id 
-- sales.salesperson_id can be joined with salespeople.salesperson_id
-- product_suppliers.product_id can be joined with products.product_id

"""

@app.route('/')
def index():
    return render_template('index.html', prompt=prompt)

@app.route('/query', methods=['POST'])
def query():
    user_question = request.json['user_question']
    input_text = f"Question: {user_question}\n{prompt}\nSchema:{schema}"
    model_inputs = tokenizer(input_text, return_tensors="pt")
    outputs = model.generate(**model_inputs, max_length=542)
    sql_query = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    # print(sql_query)

    # Example query
    query = sql_query

    # Execute the query with parameters
    cursor.execute(query)

    # Fetch all rows from the result
    result = cursor.fetchall()
    # Format result for display
    # formatted_result = [str(row) for row in result]

    # return jsonify({'sql_query': sql_query, 'result': formatted_result})
    return jsonify({'sql_query': sql_query, 'result':result})
    # return jsonify({'sql_query': sql_query})

if __name__ == '__main__':
    app.run(debug=True)