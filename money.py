import os;
from flask import flash, redirect, url_for, send_from_directory, Flask, render_template, request
import json;
import sqlite3 as sql
import ast
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug import secure_filename
from pyfcm import FCMNotification
import requests


app = Flask(__name__)

def printit(str):
    print("----------------------------Inside %s function---------------------------------"%str)

def getdata(data):
    print(" got data ")
    ret = ast.literal_eval(data.decode("utf-8"))
    print(ret)
    return ret

@app.route("/delete_event", methods = ["POST", "GET"])
def delete_event():
    res = {}
    printit("delete_event")
    if request.method == "POST":
        try:
            print("1")
            data = getdata(request.data)
            ide = data["ID"]
            print("id")
            print(ide)
            query = ("DELETE FROM event WHERE ID == %d"%ide)
            print(query)
            with sql.connect("money.db") as con:
                cur = con.cursor()
                print("2")
                cur.execute(query)
                print("3")
                res = {"result" : "Success"}
        except:
            con.rollback()
            print("4")
            res = {"result" : "Failure"}
            print("Error in delete event")
        finally:
            con.close()
        return json.dumps(res)


@app.route("/changeToken", methods = ["POST","GET"])
def change():
    printit("changeToken")
    res = {}
    if request.method == "POST":
        try:
            data = getdata(request.data)
            unique_id = data["unique_id"]
            token = data["token"]
            query = ("UPDATE user SET token = \"%s\" where unique_id == \"%s\""%(token, unique_id))
            with sql.connect("money.db") as con:
                cur = con.cursor()
                cur.execute(query)
            res = {"result" : "Success"}
        except:
            con.rollback()
            res = {"result" : "Failure"}
            print("Error in update token")
        finally:
            con.close()
        return json.dumps(res)


@app.route("/push", methods = ["POST","GET"])
def push():
    printit("push")
    api =" AAAApvAniuI:APA91bFReX5VxHZdCxO6f0cAo7DkNoKnpsaEOhgi-IN-Q-qxyHqGBA2PtyLyDhs1WUQhy0eFXk_fQ7e31G-j4N9rfjNpfFlGURzLQEtFYFIUFx602FTn5sSrvt-mEivE4uXOvdB0dxIoeqCGobIX92gZm8lJ2460dQ"
    message_title = 'Soyoung_title'
    if request.method == 'POST':
        try:
            push_service = FCMNotification(api_key=api)
            data = getdata(request.data)
            unique_id = data["unique_id"]
            ID = data["ID"]
            user_query = ("SELECT * FROM user where unique_id == \"%s\""%unique_id)
            event_query = ("SELECT * FROM event where ID == %s"%ID)
            with sql.connect("money.db") as con:
                cur = con.cursor()
                for row in cur.execute(user_query):
                    unique_id, name, nickname, account_info, token = row
                    cur2 = con.cursor()
                    for event in cur2.execute(event_query):
                        ID, creditor, debtor, price, date, repayment, info = event
                        cur3 = con.cursor()
                        for sendtoken in cur3.execute("SELECT token from user where unique_id ==\"%s\""%debtor):
                            real = sendtoken[0]
                        message_body = {"name":name, "nickname":nickname, "info":info,"price":price, "date":date, "creditor_unique_id": unique_id}
            res =push_service.notify_single_device(registration_id= real, message_title = message_title, message_body = message_body)
            print("SENT -> %s"%res)



     #       url =  "https://fcm.googleapis.com/fcm/send"
     #       auth = ('Authorization: key = %s'%api)
     #       headers = {auth, 'Content-Type: application/json',}
     #       datareal = {"message":{ "notification":{"title":message_title, "body":message_body,},"token":real}}
     #       datareal = str(datareal)
     #       responce = requests.post(url, headers = headers, data = datareal)
     #       print("OHMYGOD DID IT SUCCEED!>!>!>!!??!?!")
     #       print(responce)
        except:
            con.rollback()
            print("error in push. TT")
        finally:
            con.close()
    return json.dumps({"result":"Success"})

@app.route('/')
def home():
    return "hi, this server is not for web browsing. please use the money app :)"

@app.route('/checkuser', methods = ["POST", "GET"])
def check_user():
    printit("check_user")
    exists = False
    res = {}
    if request.method == 'POST':
        try:
            real = getdata(request.data)
            uid = real["unique_id"]
            with sql.connect("money.db") as con:
                cur = con.cursor()
                query = ("SELECT * FROM user where unique_id == \"%s\""%(uid))
                for row in cur.execute(query):
                    exists = True
                    unique_id, name, nickname, account_info, token = row
                    res = {"result" : "Success", "name" : name, "nickname": nickname, "account_info" : account_info}
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
    printit("new_user")
    exists = False
    if request.method == 'POST':
        try:
            real = getdata(request.data)
            uid = real["unique_id"]
            name = real["name"]
            nickname = real["nickname"]
            account_info = real["account_info"]
            token = real["token"]
            with sql.connect("money.db") as con:
                cur = con.cursor()
                test = ("SELECT * FROM user where nickname == %s"%("\""+nickname+"\""))
                for row in cur.execute(test):
                    exists = True
                insert = ("INSERT INTO user (unique_id, name, nickname, account_info, token) VALUES (\"%s\",\"%s\",\"%s\",\"%s\", \"%s\")"%(uid,name,nickname,account_info, token))
                if exists == False:
                    cur.execute(insert)
                    con.commit()
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
    printit("new_event")
    res = {}
    if request.method == 'POST':
        try:
            data = getdata(request.data)
            creditor = data["creditor"]
            debtor = data["debtor"]
            price = data["price"]
            date = data["date"]
            info = data["info"]
            with sql.connect("money.db") as con:
                cur = con.cursor()
                exe = ("INSERT INTO event (creditor, debtor, price, date, info, repayment) VALUES (\"%s\", \"%s\", %d, \"%s\", \"%s\", %d)"%(creditor, debtor, price, date, info, 0) )
                cur.execute(exe)
                con.commit()
                res = {"result":"Success"}
                print ("Record successfully added: info %s"%info)
        except:
            con.rollback()
            res = json.dumps({"result":"Failure"})
            print("ERROR in insert operation")
        finally:
            con.close()
    return (json.dumps(res))

@app.route('/update_user', methods = ["POST", "GET"])
def update_user():
    printit("update_user")
    res = {}
    exists = False
    if request.method == 'POST':
        try:
            data = getdata(request.data)
            uid = data["unique_id"]
            name =  data["name"]
            nickname = data["nickname"]
            account_info = data["account_info"]
            with sql.connect("money.db") as con:
                cur = con.cursor()
                query = ("SELECT * FROM user where unique_id == \"%s\""%uid);
                for row in cur.execute(query):
                    cur.execute("UPDATE user SET name = %s,nickname = %s, account_info = %s WHERE unique_id is \"%s\""%("\""+name+"\"", "\""+nickname+"\"", "\""+account_info+"\"", uid ));
                con.commit()
                res = {"result": "Success"}
                print ("Record successfully updated for name = %s"%name)
        except:
            con.rollback()
            print("ERROR in update user operation")
            res = {"result": "Failure"}
        finally:
            con.close()
    return json.dumps(res)

@app.route('/search_by_name', methods = ["POST", "GET"])
def search_name():
    printit("search_name")
    if request.method == 'POST':
        try:
            data = getdata(request.data)
            name = data["name"]
            with sql.connect("money.db") as con:
                cur = con.cursor()
                ret=[]
                mystr = ("SELECT * FROM user where name or nickname LIKE \'%%%s%%\'"%(name))
                res = cur.execute(mystr)
                for row in res:
                    uid, name, nickname, account_info, token = row
                    ret.append({"unique_id":uid, "name":name, "nickname":nickname})
        except:
            con.rollback()
            print("error in search by name")
        finally:
            con.close()
    return json.dumps(ret)

@app.route('/search_as_creditor', methods = ["POST", "GET"])
def creditor():
    printit("creditor")
    if request.method == 'POST':
        res = []
        try:
            data = getdata(request.data)
            uid = data["unique_id"]
            query = ("SELECT * FROM event where creditor == \"%s\""%uid)
            with sql.connect("money.db") as con:
                con = sql.connect("money.db")
                cur = con.cursor()
                for row in cur.execute(query):
                    ID, creditor, debtor, price, date, repayment, info = row;
                    cur2 = con.cursor()
                    helper = ("SELECT unique_id, name, nickname FROM user where unique_id == \"%s\""%debtor)
                    for helpp in cur2.execute(helper):
                         uid, name, nickname = helpp
                         res.append({"ID":ID,"unique_id":uid,"name":name, "nickname":nickname, "price":price, "date": date, "info":info})
        except:
            con.rollback()
            print("error in search_as_creditor")
        finally:
            con.close()
    return json.dumps(res)

@app.route('/find_account_info', methods = ["POST", "GET"])
def account():
    printit("find_account_info")
    if request.method == "POST":
        try:
            data = getdata(request.data)
            uid = data["unique_id"]
            query = ("SELECT account_info FROM user where unique_id == \"%s\""%(uid))
            with sql.connect("money.db")as con:
                cur = con.cursor()
                for row in cur.execute(query):
                    res = {"result" : "Success", "account_info":row[0]}
        except:
            res = {"result": "Failure"}
            con.rollback()
            print("error in find_account_info")
        finally:
            con.close()
    return json.dumps(res)

@app.route('/search_as_debtor', methods = ["POST", "GET"])
def debtor():
    printit("search_as_debtor")
    if request.method == 'POST':
        res = []
        try:
            data = getdata(request.data)
            uid = data["unique_id"]
            query = ("SELECT * FROM event where debtor == \"%s\""%(uid))
            with sql.connect("money.db") as con:
                cur = con.cursor()
                for row in cur.execute(query):
                    ID, creditor, debtor, price, date, repayment, info = row;
                    cur2 = con.cursor()
                    helper = ("SELECT unique_id, name, nickname FROM user where unique_id == \"%s\""%creditor)
                    for helpp in cur2.execute(helper):
                        uid, name, nickname = helpp
                        res.append({"ID":ID,"unique_id":uid, "name":name, "nickname":nickname, "price":price, "date": date, "info":info})
        except:
            con.rollback()
            print("error in search_as_debtor")
        finally:
            con.close()
    return json.dumps(res)

if __name__ == '__main__':
    app.debug == True
    app.run(host = '0.0.0.0', port = 8080, threaded = True, debug = True)
