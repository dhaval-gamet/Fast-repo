from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_pyfile('config.py')

# Configure session secret key
app.secret_key = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

# Initialize database
db = SQLAlchemy(app)

# Create database tables within application context
with app.app_context():
    db.create_all()

# Database Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    barcode = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    sale_price = db.Column(db.Float)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    customer_name = db.Column(db.String(100))

    def __repr__(self):
        return f'<Sale {self.id}>'

# Routes
@app.route('/')
def dashboard():
    try:
        products = Product.query.all()
        low_stock = Product.query.filter(Product.quantity < 10).count()
        total_products = len(products)
        stock_value = sum(p.quantity * p.price for p in products if p.price)
        
        return render_template('dashboard.html', 
                           products=products,
                           low_stock=low_stock,
                           total_products=total_products,
                           stock_value=stock_value)
    except Exception as e:
        flash('डेटाबेस त्रुटि: कृपया एडमिन से संपर्क करें', 'danger')
        return render_template('dashboard.html')

@app.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        try:
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
        except Exception as e:
            db.session.rollback()
            flash(f'त्रुटि: {str(e)}', 'danger')
        
        return redirect(url_for('manage_products'))
    
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/<int:id>/edit', methods=['POST'])
def edit_product(id):
    try:
        product = Product.query.get_or_404(id)
        product.name = request.form['name']
        product.quantity = int(request.form['quantity'])
        product.price = float(request.form['price'])
        product.category = request.form['category']
        product.barcode = request.form.get('barcode', '')
        
        db.session.commit()
        flash('प्रोडक्ट अपडेट किया गया!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'त्रुटि: {str(e)}', 'danger')
    
    return redirect(url_for('manage_products'))

@app.route('/products/<int:id>/delete')
def delete_product(id):
    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        flash('प्रोडक्ट डिलीट किया गया!', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'त्रुटि: {str(e)}', 'danger')
    
    return redirect(url_for('manage_products'))

@app.route('/sales', methods=['GET', 'POST'])
def manage_sales():
    if request.method == 'POST':
        try:
            product_id = int(request.form['product_id'])
            quantity = int(request.form['quantity'])
            customer = request.form.get('customer', 'सामान्य ग्राहक')
            
            product = Product.query.get(product_id)
            if not product:
                flash('प्रोडक्ट नहीं मिला!', 'danger')
                return redirect(url_for('manage_sales'))
            
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
        except Exception as e:
            db.session.rollback()
            flash(f'त्रुटि: {str(e)}', 'danger')
        
        return redirect(url_for('manage_sales'))
    
    products = Product.query.all()
    sales = Sale.query.order_by(Sale.sale_date.desc()).limit(50).all()
    return render_template('sales.html', products=products, sales=sales)

@app.route('/reports')
def view_reports():
    products = Product.query.all()
    sales = Sale.query.all()
    
    total_sales = sum(s.quantity * s.sale_price for s in sales if s.sale_price)
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

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
