# main.py

from flask import Blueprint, render_template, request, jsonify, Flask, redirect, flash, url_for
from flask_login import login_required, current_user

import sqlite3
import json

from .ecoleDirecte import EcoleDirecte as ED

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, ecoledirecte=bool(current_user.ed_username))

@main.route('/todo', methods=['POST', 'GET'])
@login_required
def todo():
    return render_template('todo.html', name=current_user.name, ecoledirecte=bool(current_user.ed_username), method=request.method)

# Todo section
# Add the elements added by the user in the DB
@main.route('/', methods=['POST'])
@login_required
def todo_post():
#     Get data from the DOM
    data = request.get_data()
    data = data.decode("utf-8") # Convert to UTF-8, currently in byte
    data = json.loads(data) # Convert string to dictionary

    connection = sqlite3.connect('db.sqlite') #Connect to DB
    cursor = connection.cursor()

    print(f"DEBUG : GOAL -> {data['goal']}") #DEBUG

    #Update the task status in the DB
    if data['goal'] == "updateStatus":
        cursor.execute("UPDATE todo SET status ='"+data['status']+"' WHERE taskID="+data['taskID']+"")

    elif data['goal'] == "addElement":
        cursor.execute("INSERT INTO todo (userID, task, date, priority, tag) VALUES ('{}','{}','{}','{}', '{}')"
                .format(current_user.name, data['task'], data['date'], data['priority'], data["tag"]))
        cursor.execute("SELECT * FROM todo WHERE userID='{}' ORDER BY taskID DESC LIMIT 1"
                .format(current_user.name))
        data_list = cursor.fetchall()
        print(f"DEBUG : TaskID -> {data_list[0][0]}") #DEBUG

    elif data['goal'] == "removeElement":
            cursor.execute("DELETE FROM todo WHERE taskID='"+data['taskID']+"'")

    connection.commit() #Save changes
    connection.close()

    return jsonify(data_list[0][0] if 'data_list' in locals() else "Success") #Return the taskID or "Success" message

@main.route('/getdata')
@login_required
def getdata():
    return render_template('getdata.html')

@main.route('/getdata', methods=['POST'])
@login_required
def todo_get():
    # get all tasks of the current user
    connection = sqlite3.connect('db.sqlite') #Connect to DB
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM todo WHERE userID='{current_user.name}'")
    data_list = cursor.fetchall()
    #print(data_list)

    connection.commit() #Save changes
    connection.close()
    print (data_list)
    return jsonify(data_list)

@main.route('/gettags', methods=["POST"])
@login_required
def todo_get_tags():
    # get all tasks of the current user
    connection = sqlite3.connect('db.sqlite') #Connect to DB
    cursor = connection.cursor()
    cursor.execute(f"SELECT tag FROM todo WHERE userID='{current_user.name}'")
    data_list = cursor.fetchall()

    connection.close()
    return jsonify(data_list)


@main.route('/ecoledirecte')
@login_required
def ecoledirecte():
    # If an account is already given, stop here
    if current_user.ed_username:
        return redirect(url_for("main.profile"))
    return render_template('ecoledirecte.html')

@main.route('/ecoledirecte_unlink')
@login_required
def ecoledirecte_unlink():
    ED.unlink()
    return redirect(url_for("main.profile"))

@main.route('/ecoledirecte', methods=['POST'])
@login_required
def ecoledirecte_post():
    # Get informations throught the form.
    ED_username = request.form.get('username')
    ED_password = request.form.get('password')
    website_password = request.form.get('website_password')

    #Check if the informations are valid, and display an error if not.
    response, token = ED.login(ED_username, ED_password)

    #print("token", token)
    #print("code", response["code"])

    if response["code"] == 505 :
        flash('Invalid username or password, please try again.')
        return redirect(url_for("main.ecoledirecte"))
    
    elif response["code"] == 40129 :
        flash('Format JSON invalide.')
        return redirect(url_for("main.ecoledirecte"))

    # Add informations in the database.
    result = ED.link(ED_username, ED_password, website_password)

    if not result: # échec link
        flash("User Password is incorrect")
        return redirect(url_for("main.ecoledirecte"))

    return redirect(url_for('main.todo'))

@main.route('/ecoledirecte_fetch')
@login_required
def ecoledirecte_fetch_form():
    return render_template('ecoledirecte_fetch.html')

@main.route('/ecoledirecte_fetch', methods=['POST'])
@login_required
def ecoledirecte_fetch():
    password = request.form.get('password')

    if not password :
        flash('Veuillez renseigner votre mot de passe')
        return redirect(url_for("main.ecoledirecte_fetch"))

    work, token = ED.AddWork(password)

    if not token :
        flash('Mot de passe incorrect')
        return redirect(url_for("main.ecoledirecte_fetch"))

    #print(work)

    return redirect(url_for("main.todo"))
    
@main.route('/pomodoro')
@login_required
def pomodoro():
    return render_template('pomodoro.html')
