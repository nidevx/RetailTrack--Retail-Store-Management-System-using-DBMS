
-- Simple Retail Store Database --


CREATE DATABASE IF NOT EXISTS simple_retail_store;
USE simple_retail_store;

-- 1. Products table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Customers table  
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Sales table
CREATE TABLE sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    product_id INT,
    quantity_sold INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Insert sample data 

-- Sample products
INSERT INTO products (product_name, price, stock_quantity) VALUES
('Rice 1kg', 80.00, 50),
('Dal 1kg', 120.00, 30),
('Oil 1L', 150.00, 25),
('Sugar 1kg', 45.00, 40),
('Tea 250g', 200.00, 35),
('Bread', 25.00, 20),
('Milk 1L', 55.00, 15),
('Biscuits', 30.00, 60);

-- Sample customers  
INSERT INTO customers (customer_name, phone, email) VALUES
('Rajesh Kumar', '9876543210', 'rajesh@email.com'),
('Priya Sharma', '9876543211', 'priya@email.com'),
('Amit Patel', '9876543212', 'amit@email.com'),
('Sneha Reddy', '9876543213', 'sneha@email.com'),
('Karthik Menon', '9876543214', 'karthik@email.com'),
('Deepa Agarwal', '9876543215', 'deepa@email.com');
