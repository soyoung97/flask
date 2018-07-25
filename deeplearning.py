import os
from flask import flash, redirect, url_for, send_from_directory, Flask, render_template, request
import model
import json
import sqlite3 as sql
from werkzeug import secure_filename
UPLOAD_FOLDER = '/home/soyoung/static'
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#uinfo : id , pwd

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "-1"
    r.headers['Cache-Control'] = 'public, max-age=0'
    r.headers["X-UA-Compatible"] = "IE=Edge, chrome = 1"
    return r

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/register', methods = ["POST", "GET"])
def register():
    exists = False
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            with sql.connect("site.db") as con:
                cur = con.cursor()
                query = ("SELECT * FROM uinfo where id == \"%s\""%(username))
                print(query)
                for row in cur.execute(query):
                    print("already exists")
                    exists = True
                if exists == True:
                    print("current id already exists. please try another id.")
                else:
                    query_1 = ("INSERT INTO uinfo (id, pwd) VALUES (\"%s\", \"%s\")"%(username, password))
                    cur.execute(query_1)
                    print("registeration success! please log in with this id")
        except:
            con.rollback()
            print("error in register")
        finally:
            con.close()

    return render_template('register.html')

@app.route("/login", methods = ["POST", "GET"])
def login():
    success = False
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            with sql.connect("site.db") as con:
                cur = con.cursor()
                query = ("SELECT * FROM uinfo where id == \"%s\" and pwd == \"%s\""%(username,password))
                print(query)
                for row in cur.execute(query):
                    success = True
                    print("login success")
                    full_filename = os.path.join(app.config["UPLOAD_FOLDER"], "cat.jpg")
                    print("asdklfjaskl;df")
                    print(full_filename)
                    return render_template("week4home.html")#, #sample_image = full_filename)
                    #flash("login success")
                if success == False:
                    print("login failed")
                    return render_template("loginfailed.html")
                    #flash("login failed")
        except:
            con.rollback()
            print("error in login")
        finally:
            con.close()
    return render_template("login.html")
@app.route("/black_image", methods = ["POST","GET"])
def blackimage():
    if request.method == "POST":
        f = request.files['file']
        print("got file. filename = %s"%f.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
        f.save(file_path)
        print("saved. file path = %s"%file_path)
        output = model.MODEL(file_path).Make()
        #with open(os.path.join(app.config["UPLOAD_FOLDER"], output)) as f:
        #    f.read()
        print("output -------> ",output)
        #output = file_path
        return redirect(url_for('uploaded_file', filename= output))
        #return render_template("return_image.html", imgpath = output )
    return render_template("black_image.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080, threaded = True)
