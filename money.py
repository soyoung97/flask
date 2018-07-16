import os;
from flask import flash, redirect, url_for, send_from_directory, Flask, render_template, request
import json;
import sqlite3 as sql
import ast
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug import secure_filename
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/test', methods = ["POST","GET"])
def test():
    with sql.connect("money.db") as con:
        cur = con.cursor()
        string = "soyoung"
        for row in cur.execute("SELECT * FROM user where name == %s"%("\""+string+"\"")):
             unique_id, name, nickname, account_info = row
             string =str(unique_id)+name+nickname+account_info
             sample = [23,2]
             return json.dumps(sample)
    return "hello"

@app.route('/checkuser', methods = ["POST", "GET"])
def check_user():
    exists = False
    res = {}
    if request.method == 'POST':
        try:
            raw1 = request.data
            print(raw1)
            raw2 = raw1.decode("utf-8")
            print(raw2)
            real = ast.literal_eval(raw2)
            uid = real["unique_id"]
            print(uid)
            with sql.connect("money.db") as con:
                print("in checkuser")
                cur = con.cursor()
                query = ("SELECT * FROM user where unique_id == \"%s\""%(uid))
                print(query)
                for row in cur.execute(query):
                    exists = True
                    unique_id, name, nickname, account_info = row
                    res = {"result" : "Success", "name" : name, "nickname": nickname, "account_info" : account_info}
                    print("Printing res...")
                    print (res)
                    print("........done")
        except:
            con.rollback()
            print("Error in insert operation")
        finally:
            con.close()
    if exists == False:
        res = {"result" : "Failure"}
    return json.dumps(res)

@app.route('/make_new_user', methods = ["POST", "GET"])
def new_user():
    exists = False
    if request.method == 'POST':
        try:
            print(1)
            raw1 = request.data
            print(raw1)
            print(2)
            raw2 = raw1.decode("utf-8")
            print(3.5)
            real = ast.literal_eval(raw2)
            print(real)
            print(4)
            uid = real["unique_id"]
            print(uid)
            print(5)
            name = real["name"]
            print(name)
            print(6)
            nickname = real["nickname"]
            account_info = real["account_info"]
            print(7)
            with sql.connect("money.db") as con:
                cur = con.cursor()
                test = ("SELECT * FROM user where nickname == %s"%("\""+nickname+"\""))
                print(8)
                for row in cur.execute(test):
                    print(9)
                    exists = True
                print(10)
                insert = ("INSERT INTO user (unique_id, name, nickname, account_info) VALUES (\"%s\",\"%s\",\"%s\",\"%s\")"%(uid,name,nickname,account_info))
                print(insert)
                print(11)
                if exists == False:
                    cur.execute(insert)
                    print(12)
                    con.commit()
                    print ("Record successfully added: name %s"%name)
                print("This nickname currently already exists. please try another nickname")
        except:
            con.rollback()
            print("ERROR in insert operation")
        finally:
            con.close()
    if exists == True:
        return json.dumps({"result" : "Failure"})
    return json.dumps({"result": "Success"})

@app.route('/make_new_event', methods = ["POST", "GET"])
def new_event():
    if request.method == 'POST':
        try:
            data = request.data
            print(data)
            data = data.decode("utf-8")
            print(data)
            print("dskksdafjlasdfk")
            data = ast.literal_eval(data)
            print("dasfkj;lksdajfkl;asjdkl;fasdjasdkl;fjaskld;")
            print(data)
            creditor = data["creditor"]
            debtor = data["debtor"]
            price = data["price"]
            date = data["date"]
            info = data["info"]
            with sql.connect("money.db") as con:
                cur = con.cursor()
                exe = ("INSERT INTO event (creditor, debtor, price, date, info, repayment) VALUES (\"%s\", \"%s\", %d, \"%s\", \"%s\", %d)"%(creditor, debtor, price, date, info, 0) )
                print(exe)
                cur.execute(exe)
                con.commit()
                print ("Record successfully added: info %s"%info)
        except:
            con.rollback()
            res = json.dumps({"result":"Failure"})
            print("ERROR in insert operation")
        finally:
            con.close()
    res = json.dumps({"result":"Success"})
    return res
@app.route('/update_user', methods = ["POST", "GET"])
def update_user():
    print("in update_user")
    res = {}
    exists = False
    if request.method == 'POST':
        try:
            data = request.data
            print("DATA")
            print(data)
            data = data.decode("utf-8")
            data = ast.literal_eval(data)
            print("REALDATA")
            print(data)
            uid = data["unique_id"]
            name =  data["name"]
            nickname = data["nickname"]
            account_info = data["account_info"]
            with sql.connect("money.db") as con:
                print('connection successful')
                cur = con.cursor()
                query = ("SELECT * FROM user where unique_id == \"%s\""%uid);
                for row in cur.execute(query):
                    print("inside select moon~~~")
                    cur.execute("UPDATE user SET name = %s,nickname = %s, account_info = %s WHERE unique_id is \"%s\""%("\""+name+"\"", "\""+nickname+"\"", "\""+account_info+"\"", uid ));
                con.commit()
                res = {"result": "Success"}
                print ("Record successfully updated for name = %s", name)
        except:
            con.rollback()
            print("ERROR in update user operation")
            res = {"result": "Failure"}
        finally:
            con.close()
    return json.dumps(res)

@app.route('/search_by_name', methods = ["POST", "GET"])
def search_name():
    if request.method == 'POST':
        try:
            print("REQUEST start")
            data = request.data
            print(data)
            print(type(data))
            what = data.decode("utf-8")
            print(what)
            print(type(what))
            yeah = ast.literal_eval(what)
            print(yeah)
            print(type(yeah))
            print("did i print name?")
            name = yeah["name"]
            print(name)
            with sql.connect("money.db") as con:
                cur = con.cursor()
                ret=[]
                print("sql start:")

                mystr = ("SELECT * FROM user where name LIKE \'%%%s%%\'"%(name))
                print(mystr)
                res = cur.execute(mystr)
               # sql = "SELECT * FROM user where name LIKE \%%s\%"
               # cur.execute(sql,(name))
                print("after res")
                for row in res:
                    print("inside row")
                    uid, name, nickname, account_info = row
                    print(uid)
                    print(name)
                    print(nickname)
                    ret.append({"unique_id":uid, "name":name, "nickname":nickname})
                    print(json.dumps(ret))
        except:
            con.rollback()
            print("error in search by name")
        finally:
            print("FINAL")
            con.close()
    print("HI")
    return json.dumps(ret)



@app.route('/search_as_creditor', methods = ["POST", "GET"])
def creditor():
    if request.method == 'POST':
        res = []
        try:
            print("creditor start")
            data = ast.literal_eval(request.data.decode("utf-8"))
            print(data)
            uid = data["unique_id"]
            print("USER _ID : %s"%(uid))
            query = ("SELECT * FROM event where creditor == \"%s\""%uid)
            print(query)
            with sql.connect("money.db") as con:
                con = sql.connect("money.db")
                cur = con.cursor()
                print("IN MIDWHERE")
                for row in cur.execute(query):
                    print(row)
                    print("inside cur.execute(query)")
                    ID, creditor, debtor, price, date, repayment, info = row;
                    cur2 = con.cursor()
                    helper = ("SELECT unique_id, name, nickname FROM user where unique_id == \"%s\""%debtor)
                    print(helper)
                    for helpp in cur2.execute(helper):
                         uid, name, nickname = helpp
                         res.append({"ID":ID,"unique_id":uid,"name":name, "nickname":nickname, "price":price, "date": date, "info":info})
                         print(res)
        except:
            con.rollback()
            print("error in search_as_creditor")
        finally:
            print("FINAL")
            con.close()
    print("RESPONSE : %s"%(json.dumps(res)))
    return json.dumps(res)

@app.route('/find_account_info', methods = ["POST", "GET"])
def account():
    if request.method == "POST":
        print("REALSTART")
        try:
            print("starting find_account_info")
            data = ast.literal_eval(request.data.decode("utf-8"))
            uid = data["unique_id"]
            print("UID")
            print(uid)
            query = ("SELECT account_info FROM user where unique_id == \"%s\""%(uid))
            with sql.connect("money.db")as con:
                cur = con.cursor()
                for row in cur.execute(query):
                    res = {"result" : "Success", "account_info":row[0]}
                    print(res)
        except:
            res = {"result": "Failure"}
            con.rollback()
            print("error in find_account_info")
        finally:
            print("FINAL")
            con.close()
    return json.dumps(res)


@app.route('/search_as_debtor', methods = ["POST", "GET"])
def debtor():
    if request.method == 'POST':
        res = []
        try:
            print("debtor start")
            data = ast.literal_eval(request.data.decode("utf-8"))
            print(data)
            uid = data["unique_id"]
            #print("UID ISSSSSSSSSS")
            #print(uid)
            query = ("SELECT * FROM event where debtor == \"%s\""%(uid))
            #print(query)
            with sql.connect("money.db") as con:
                cur = con.cursor()
                #print("IN MIDWHERE")
                for row in cur.execute(query):
                    print("in cur.execute(query)")
                    ID, creditor, debtor, price, date, repayment, info = row;
                    cur2 = con.cursor()
                    print("WHAT IS THE MATTER")
                    helper = ("SELECT unique_id, name, nickname FROM user where unique_id == \"%s\""%creditor)
                    print(helper)
                    for helpp in cur2.execute(helper):
                        print("in for loop")
                        uid, name, nickname = helpp
                        res.append({"ID":ID,"unique_id":uid, "name":name, "nickname":nickname, "price":price, "date": date, "info":info})
                       # print(res)
        except:
            con.rollback()
            print("error in search_as_debtor")
        finally:
            print("FINAL")
            con.close()
    return json.dumps(res)

@app.route('/delete_event', methods = ["POST", "GET"])
def delete():
    if request.method == 'POST':
        res = {}
        try:
            print("delete start.")
            data = ast.literal_eval(request.data.decode("utf-8"))
            print(data)
            uid = data['ID']
            print(uid)
            query = ("DELETE FROM event WHERE ID == \"%s\""%(uid))
            print(query)
            with sql.connect("money.db") as con:
                cur = con.cursor()
                mid = cur.execute(query)
                res = {"result" : "Success"}
        except:
            con.rollback()
            print("error in delete")
            res = {"result" : "Failure"}
        finally:
            con.close()
    return json.dumps(res)



if __name__ == '__main__':
    app.debug == True
    app.run(host = '0.0.0.0', port = 8080, threaded = True, debug = True)
