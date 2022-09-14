"""Server for running app."""


from flask import Flask, render_template, redirect, request, flash, session
from model import db, connect_to_db
from werkzeug.utils import secure_filename


import crud
import csv
import os


from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def show_homepage():
    """Displays homepage."""

    return render_template('homepage.html')


@app.route('/account', methods=['POST'])
def create_user_account():
    """User creates an account."""

    email = request.form.get('email')
    password = request.form.get('password')

    user = crud.get_user_by_email(email)

    if user:
        # checks if user already created an account with this email
        flash('This email already has an account. Try another email or try logging in.')
    else:
        new_user = crud.create_user(email, password)
        db.session.add(new_user)
        db.session.commit()
        flash('Congratulations. Your account was created.')
    return redirect('/')


@app.route('/login', methods=['POST'])
def user_login():
    """User logs in."""

    email = request.form.get('email')
    password = request.form.get('password')

    user = crud.get_user_by_email(email)

    session['user_id'] = user.user_id

    # check if user has an account and if password matches
    if not user or user.password != password:
        flash('Error. Try again.')
        return redirect('/')
    else:
        flash('You are logged in.')
        return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """User uploads csv file that is parsed."""

    file = request.files['file']

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('input', filename))

        with open(f'input/{filename}', 'r') as csvfile:
            csv_read = csv.DictReader(csvfile)

            for line in csv_read:
                customer = crud.create_customer(line)

                db.session.add(customer)
                db.session.commit()

                session['customer_id'] = customer.customer_id

                order = crud.create_order(line)

                db.session.add(order)
                db.session.commit()

    return render_template('dashboard.html')


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, host="0.0.0.0")
