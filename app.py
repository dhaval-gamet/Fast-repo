from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# 🔧 Render पर table auto-create: सिर्फ एक बार create_all() चलेगा
@app.before_request
def ensure_tables_exist():
    if not hasattr(app, '_tables_created'):
        db.create_all()
        app._tables_created = True

# डेटाबेस मॉडल
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    barcode = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    sale_price = db.Column(db.Float)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    customer_name = db.Column(db.String(100))

# रूट्स
@app.route('/')
def dashboard():
    products = Product.query.all()
    low_stock = Product.query.filter(Product.quantity < 10).count()
    total_products = len(products)
    stock_value = sum(p.quantity * p.price for p in products)
    return render_template('dashboard.html', 
                         products=products,
                         low_stock=low_stock,
                         total_products=total_products,
                         stock_value=stock_value)

@app.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        category = request.form['category']
        barcode = request.form.get('barcode', '')
        
        new_product = Product(
            name=name,
            quantity=quantity,
            price=price,
            category=category,
            barcode=barcode
        )
        
        db.session.add(new_product)
        db.session.commit()
        flash('प्रोडक्ट सफलतापूर्वक जोड़ा गया!', 'success')
        return redirect(url_for('manage_products'))
    
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/<int:id>/edit', methods=['POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    product.name = request.form['name']
    product.quantity = int(request.form['quantity'])
    product.price = float(request.form['price'])
    product.category = request.form['category']
    product.barcode = request.form.get('barcode', '')
    
    db.session.commit()
    flash('प्रोडक्ट अपडेट किया गया!', 'success')
    return redirect(url_for('manage_products'))

@app.route('/products/<int:id>/delete')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('प्रोडक्ट डिलीट किया गया!', 'danger')
    return redirect(url_for('manage_products'))

@app.route('/sales', methods=['GET', 'POST'])
def manage_sales():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])
        customer = request.form.get('customer', 'सामान्य ग्राहक')
        
        product = Product.query.get(product_id)
        if product.quantity < quantity:
            flash('पर्याप्त स्टॉक नहीं है!', 'danger')
            return redirect(url_for('manage_sales'))
        
        new_sale = Sale(
            product_id=product_id,
            quantity=quantity,
            sale_price=product.price,
            customer_name=customer
        )
        db.session.add(new_sale)
        
        product.quantity -= quantity
        db.session.commit()
        
        flash('बिक्री सफलतापूर्वक दर्ज की गई!', 'success')
        return redirect(url_for('manage_sales'))
    
    products = Product.query.all()
    sales = Sale.query.order_by(Sale.sale_date.desc()).limit(50).all()
    return render_template('sales.html', products=products, sales=sales)

@app.route('/reports')
def view_reports():
    products = Product.query.all()
    sales = Sale.query.all()
    
    total_sales = sum(s.quantity * s.sale_price for s in sales)
    total_items_sold = sum(s.quantity for s in sales)
    
    return render_template('reports.html', 
                         products=products,
                         sales=sales,
                         total_sales=total_sales,
                         total_items_sold=total_items_sold)

@app.route('/api/products')
def api_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'quantity': p.quantity,
        'price': p.price,
        'category': p.category
    } for p in products])

# ✅ Local testing के लिए
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
