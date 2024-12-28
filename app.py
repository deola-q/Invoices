from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import app, db
from flask_wtf.csrf import CSRFProtect
from flask import render_template, request, jsonify, flash
from models import Company, Invoice, PurchasedProduct, Customer, ResponsibleForInvoice, InvoiceItem, User
from forms import LoginForm

from flask_login import login_required, current_user
from functools import wraps
from flask import abort
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)  
login_manager.login_view = 'login' 
login_manager.login_message = "Вы не имеете доступа к данному функционалу."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# для проверки роли
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403) 
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/debug_user')
@login_required
def debug_user():
    return f"Current user: {current_user.email}, Role: {current_user.role}"

@app.route('/check_auth')
@login_required
def check_auth():
    return f"Authenticated: {current_user.is_authenticated}, Role: {current_user.role}"


@app.route("/")
def home():
    form = LoginForm()  
    return render_template("base.html", form=form)  

@app.route('/company')
def company_index():
    companies = Company.query.all()
    return render_template('company.html', companies=companies, user_role=current_user.role)


@app.route('/add_company', methods=['POST'])
@role_required('admin')
@login_required
def add_company():
    brand_name = request.form['brand_name']
    short_name = request.form['short_name']
    category = request.form['category']
    type_c = request.form['type_c']

    # Проверка на минимальную длину
    if len(brand_name) < 5:
        flash("Название компании должно состоять как минимум из 5 символов.", "error")
        return redirect(url_for('company_index'))

    new_company = Company(
        brand_name=brand_name,
        short_name=short_name,
        category=category,
        type_c=type_c
    )

    db.session.add(new_company)
    db.session.commit()
    return redirect(url_for('company_index'))


# @app.route('/delete_company/<int:company_id>', methods=['POST'])
# def delete_company(company_id):
#     company = Company.query.get_or_404(company_id)
#     db.session.delete(company)
#     db.session.commit()
#     return redirect(url_for('company_index'))

@app.route('/update_company/<int:company_id>', methods=['POST'])
def update_company(company_id):
    company = Company.query.get_or_404(company_id)

    company.brand_name = request.form.get('brand_name')
    company.short_name = request.form.get('short_name')
    company.category = request.form.get('category')
    company.type_c = request.form.get('type_c')

    try:
        db.session.commit()
        return redirect(url_for('company_index'))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Маршруты для таблицы INVOICE
from flask import request  # для получения параметра 'page'

from flask import request  # для получения параметра 'page'

@app.route('/invoice')
def invoice_index():
    # Получаем текущую страницу из параметров запроса (по умолчанию 1)
    page = request.args.get('page', 1, type=int)
    per_page = 30  # Количество записей на странице

    if current_user.role == 'admin':
        invoices = Invoice.query.paginate(page=page, per_page=per_page)
    elif current_user.role == 'worker':
        invoices = Invoice.query.filter_by(worker_id=current_user.id).paginate(page=page, per_page=per_page)
    
    return render_template('invoice.html', invoices=invoices)


@app.route('/add_invoice', methods=['POST'])
def add_invoice():
    # product_id = int(request.form['product_id'])
    customer_id = int(request.form['customer_id'])
    purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date()
    worker_id = int(request.form['worker_id'])

    # product = PurchasedProduct.query.get(product_id)
    customer = Customer.query.get(customer_id)

    # if not product or not customer:
        # return jsonify({'error': f'Customer or Product with this ID does not exist!'}), 400

    new_invoice = Invoice(
        # product_id=product_id,
        customer_id=customer_id,
        purchase_date=purchase_date,
        worker_id=worker_id
    )

    db.session.add(new_invoice)
    db.session.commit()
    return redirect(url_for('invoice_index'))

@app.route('/delete_invoice/<int:invoice_number>', methods=['POST'])
def delete_invoice(invoice_number):
    invoice = Invoice.query.get_or_404(invoice_number)
    db.session.delete(invoice)
    db.session.commit()
    return redirect(url_for('invoice_index'))


@app.route('/product')
def product_index():
    products = PurchasedProduct.query.all()
    return render_template('product.html', products=products, user_role=current_user.role)

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']

    if len(name) < 3:
        flash("Название продукции должно состоять как минимум из 3 символов.", "error")
        return redirect(url_for('product_index'))
    
    company_id = int(request.form['company_id'])
    category = request.form['category']
    batch_num = int(request.form['batch_num'])
    price = float(request.form['price'])

    company = Company.query.get(company_id)
    if not company:
        return jsonify({'error': f'Company with ID {company_id} does not exist!'}), 400

    if price <= 0:
        return jsonify({'error': 'Price must be greater than 0!'}), 400

    new_product = PurchasedProduct(
        name=name,
        company_id=company_id,
        category=category,
        batch_num=batch_num,
        price=price
    )

    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('product_index'))

# @app.route('/delete_product/<int:product_id>', methods=['POST'])
# def delete_product(product_id):
#     product = PurchasedProduct.query.get_or_404(product_id)
#     db.session.delete(product)
#     db.session.commit()
#     return redirect(url_for('product_index'))

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    
    product = PurchasedProduct.query.get_or_404(product_id)
    product.name = request.form.get('name')
    product.company_id = int(request.form.get('company_id'))
    product.category = request.form.get('category')
    product.batch_num = int(request.form.get('batch_num'))
    product.price = float(request.form.get('price'))
    try:
        db.session.commit()
        return redirect(url_for('product_index'))
    except Exception as e:
        return jsonify({'error': str(e)}), 400



@app.route('/customers')
def customer_index():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers, user_role=current_user.role)


@app.route('/add_customer', methods=['POST'])
def add_customer():
    try:
        name = request.form['name']
        surname = request.form['surname']
        lastname = request.form.get('lastname', None)  

        new_customer = Customer(
            name=name,
            surname=surname,
            lastname=lastname
        )

        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('customer_index'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 400

@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for('customer_index'))

@app.route('/update_customer/<int:customer_id>', methods=['POST'])
def update_customer(customer_id):
    try:

        customer = Customer.query.get_or_404(customer_id)
        customer.name = request.form.get('name')
        customer.surname = request.form.get('surname')
        customer.lastname = request.form.get('lastname', None)
        db.session.commit()
        return redirect(url_for('customer_index'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 400



@app.route('/responsible')
def responsible_index():
    employees = ResponsibleForInvoice.query.all()
    return render_template('responsible.html', employees=employees)


@app.route('/add_responsible', methods=['POST'])
def add_responsible():
    try:
        invoice_number = int(request.form['invoice_number'])
        name = request.form['name']
        surname = request.form['surname']
        lastname = request.form.get('lastname', None)  # Optional
        shift_code = int(request.form['shift_code'])

        new_employee = ResponsibleForInvoice(
            # invoice_number=invoice_number,
            name=name,
            surname=surname,
            lastname=lastname,
            shift_code=shift_code
        )

        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for('responsible_index'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 400


@app.route('/delete_responsible/<int:employee_id>', methods=['POST'])
def delete_responsible(employee_id):
    employee = ResponsibleForInvoice.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return redirect(url_for('responsible_index'))



from flask import request  # для получения параметра 'page'

@app.route('/invoice_item')
def invoice_items_index():
    page = request.args.get('page', 1, type=int)  # Получаем текущую страницу из параметров запроса (по умолчанию 1)
    per_page = 30  # Количество записей на странице

    if current_user.role == 'admin':
        invoice_items = InvoiceItem.query.paginate(page=page, per_page=per_page)
    elif current_user.role == 'worker':
        worker_invoices = Invoice.query.filter_by(worker_id=current_user.id).all()
        worker_invoice_ids = [invoice.invoice_number for invoice in worker_invoices]
        invoice_items = InvoiceItem.query.filter(InvoiceItem.invoice_id.in_(worker_invoice_ids)).paginate(page=page, per_page=per_page)

    return render_template('invoice_item.html', invoice_items=invoice_items)




@app.route('/add_invoice_item', methods=['POST'])
def add_invoice_item():
    try:
        invoice_id = int(request.form['invoice_id'])
        product_id = int(request.form['product_id'])

        product = PurchasedProduct.query.get(product_id)
        invoice = Invoice.query.get(invoice_id)

        if not product or not invoice:
            return jsonify({'error': f'Customer or Product with this ID does not exist!'}), 400

        existing_item = InvoiceItem.query.filter_by(invoice_id=invoice_id, product_id=product_id).first()
        if existing_item:
            flash("Такой товар уже есть в накладной.", "error")
            return redirect(url_for('invoice_items_index'))
        
        new_invoice_item = InvoiceItem(invoice_id=invoice_id, product_id=product_id)

        db.session.add(new_invoice_item)
        db.session.commit()
        return redirect(url_for('invoice_items_index'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 400


@app.route('/delete_invoice_item/<int:invoice_id>/<int:product_id>', methods=['POST'])
def delete_invoice_item(invoice_id, product_id):
    invoice_item = InvoiceItem.query.get_or_404((invoice_id, product_id))
    db.session.delete(invoice_item)
    db.session.commit()
    return redirect(url_for('invoice_items_index'))

@app.route('/update_invoice_item/<int:invoice_id>/<int:product_id>', methods=['POST'])
def update_invoice_item(invoice_id, product_id):
    try:
        invoice_item = InvoiceItem.query.get_or_404((invoice_id, product_id))

        new_invoice_id = int(request.form['new_invoice_id'])
        new_product_id = int(request.form['new_product_id'])

        if new_invoice_id != invoice_id or new_product_id != product_id:
            db.session.delete(invoice_item)
            updated_item = InvoiceItem(invoice_id=new_invoice_id, product_id=new_product_id)
            db.session.add(updated_item)
        else:
            invoice_item.invoice_id = new_invoice_id
            invoice_item.product_id = new_product_id

        db.session.commit()
        return redirect(url_for('invoice_items_index'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 400
    
    

from flask_login import login_user, logout_user

from flask_login import login_user, current_user

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.psw.data
        role = form.role.data

        # Проверяем, существует ли пользователь
        user = User.query.filter_by(email=email).first()

        if user:
            # Проверяем пароль
            if user.check_password(password):
                login_user(user)  # Логин пользователя через Flask-Login
                if user.role == 'admin':
                    flash("Добро пожаловать, Администратор!", "success")
                    return redirect(url_for('company_index'))
                elif user.role == 'worker':
                    flash("Добро пожаловать, Работник склада!", "success")
                    return redirect(url_for('company_index'))
                else:
                    flash("Неизвестная роль пользователя!", "error")
            else:
                flash("Неверный пароль!", "error")
        else:
            # Регистрация нового пользователя
            new_user = User(email=email, role=role)
            new_user.set_password(password)  
            db.session.add(new_user)
            db.session.commit()
            flash(f"Пользователь зарегистрирован как {role}. Пожалуйста, войдите снова.", "success")
            return redirect(url_for('login')) 

    return render_template('base.html', form=form, user_role=current_user.role if current_user.is_authenticated else None)


@app.route('/statistics')
def statistics():
    # Пример получения статистики
    total_users = User.query.count()  # Общее количество пользователей
    admin_count = User.query.filter_by(role='admin').count()  # Количество администраторов
    worker_count = User.query.filter_by(role='worker').count()  # Количество работников
    total_products = PurchasedProduct.query.count()  # Общее количество продуктов (если есть модель Product)
    total_customers = Customer.query.count()

    # Формирование результата
    stats = {
        "total_users": total_users,
        "admin_count": admin_count,
        "worker_count": worker_count,
        "total_products": total_products,
        "total_customers": total_customers
    }
    return render_template('statistics.html', stats=stats) 


def get_filtered_invoice_items():

    search_inv = request.args.get('inv', '')
    search_name = request.args.get('name', '')
    search_category = request.args.get('category', '')
    search_price_min = request.args.get('price_min', type=float)
    search_price_max = request.args.get('price_max', type=float)
    page = request.args.get('page', 1, type=int)
    per_page = 50  


    query = db.session.query(InvoiceItem, PurchasedProduct).join(PurchasedProduct, InvoiceItem.product_id == PurchasedProduct.product_id)

    if search_inv:
        query = query.filter(InvoiceItem.invoice_id == int(search_inv))
    if search_name:
        query = query.filter(PurchasedProduct.name.ilike(f'%{search_name}%'))
    if search_category:
        query = query.filter(PurchasedProduct.category.ilike(f'%{search_category}%'))
    if search_price_min:
        query = query.filter(PurchasedProduct.price >= search_price_min)
    if search_price_max:
        query = query.filter(PurchasedProduct.price <= search_price_max)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    invoice_items = pagination.items

    return invoice_items, pagination

@app.route('/filtered_invoice_items', methods=['GET'])
def filtered_invoice_items():
    # Получаем данные с фильтрацией и пагинацией
    invoice_items, pagination = get_filtered_invoice_items()

    return render_template('filtered_invoice_item.html', 
                           invoice_items=invoice_items, 
                           pagination=pagination)

if __name__ == '__main__':
    app.run(debug=True)


