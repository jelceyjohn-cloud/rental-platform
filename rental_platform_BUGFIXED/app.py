"""
app.py — Flask backend for the Rental Property Listing Platform

Public side:
  /                       -> browse/search properties
  /property/<id>          -> property detail page
  /property/<id>/apply    -> apply for that property (GET form, POST save)

Admin side (session-based login):
  /admin/login            -> login form
  /admin/logout
  /admin/dashboard        -> overview: properties + application counts
  /admin/property/add     -> add a new property
  /admin/property/<id>/delete
  /admin/applications     -> view every application received
"""

import flask 
from werkzeug.security import generate_password_hash, check_password_hash 
import functools
import os
from models import db, Property, Application, Admin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

print("=" * 60)
print("STARTUP CHECK")
print(f"  app.py location:          {BASE_DIR}")
print(f"  Looking for templates at: {TEMPLATE_DIR}")
print(f"  templates/ exists?        {os.path.isdir(TEMPLATE_DIR)}")
print(f"  Looking for static at:    {STATIC_DIR}")
print(f"  static/ exists?           {os.path.isdir(STATIC_DIR)}")
print("=" * 60)

if not os.path.isdir(TEMPLATE_DIR):
    raise SystemExit(f"\nSTARTUP ERROR: templates folder not found at:\n  {TEMPLATE_DIR}\n"
                      f"This means the 'templates' folder was not uploaded/pushed correctly.\n")
if not os.path.isdir(STATIC_DIR):
    raise SystemExit(f"\nSTARTUP ERROR: static folder not found at:\n  {STATIC_DIR}\n"
                      f"This means the 'static' folder was not uploaded/pushed correctly.\n")

app = flask.Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = 'dev-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    # Create a default admin account the first time the app runs,
    # so there's something to log in with immediately.
    if not Admin.query.filter_by(username='admin').first():
        default_admin = Admin(
    username='admin',
    password_hash=generate_password_hash('admin123')
)
        db.session.add(default_admin)
        db.session.commit()


# ---------------------------------------------------------
# LOGIN-REQUIRED DECORATOR (protects admin routes)
# ---------------------------------------------------------
def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        if not flask.session.get('admin_logged_in'):
            return flask.redirect(flask.url_for('admin_login'))
        return view_func(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------
# PUBLIC ROUTES
# ---------------------------------------------------------
@app.route('/')
def home():
    city = flask.request.args.get('city', '').strip()
    max_price = flask.request.args.get('max_price', '').strip()

    query = Property.query.filter_by(available=True)

    if city:
        query = query.filter(Property.city.ilike(f'%{city}%'))
    if max_price.isdigit():
        query = query.filter(Property.price <= int(max_price))

    properties = query.order_by(Property.created_at.desc()).all()
    return flask.render_template('home.html', properties=properties, city=city, max_price=max_price)


@app.route('/property/<int:property_id>')
def property_detail(property_id):
    prop = Property.query.get_or_404(property_id)
    return flask.render_template('property_detail.html', prop=prop)


def validate_application_form(form):
    errors = []
    name = form.get('applicant_name', '').strip()
    email = form.get('email', '').strip()
    phone = form.get('phone', '').strip()
    movein = form.get('move_in_date', '').strip()

    if not name:
        errors.append("Name is required.")
    elif not name.replace(' ', '').isalpha():
        errors.append("Name must contain letters only (no numbers).")

    if not email or '@' not in email or '.' not in email:
        errors.append("A valid email address is required.")

    if not phone:
        errors.append("Phone number is required.")

    if not movein:
        errors.append("Move-in date is required.")

    return errors


@app.route('/property/<int:property_id>/apply', methods=['GET', 'POST'])
def apply(property_id):
    prop = Property.query.get_or_404(property_id)

    if flask.request.method == 'POST':
        errors = validate_application_form(flask.request.form)
        if errors:
            return flask.render_template('apply.html', prop=prop, errors=errors, form_data=flask.request.form)

        new_app = Application(
            property_id=prop.id,
            applicant_name=flask.request.form.get('applicant_name', '').strip(),
            email=flask.request.form.get('email', '').strip(),
            phone=flask.request.form.get('phone', '').strip(),
            move_in_date=flask.request.form.get('move_in_date', '').strip(),
            occupants=flask.request.form.get('occupants') or 1,
            message=flask.request.form.get('message', '').strip(),
        )
        db.session.add(new_app)
        db.session.commit()
        return flask.render_template('apply_success.html', prop=prop)

    return flask.render_template('apply.html', prop=prop, errors=None, form_data={})


# ---------------------------------------------------------
# ADMIN ROUTES
# ---------------------------------------------------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if flask.request.method == 'POST':
        username = flask.request.form.get('username', '').strip()
        password = flask.request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            flask.session['admin_logged_in'] = True
            flask.session['admin_username'] = admin.username
            return flask.redirect(flask.url_for('admin_dashboard'))
        else:
            error = "Invalid username or password."

    return flask.render_template('admin_login.html', error=error)


@app.route('/admin/logout')
def admin_logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('admin_login'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    properties = Property.query.order_by(Property.created_at.desc()).all()
    total_applications = Application.query.count()
    return flask.render_template('admin_dashboard.html', properties=properties,
                            total_applications=total_applications)


@app.route('/admin/property/add', methods=['GET', 'POST'])
@login_required
def add_property():
    if flask.request.method == 'POST':
        new_prop = Property(
            title=flask.request.form.get('title', '').strip(),
            city=flask.request.form.get('city', '').strip(),
            address=flask.request.form.get('address', '').strip(),
            price=flask.request.form.get('price') or 0,
            bedrooms=flask.request.form.get('bedrooms') or 1,
            bathrooms=flask.request.form.get('bathrooms') or 1,
            description=flask.request.form.get('description', '').strip(),
            
        )
        db.session.add(new_prop)
        db.session.commit()
        return flask.redirect(flask.url_for('admin_dashboard'))

    return flask.render_template('add_property.html')


@app.route('/admin/property/<int:property_id>/delete', methods=['POST'])
@login_required
def delete_property(property_id):
    prop = Property.query.get_or_404(property_id)
    db.session.delete(prop)   # cascade also deletes its applications
    db.session.commit()
    return flask.redirect(flask.url_for('admin_dashboard'))


@app.route('/admin/applications')
@login_required
def view_applications():
    applications = Application.query.order_by(Application.submitted_at.desc()).all()
    return flask.render_template('view_applications.html', applications=applications)


if __name__ == '__main__':
    app.run(debug=True)
