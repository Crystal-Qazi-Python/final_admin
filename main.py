from flask import Flask, render_template, request, redirect, flash, g
from flask_paginate import get_page_parameter, Pagination
import sqlite3
import csv
from csv import reader
import os
from werkzeug.utils import secure_filename
from flask_sslify import SSLify
import yaml
from waitress import serve
import pandas as pd
import glob
import requests
import pathlib
import wget
import subprocess
from flask import send_file


app = Flask(__name__)
app.config['SECRET_KEY'] = 'j#!cl88i%@q@z2vgo7$4bg9!pa5$#!(r96om$+i4!cb+-dl^)a'
path = "E:/"
upload_folder = os.path.join(os.getenv('USERPROFILE'), os.getenv('temp'))
export_folder = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
# export_folder = "E:/"
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
extension = csv
app.config['UPLOAD_FOLDER'] = upload_folder




def yaml_data():
    with open('config.yaml', 'r') as f:
        yml_data = yaml.load(f, Loader=yaml.FullLoader)
        return yml_data
    

def get_db():
    con = getattr(g, "directory.db", None)
    if con is None:
        con = g._database = sqlite3.connect("directory.db")
        with con:
            try:
                # con.execute("create table users (id INTEGER PRIMARY KEY NOT NULL, name TEXT not null, \
                # department  TEXT NOT NULL, designation  TEXT char(20), ext INTEGER NOT NULL UNIQUE)")
                # con.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL, \
                #     department TEXT NOT NULL, designation TEXT char(20) NOT NULL, ext INTEGER NOT NULL UNIQUE)")
                con.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, \
                                    department TEXT, designation TEXT char(20), ext INTEGER UNIQUE)")
                flash("New Database Created")
                con.commit()

                # id INTEGER NOT NULL UNIQUE AUTOINCREMENT
            except sqlite3.OperationalError:
                pass
            finally:
                return con


@app.route("/", methods=['POST', 'GET'])
def index():
    yml_data = yaml_data()
    con = get_db()
    # con = sqlite3.connect("directory.db")
    con.row_factory = sqlite3.Row
    ###########################################################################
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    
    limit = 10
    from_num = page * limit - limit + 1
    to_num = page * limit

    #########################################################################
    cur = con.cursor()
    cur.execute("select * from users")
    users = cur.fetchall()
    total = len(users)
    print(total)
    # flash('connect', 'warning')

    ##########################################################################
    cur.execute("""select * from users
                        where id between ? and ?""", (from_num, to_num))
    users = cur.fetchall()
    con.close()
    # pagination = Pagination(page=page, page_per=limit, total=total, search=search)
    pagination = Pagination(page=page,  total=total, search=search)
    # pagination = Pagination(page=page, total=users.count(), search=search, record_name='users')

    ############################################################################
    return render_template("dashboards/index.html", users=users, pagination=pagination, data = yml_data, test=page )




@app.route("/save", methods=['POST', 'GET'])
def save():
    try:
        if request.method == "POST":
            name = request.form["name"]
            department = request.form["department"]
            designation = request.form["designation"]
            ext = request.form["ext"]
            if ext.isdigit() == False:
                flash("You can add only Numbers")
                return redirect("/")
            if ext == "":
                flash("Ext cannot be Null")
                return redirect("/")

            else:
                con = sqlite3.connect("directory.db")
                cur = con.cursor()
                cur.execute("INSERT into users(name, department, designation, ext) \
                 values (?,?,?,?);", (name, department, designation, ext,))
                # cur.execute("insert into Users (name, department, designation, ext) SELECT ?, ?, ?, ? \
                #      Where not exists(select * from Users where Ext=?)", (name, department, designation, ext, ext, ))
                con.commit()
                con.close()
                flash("Record Add successfully")
                return redirect("/")
    except sqlite3.IntegrityError:
        flash("Ext/Number Already Exist Kindly Add Multiple Name Against Ext")
        return redirect("/", )
    
@app.route("/edit", methods=['POST', 'GET'])
def edit():
    try:
        if request.method == "POST":
            userid = request.form["id"]
            name = request.form["name"]
            department = request.form["department"]
            designation = request.form["designation"]
            ext = request.form["ext"]
            if ext.isdigit() == False:
                flash("You can add only Numbers")
                return redirect("/")
            if ext == "":
                flash("Ext cannot be Null")
                return redirect("/")

            else:
                con = sqlite3.connect("directory.db")
                cur = con.cursor()
                cur.execute("UPDATE Users SET name=?, Department=?, Designation=?, Ext=? \
                WHERE ROWID= ?",
                            (name, department, designation, ext, userid))
                # cur.execute("UPDATE Users SET name=?, Department=?, Designation=?, Ext=? \
                #             WHERE ID= ? AND NOT EXISTS(SELECT ext FROM Users WHERE Ext = ?)",
                #             (name, department, designation, ext, userid, ext))
                con.commit()
                con.close()
                flash("Record Edit successfully")
                return redirect("/")
    except sqlite3.IntegrityError:
        flash("Ext/Number Already Exist Kindly Add Multiple Name Against Ext")
        return redirect("/", )
    
@app.route("/delete", methods=['POST', 'GET'])
def delete():
    if request.method == "GET":
        try:
            userid = request.args.get('entry_id')
            con = sqlite3.connect("directory.db")
            cur = con.cursor()
            cur.execute("DELETE FROM Users WHERE ROWID = ?", (userid,))
            con.commit()
            con.close()
        finally:
            flash("Record Deleted")
            return redirect("/")
    else:
        flash("not")
        return redirect("/")
    
    

@app.route("/import-export", methods=['POST', 'GET'] )
def setup():
    yml_data = yaml_data()
    choice = request.args.get('my_filename')
    
    path = "./static//*.csv"
    csv = glob.glob(path)
    test = ''.join(csv)

 
    return render_template("pages/pages/import-export.html", data=path, csv=test)

@app.route("/export", methods=['POST', 'GET'])
# def export():
#     con = get_db()
#     cur = con.cursor()
#     cur.execute("select * from users;")

#     choice = request.args.get('my_filename')
#     # choice = input("Please select a folder number: ")
#     file_path = os.path.join(export_folder, choice)

#     with open(file_path, 'w', newline='') as csv_file:
#         csv_writer = csv.writer(csv_file)
#         csv_writer.writerow([i[0] for i in cur.description])
#         csv_writer.writerows(cur)
#         con.close()
#         flash('file downloaded to ' + export_folder)
#         return redirect("/import-export")


def export():
        con = get_db()
        cur = con.cursor()
        clients = pd.read_sql('SELECT * FROM users;' ,con)
        clients.to_csv('static/data.csv', index=False)
        path = "static/data.csv"
        send_file(path, as_attachment=True)
        return redirect("/download_export")


@app.route('/download_export')
def export_csv():
            #For windows you need to use drive name [ex: F:/Example.pdf]
            path = "static/data.csv"
            return send_file(path, as_attachment=True)         
 
           

    










@app.route('/import', methods=['POST', 'GET'])
def success():
    if request.method == 'POST':
        try:
            f = request.files['file']
            if f.filename == '':
                flash('No File selected')

                return redirect("/import-export")

            if 'file' not in request.files:
                flash('Please Select Csv File Only')
                return redirect('/import-export')
        finally:
            try:
                f = request.files['file']
                f.save(os.path.join(upload_folder, secure_filename(f.filename)))
                # f.save('E:/testdata.csv')
                con = get_db()
                cur = con.cursor()
                o_file = open(os.path.join(upload_folder, f.filename), 'r')
                # o_file = open('E:/testdata.csv', 'r')
                next(reader(o_file))
                content = csv.reader(o_file)
                # cur.executemany('INSERT or ignore INTO users (id, name, department, designation, ext) \
                #                     VALUES (?, ?, ?, ?, ?);', content)
                cur.executemany('INSERT or ignore INTO users (id, name, department, designation, ext) \
                                                VALUES (?, ?, ?, ?, ?);', content)
                con.commit()
                con.close()

                flash("Data Imported")
                flash("Duplicate Data Ignored to Import")
                o_file.close()
                return redirect('/import-export')

            except sqlite3.IntegrityError as e:
                if str(e) == "UNIQUE constraint failed: users.ext":
                    flash('Please Remove Duplicate Ext')

                    return redirect('/import-export')
                if str(e) == "UNIQUE constraint failed: users.id":
                    flash('Please Duplicate in ID')
                    return redirect('/import-export')

            finally:

                return redirect("/import-export")
    else:
        return redirect("/import-export")
    
@app.route("/drop")
def drop():
    con = get_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("DROP TABLE users;")
    con.commit()
    con.close()

    return redirect("/")



@app.route("/dash")
def dash():
        return render_template('dash.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = 4244)