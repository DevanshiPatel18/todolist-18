from flask import Flask, render_template, url_for, request, session, redirect, jsonify,flash,app
from bson.json_util import dumps, ObjectId
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
import json
from datetime import timedelta

app = Flask(__name__)
app.secret_key="secretkey"

app.config["MONGO_URI"]= "mongodb+srv://devanshi:I58dsdwAuh47EEow@cluster0-8jifm.mongodb.net/mydb?retryWrites=true&w=majority"
app.config["MONGO_DB"] = "mydb"

mongo = PyMongo(app)

@app.route("/")
def index():
    return render_template("login.html")

@app.after_request
def after_request(response):
    if "id" and "user" in session:
        return response
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route("/signup.html")
def i():
    return render_template("signup.html")

@app.route("/timeout")
def timeout():
    return render_template("sessiontimeout.html")

@app.route("/signup",methods=["POST"])
def signup():
    a = request.form['username']
    b = request.form['pwd']
    c = request.form['cpwd']

    if a and b and c and request.method == "POST":
       
        _hashed = generate_password_hash(b)

        if check_password_hash(_hashed,c):
            i = mongo.db.user.insert({"name":a,"password":_hashed})
            if i:
                return render_template("login.html")
        flash("The passwords do not match")

@app.route("/login" , methods=["POST"])
def login():
    a = request.form["username"]
    b = request.form["pwd"]

    if a and b and request.method == "POST":

        id = mongo.db.user.find({'name': a})
        if id:
            temp=""
            for i in id:
                temp  = i['password']
                user = a
                user_id = i['_id']
                session['id'] = json.dumps(user_id,default=str)
                session['user'] = user
            if check_password_hash(temp,b):
                todos = mongo.db.todolist.find({"name":a})
                return render_template("todolist.html",user=user,id=user_id,todo=todos)
        flash("Wrong login credentials.")
        return render_template("login.html")
    return render_template("login.html")

@app.route("/display")
def dis():
    if session.get('id') and session.get('user'):
        id = session['id']
        user = session['user']
        l = mongo.db.todolist.find({"user":id})
        if l :
            return render_template("todolist.html",user=user,id=id,todo=l)
    return redirect(url_for("timeout"))

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

@app.route("/add",methods=["POST"])
def add():
    if session.get('id') and session.get('user'):
        user_id = str(session['id'])
        user = session['user']
        task = request.form["task"]
        taskdesc = request.form["taskdesc"]
        priority = request.form["priority"]
        date = request.form['date']

        id = mongo.db.todolist.insert_one({"user":user_id,"name":user,"date": date,"task":task,"taskdesc":taskdesc,"priority":priority,"status":"no"})

        if id:
            return redirect(url_for("dis"))

    return redirect(url_for("timeout"))

@app.route("/logout",methods=["POST"])
def log_out():
    session.pop("user",None)
    session.pop("id",None)

    return render_template("login.html")

@app.route("/delete",methods=["GET"]) 
def delete():
    if session.get("user") and session.get("id"):
        id = request.values.get("j")
        if id:
            s = mongo.db.todolist.remove({"_id":ObjectId(id)})
            if s:
                return redirect(url_for("dis"))

@app.route("/modify",methods=["GET"]) 
def modify():
    if session.get("user") and session.get("id"):
        id = request.values.get("k")
        user = session['id']
        j = mongo.db.todolist.find({"user":user,"_id":ObjectId(id)})
        if j:
            return render_template("update.html",rec=j)

@app.route("/edit",methods=["POST"])
def edit():
    if session.get("user") and session.get("id"):
        user_id = session.get("id")
        user = session.get("user")
        task = request.values.get("task")
        taskdesc = request.values.get("taskdesc")
        priority = request.values.get("priority")
        date = request.values.get("date")
        status = request.values.get("status")

        updated = mongo.db.todolist.update_one({"user":user_id,"name":user},{"$set": {"task":task,"taskdesc":taskdesc,"priority":priority,"date":date,"status":status}})

        if updated:
            return redirect(url_for("dis"))

if __name__ == "__main__":
     app.run(debug=True)