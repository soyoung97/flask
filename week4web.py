import os;
from flask import flash, redirect, url_for, send_from_directory, Flask, render_template, request
import json;
import sqlite3 as sql
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug import secure_filename
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16* 1024 * 1024
UPLOAD_FOLDER = '/home/soyoung/photos'
ALLOWED_EXTENTIONS = set(['txt','pdf','png','jpg','jpeg','gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
   return render_template('week4home.html')

@app.route('/enternew')
def new_student():
   return render_template('student.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
   if request.method == 'POST':
      try:
         nm = request.form['nm']
         addr = request.form['add']
         city = request.form['city']
         pin = request.form['pin']
         print(1)
         with sql.connect("database.db") as con:
            cur = con.cursor()
            print(2)
            cur.execute("INSERT INTO student (name,addr,city,pin) VALUES (?,?,?,?)",(nm,addr,city,pin) )
            print(3)
            con.commit()
            print(4)
            msg = "Record successfully added"
      except:
         print(5)
         con.rollback()
         print(6)
         msg = "error in insert operation"
      
      finally:
         return render_template("result.html",msg = msg)
         con.close()

@app.route('/list')
def list():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from student")
   
   rows = cur.fetchall();
   return render_template("list.html",rows = rows)

#loadData: Display information on db as Json 
@app.route("/loadData", methods=["GET", "POST"])
def loadData():
    cursor = sql.connect("database.db").cursor();
    cursor.execute("select * from student")
    result = []
    columns = tuple( [d[0] for d in cursor.description] )
    for row in cursor:
        result.append(dict(zip(columns, row)))
    print(result);
    return json.dumps(result);

#upLoad: picture upload, and save information about postings in DB.
@app.route('/upload')
def upload():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                            secure_filename(f.filename)))
      return redirect(url_for('uploaded_file', filename=secure_filename(f.filename)))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/getphotos', methods = ["GET"])
def getphotos():
    ret_file_list = []
    for file_name in os.listdir('/home/soyoung/photos'):
        ret_file_list.append(file_name)
    print(ret_file_list)
    return json.dumps(ret_file_list)

@app.route('/fromandroid', methods = ["POST"])
def uploadfromandroid():
    print("whatthehell!!!")
    if request.method == 'POST':
        print("THis is CRAZY")
        #f = request.files['file']
        #print(type(f));
        #print(f);
        for key in request.files.keys():
            print(key)

        obj = request.files.getlist('uploaded_file')
        print(obj)
        tmp = obj[0]
        #print(request.files.getlist('uploaded_file'));
        tmp.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                    secure_filename(tmp.filename)))
        print(2000);
        return redirect(url_for('uploaded_file', filename=secure_filename(tmp.filename)))
       
@app.route('/uploadAudio', methods = ["POST"])
def uploadAudio():
    print("in uploadaudio")
    if request.method == 'POST':
        print("in second")
        print(request.files['file'])
        print(request.files.getlist)
        for key in request.files.keys():
            print(key)
    print(g)


if __name__ == '__main__':
   app.debug = True
   app.run(host = '0.0.0.0', port = 8080, threaded=True)

