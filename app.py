from flask import Flask,render_template,session,request,redirect, url_for,jsonify
import requests
from datetime import date
import os
import sqlite3


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/image'

conn = sqlite3.connect('database.db', check_same_thread=False)

app.secret_key = 'your_secret_key'
product_list = [
        {
            'id' : '1',
            'title' : 'shirt',
            'price' : '10.00',
            'description': "'The Gidan Ultra Cotton T-shirt is made from a substaintial 6.0 oz. per sq. yd. fabric constructed from 100% cotton, this classic fit preshrunk jersey knit provides unmatched comfort with each wear. Featuring a laped neck and shoulder, and a seamless double-needle collar, and available in a range of colors, it offers it all in ultimate head turning package.'",
            'image': 'products/f1.jpg',
        },
        {
            'id': '2',
            'title': 'flower shirt',
            'price': '10.00',
            'description': "'The Gidan Ultra Cotton T-shirt is made from a substaintial 6.0 oz. per sq. yd. fabric constructed from 100% cotton, this classic fit preshrunk jersey knit provides unmatched comfort with each wear. Featuring a laped neck and shoulder, and a seamless double-needle collar, and available in a range of colors, it offers it all in ultimate head turning package.'",
            'image': 'products/f2.jpg',
        },
        {
            'id': '3',
            'title': 'red shirt',
            'price': '10.00',
            'description': "'The Gidan Ultra Cotton T-shirt is made from a substaintial 6.0 oz. per sq. yd. fabric constructed from 100% cotton, this classic fit preshrunk jersey knit provides unmatched comfort with each wear. Featuring a laped neck and shoulder, and a seamless double-needle collar, and available in a range of colors, it offers it all in ultimate head turning package.'",
            'image': 'products/f3.jpg',
        },
        {
            'id': '4',
            'title': 'yellow shirt',
            'price': '10.00',
            'description': "'The Gidan Ultra Cotton T-shirt is made from a substaintial 6.0 oz. per sq. yd. fabric constructed from 100% cotton, this classic fit preshrunk jersey knit provides unmatched comfort with each wear. Featuring a laped neck and shoulder, and a seamless double-needle collar, and available in a range of colors, it offers it all in ultimate head turning package.'",
            'image': 'products/f4.jpg',
        },


    ]

# Telegram bot configuration
bot_token = "7150364581:AAE6GBU-0J4O06amcTRKVfq13dY0DRiCAuo"
chat_id = "-1002120257472"


@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")


@app.get('/about')
def about():
    return render_template('about.html')


@app.get('/contact')
def contact():
    return render_template('contact.html')


@app.route('/shop')
def shop():
    response = requests.get('https://fakestoreapi.com/products')
    products = response.json()
    for product in products:
        print(product['image'])
    return render_template('shop.html', product_list=products)


@app.route('/product/<int:product_id>', methods=['GET'])
def sproduct(product_id):
    response = requests.get(f'https://fakestoreapi.com/products/{product_id}')
    product = response.json()
    return render_template('sproduct.html', product=product)


@app.route('/checkout/<int:product_id>', methods=['GET'])
def checkout(product_id):
    response = requests.get(f'https://fakestoreapi.com/products/{product_id}')
    product = response.json()
    return render_template('checkout.html', product=product)


@app.route('/submit_order/<int:product_id>', methods=['POST'])
def submit_order(product_id):
    response = requests.get(f'https://fakestoreapi.com/products/{product_id}')
    product = response.json()
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')

    order_details = (
        f"Order submitted for {product['title']} by {name} "
        f"(Phone: {phone}, Email: {email})"
    )

    caption_text = (
        f"<strong>🧾 Order Confirmation</strong>\n"
        f"<code>Product: {product['title']}</code>\n"
        f"<code>Price: ${product['price']}</code>\n"
        f"<code>Name: {name}</code>\n"
        f"<code>Phone: {phone}</code>\n"
        f"<code>Email: {email}</code>\n"
        f"<code>📆 Date: {date.today()}</code>\n"
        f"<code>=======================</code>\n"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    params = {
        "chat_id": chat_id,
        "photo": product['image'],  # URL of the product image
        "caption": caption_text,
        "parse_mode": "HTML"
    }
    telegram_response = requests.post(url, data=params)

    # Log the response from Telegram for debugging
    print(telegram_response.status_code)
    print(telegram_response.text)
    return order_details


@app.get('/cart')
def cart():
    return render_template('cart.html')


@app.get('/jinja')
def jinja():
    # Set session data
    session['username'] = 'vicheka'
    return render_template('jinja.html', username=session.get('username'))


@app.get('/product_list')
def product_list():
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, price, category, description, COALESCE(image, 'no_image') AS image FROM product")
    rows = cursor.fetchall()
    products = [
        {
            'id': row[0],
            'title': row[1],
            'price': row[2],
            'category': row[3],
            'description': row[4],
            'image': row[5],
        } for row in rows
    ]
    return render_template('product_list.html', data=products, module='product')


@app.get('/add_product')
def add_product():
    # row = conn.execute("select * from product")
    # for item in row:
    #     print(f"{item[0]}-{item[1]}")
    return render_template('add_product.html')


@app.route('/submit_new_product', methods=['POST'])
def submit_new_product():
    product_id = request.form.get('product_id')
    title = request.form.get('title')
    file = request.form.get('file')
    price = request.form.get('price')
    category = request.form.get('category')
    description = request.form.get('description')
    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'] + '/product', file.filename))

    res = conn.execute(
        f"""INSERT INTO `product` VALUES (null, '{title}', {price}, '{category}', '{description}', '{file.filename}')""")
    conn.commit()
    print(res)
    return redirect(url_for('product_list'))


@app.route('/delete_product/<int:id>', methods=['DELETE'])
def delete_product(id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE id=?", (id,))
        conn.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        print(e)
        return jsonify({'success': False}), 500


@app.route('/edit_product', methods=['GET'])
def edit_product():
    product_id = request.args.get('id')
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM product WHERE id = ?', (product_id,))
    row = cursor.fetchone()  # Fetch a single row
    conn.close()

    if row is None:
        return "Product not found", 404

    product = {
        'id': row[0],
        'title': row[1],
        'price': row[2],
        'category': row[3],
        'description': row[4],
        'image': row[5],
    }

    print(product)  # Debugging statement
    return render_template('edit_product.html', product=product)


@app.route('/update_product', methods=['POST'])
def update_product():
    product_id = request.form['product_id']
    title = request.form['title']
    price = request.form['price']
    category = request.form['category']
    description = request.form['description']
    file = request.files['file']

    # Check if a new file was uploaded
    if file and file.filename != '':
        filename = file.filename
        file.save(os.path.join('static/image/product', filename))
    else:
        filename = None  # No new file uploaded
    cursor = conn.cursor()

    # Update query with or without file
    if filename:
        cursor.execute("""
            UPDATE product 
            SET title = ?, price = ?, category = ?, description = ?, image = ? 
            WHERE id = ?
        """, (title, price, category, description, filename, product_id))
    else:
        cursor.execute("""
            UPDATE product 
            SET title = ?, price = ?, category = ?, description = ? 
            WHERE id = ?
        """, (title, price, category, description, product_id))

    conn.commit()


    return redirect(url_for('product_list'))


if __name__ == '__main__':
    app.run()
