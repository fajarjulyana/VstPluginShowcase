from models import db, User, VSTProduct, CartItem, Purchase, Contact

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "arvin-studio-secret-key"

# ✅ Configure Image Uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# ✅ Correctly Initialize db
db.init_app(app)

# ✅ Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    products = VSTProduct.query.all()
    return render_template('index.html', products=products)

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = VSTProduct.query.get_or_404(product_id)
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id)
        db.session.add(cart_item)

    db.session.commit()
    flash('Product added to cart!')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action')
        return redirect(url_for('cart'))

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('cart'))

    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        # Create purchase records
        for item in cart_items:
            purchase = Purchase(
                buyer_name=current_user.username,
                buyer_email=current_user.email,
                product_id=item.product_id,
                amount=item.product.price * item.quantity
            )
            db.session.add(purchase)
            db.session.delete(item)

        db.session.commit()
        flash('Thank you for your purchase!')
        return redirect(url_for('index'))

    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/contact', methods=['POST'])
def contact():
    try:
        data = request.form
        contact = Contact(
            name=data['name'],
            email=data['email'],
            message=data['message']
        )
        db.session.add(contact)
        db.session.commit()
        return jsonify({'message': 'Message sent successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']) and user.is_admin:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    products = VSTProduct.query.all()
    purchases = Purchase.query.all()
    contacts = Contact.query.all()
    return render_template('admin/dashboard.html', products=products, purchases=purchases, contacts=contacts)


@app.route('/admin/products/new', methods=['GET', 'POST'])
@login_required
def admin_new_product():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        features = request.form.getlist('features')

        # Handle file upload
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_url = f"/{image_path}"  # Store relative path
        else:
            image_url = None  # No file uploaded

        product = VSTProduct(
            name=name,
            description=description,
            price=price,
            features=features,
            image_url=image_url
        )

        db.session.add(product)
        db.session.commit()
        flash('Product added successfully')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/product_form.html')

@app.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_product(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    product = VSTProduct.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.features = request.form.getlist('features')

        # Handle image upload
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            product.image_url = f"/{image_path}"  # Update image URL if new file is uploaded

        db.session.commit()
        flash('Product updated successfully')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/product_form.html', product=product)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already registered')
            return redirect(url_for('register'))

        user = User(
            username=request.form['username'],
            email=request.form['email']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # ✅ Ensure tables are created
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@arvinstudio.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    app.run(host='0.0.0.0', port=5000, debug=True)
