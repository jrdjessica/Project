"""CRUD operations."""


import csv
from flask import session, flash
from model import User, Customer, Order, connect_to_db, db
import os

import json
import ssl
import shutil

import urllib.request
import urllib.parse
import urllib.error


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def create_user(email, password):
    """Create a user."""

    user = User(email=email, password=password)

    return user


def get_user_by_email(email):
    """Return a user by email."""

    user = User.query.filter(User.email == email).first()

    return user


def create_customer(line):
    """Create a customer."""

    user_id = session['user_id']

    # Create address
    address_components = ['Street 1', 'Street 2', 'Ship City',
                          'Ship State', 'Ship Zipcode', 'Ship Country']

    address = ''

    for comp in address_components:
        if comp == 'Ship Country':
            address += line[comp]
        elif line[comp] != '':
            address += f'{line[comp]}, '

    # Create latitude and longitude
    parms = dict()
    parms['address'] = address
    key = os.environ['GEO_KEY']
    parms['key'] = key
    url = 'https://maps.googleapis.com/maps/api/geocode/json?' + \
        urllib.parse.urlencode(parms)

    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()

    js = json.loads(data)

    if js['status'] != 'OK':
        print(js["status"])

    lat = js['results'][0]['geometry']['location']['lat']
    lng = js['results'][0]['geometry']['location']['lng']

    # Create instance
    customer = Customer(user_id=user_id, fname=line['First Name'].title(), lname=line['Last Name'].title(), street=line['Street 1'], street2=line['Street 2'],
                        city=line['Ship City'].title(), state=line['Ship State'], zipcode=line['Ship Zipcode'], country=line['Ship Country'], address=address, latitude=lat, longitude=lng)

    return customer


def add_to_database(file):
    """Parse through csv file and add data to database."""

    with open(file, newline='') as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            print(row['date'])


def create_order(line):
    """Create an order."""

    user_id = session['user_id']
    customer_id = session['customer_id']

    order = Order(order_id=line['Order ID'], customer_id=customer_id, user_id=user_id, num_items=line['Number of Items'], date=line['Sale Date'],
                  total=line['Order Total'], net=line['Order Net'])

    return order


def convert_currency(data):
    """Return converted currency total."""

    return data['conversion_result']


def delete_account(user_id):
    """Delete file and remove from database."""

    if user_id == 1:
        flash('Error. This demo code cannot be deleted')
    else:
        path = f'input/{user_id}'
        shutil.rmtree(path)
        for customer in Customer.query.filter(Customer.user_id == user_id).all():
            db.session.delete(customer)
            db.session.delete(customer.user)
        for order in Order.query.filter(Order.customer_id == user_id).all():
            db.session.delete(order)
        db.session.commit()


if __name__ == "__main__":
    from server import app

    connect_to_db(app)
