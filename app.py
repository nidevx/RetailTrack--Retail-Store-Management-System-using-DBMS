from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'simple-retail-store'

# Database configuration - UPDATE THESE WITH YOUR MYSQL DETAILS
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         
    'password': 'shan',      
    'database': 'simple_retail_store'
}

def get_db_connection():
    '''Get database connection'''
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database error: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    '''Execute database query'''
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.rowcount

        return result
    except Error as e:
        print(f"Query error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    '''Single page with all functionality'''

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # --- EXISTING ADD PRODUCT ---
        if form_type == 'add_product':
            name = request.form.get('product_name')
            price = request.form.get('price')
            stock = request.form.get('stock_quantity')
            query = "INSERT INTO products (product_name, price, stock_quantity) VALUES (%s, %s, %s)"
            execute_query(query, (name, price, stock))
            flash('Product added!', 'success')

        # --- EXISTING ADD CUSTOMER ---
        elif form_type == 'add_customer':
            name = request.form.get('customer_name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            query = "INSERT INTO customers (customer_name, phone, email) VALUES (%s, %s, %s)"
            execute_query(query, (name, phone, email))
            flash('Customer added!', 'success')

        # --- NEW: EDIT PRODUCT ---
        elif form_type == 'edit_product':
            p_id = request.form.get('product_id')
            name = request.form.get('product_name').strip()
            price = request.form.get('price')
            
            if not name or float(price) < 0:
                flash('Invalid data! Name is required and price cannot be negative.', 'error')
            else:
                query = "UPDATE products SET product_name = %s, price = %s WHERE product_id = %s"
                execute_query(query, (name, price, p_id))
                flash('Product updated successfully!', 'success')

        # --- NEW: DELETE PRODUCT ---
        elif form_type == 'delete_product':
            p_id = request.form.get('product_id')
            result = execute_query("DELETE FROM products WHERE product_id = %s", (p_id,))
            if result:
                flash('Product deleted!', 'success')
            else:
                flash('Error: Cannot delete product (it might be linked to past sales).', 'error')

        # --- NEW: EDIT CUSTOMER ---
        elif form_type == 'edit_customer':
            c_id = request.form.get('customer_id')
            name = request.form.get('customer_name').strip()
            phone = request.form.get('phone')
            email = request.form.get('email')

            if not name:
                flash('Customer name is required!', 'error')
            else:
                query = "UPDATE customers SET customer_name = %s, phone = %s, email = %s WHERE customer_id = %s"
                execute_query(query, (name, phone, email, c_id))
                flash('Customer updated!', 'success')

        # --- NEW: DELETE CUSTOMER ---
        elif form_type == 'delete_customer':
            c_id = request.form.get('customer_id')
            result = execute_query("DELETE FROM customers WHERE customer_id = %s", (c_id,))
            if result:
                flash('Customer deleted!', 'success')
            else:
                flash('Error: Cannot delete customer (linked to past sales).', 'error')

        # --- NEW: DELETE SALE ---
        elif form_type == 'delete_sale':
            sale_id = request.form.get('sale_id')
            sale_data = execute_query("SELECT product_id, quantity_sold FROM sales WHERE sale_id = %s", (sale_id,), fetch=True)
            
            if sale_data:
                p_id = sale_data[0]['product_id']
                qty = sale_data[0]['quantity_sold']
                execute_query("UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s", (qty, p_id))
                execute_query("DELETE FROM sales WHERE sale_id = %s", (sale_id,))
                flash(f'Sale #{sale_id} deleted and stock restored!', 'success')
            else:
                flash('Error: Sale record not found.', 'error')

        # --- EXISTING MAKE SALE ---
        elif form_type == 'make_sale':
            c_id = request.form.get('customer_id')
            p_id = request.form.get('product_id')
            qty = int(request.form.get('quantity'))

            prod = execute_query("SELECT * FROM products WHERE product_id = %s", (p_id,), fetch=True)
            if prod and prod[0]['stock_quantity'] >= qty:
                total = prod[0]['price'] * qty
                execute_query("UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s", (qty, p_id))
                execute_query("INSERT INTO sales (customer_id, product_id, quantity_sold, total_amount) VALUES (%s, %s, %s, %s)", 
                              (c_id, p_id, qty, total))
                flash(f'Sale completed! Total: ₹{total:.2f}', 'success')
            else:
                flash('Insufficient stock!', 'error')

        return redirect(url_for('index'))

    # --- HANDLING SORTING PARAMETERS ---
    # Product Sorting
    p_sort = request.args.get('p_sort', 'product_name')
    p_order = request.args.get('p_order', 'ASC')
    allowed_p_cols = ['product_name', 'price', 'stock_quantity', 'created_at']
    if p_sort not in allowed_p_cols: p_sort = 'product_name'
    products = execute_query(f"SELECT * FROM products ORDER BY {p_sort} {p_order}", fetch=True) or []

    # Customer Sorting
    c_sort = request.args.get('c_sort', 'customer_name')
    c_order = request.args.get('c_order', 'ASC')
    allowed_c_cols = ['customer_name', 'created_at']
    if c_sort not in allowed_c_cols: c_sort = 'customer_name'
    customers = execute_query(f"SELECT * FROM customers ORDER BY {c_sort} {c_order}", fetch=True) or []

    # Sales Sorting
    s_sort = request.args.get('s_sort', 'sale_date')
    s_order = request.args.get('s_order', 'DESC')
    allowed_s_cols = ['sale_id', 'quantity_sold', 'total_amount', 'sale_date']
    if s_sort not in allowed_s_cols: s_sort = 'sale_date'
    
    sales_query = f'''
        SELECT s.sale_id, c.customer_name, p.product_name, s.quantity_sold, 
               s.total_amount, s.sale_date
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN products p ON s.product_id = p.product_id
        ORDER BY s.{s_sort} {s_order}
        LIMIT 20
    '''
    sales = execute_query(sales_query, fetch=True) or []

    return render_template('index.html', 
                         products=products, 
                         customers=customers, 
                         sales=sales,
                         p_sort=p_sort, p_order=p_order,
                         c_sort=c_sort, c_order=c_order,
                         s_sort=s_sort, s_order=s_order)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)