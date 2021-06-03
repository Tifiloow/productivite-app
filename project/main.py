# main.py

from flask import Blueprint, render_template, request, jsonify, Flask
from flask_login import login_required, current_user

import sqlite3
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


# Todo section
# Add the elements added by the user in the DB
@main.route('/', methods=['POST'])
def todo_post():
#     Get the data from the DOM
    data = request.get_data()
    data = data.decode("utf-8") # Convert to UTF-8, currently in byte
    data = json.loads(data) # Convert string to dictionary

    connection = sqlite3.connect('db.sqlite') #Connect to DB
    cursor = connection.cursor()

#     Add the elements in the DB
    cursor.execute("INSERT INTO todo VALUES ('" + current_user.name + "', '" + data['task'] + "', '" + data['date'] + "', '" + data['priority55'] + "')")

    cursor.execute("SELECT * FROM todo")

    data_list = cursor.fetchall()
    print(data_list)
    connection.commit() #Save changes
    connection.close()
    return None

