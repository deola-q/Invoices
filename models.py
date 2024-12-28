from flask_sqlalchemy import SQLAlchemy
from config import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# Модель для таблицы COMPANY
class Company(db.Model):
    __tablename__ = 'company'

    company_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    brand_name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(50))
    category = db.Column(db.String(2), nullable=False)
    type_c = db.Column(db.String(1), nullable=False)

    def __repr__(self):
        return f'<Company {self.brand_name}>'
    
# Модель для таблицы CUSTOMERS
from sqlalchemy.orm import relationship

class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50))

    # Отношение к таблице Invoice
    invoices = relationship('Invoice', back_populates='customer', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Customer {self.name} {self.surname}>'


class Invoice(db.Model):
    __tablename__ = 'invoice'

    invoice_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)  # Связь с customers
    purchase_date = db.Column(db.Date, nullable=False)
    worker_id = db.Column(db.Integer, nullable=False)

    # Обратное отношение к Customer
    customer = relationship('Customer', back_populates='invoices')

    def __repr__(self):
        return f'<Invoice #{self.invoice_number}>'


# Модель для таблицы PURCHASED_PRODUCT
class PurchasedProduct(db.Model):
    __tablename__ = 'purchased_product'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(2), nullable=False)
    batch_num = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

# Модель для таблицы RESPONSIBLE_FOR_INVOICES
class ResponsibleForInvoice(db.Model):
    __tablename__ = 'responsible_for_invoices'

    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # invoice_number = db.Column(db.Integer, db.ForeignKey('invoice.invoice_number'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50))
    shift_code = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Employee {self.name} {self.surname}, Shift {self.shift_code}>'

# Модель для таблицы INVOICE_ITEMS
class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.invoice_number'), primary_key=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('purchased_product.product_id'), primary_key=True, nullable=False)

    invoice = db.relationship('Invoice', backref=db.backref('invoice_items', cascade='all, delete-orphan'))
    product = db.relationship('PurchasedProduct', backref=db.backref('invoice_items', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<InvoiceItem Invoice {self.invoice_id}, Product {self.product_id}>'
    
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Здесь храним хеш пароля
    role = db.Column(db.String(50), nullable=False)  # admin или worker

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    


