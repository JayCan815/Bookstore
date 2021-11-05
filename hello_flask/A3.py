from flask import Flask, render_template, request
from flask_json import FlaskJSON, json_response
from Bcon import GetDb
import bcrypt
import json
import jwt

app = Flask(__name__)
FlaskJSON(app)

global_db_con = GetDb()
JWT_TOKEN = None
JWT_Secret = None


with open("secret.txt", "r") as f:
    JWT_SECRET = f.read()


@app.route("/", methods=["GET"]) 
def Index():
        return render_template("index.html")






@app.route("/loginauth", methods=["POST"])
def Login():

    
    cursor = global_db_con.cursor()
    cursor.execute("select username,password from users where username = '" + request.form["username"] + "';")
    
    res = cursor.fetchone()


    if res is None:
       return json_response(data={"message": "Username does not exist."},status='bad')
    else:

        pw = request.form["password"]
        saltedpw = bcrypt.hashpw(bytes(pw,"utf-8"),bcrypt.gensalt(10))
        

        if bcrypt.checkpw(bytes(request.form["password"],'utf-8'), bytes(res[1],'utf-8')) :
            global JWT_TOKEN
            JWT_TOKEN = jwt.encode({"user": res[0]}, JWT_SECRET, algorithm="HS256")
            return json_response(data={"jwt": JWT_TOKEN})
        else:
            return json_response(data = {"message": "Incorrect password."}, status='bad')






@app.route("/storepage",methods=["GET"])
def displaybooks():
    cursor = global_db_con.cursor()
    cursor.execute("select * from books");

    tok = request.args.get("jwt")
    

    if tok is None:
        print("ERROR")

    a = jwt.decode(JWT_TOKEN,JWT_SECRET,algorithms=["HS256"])
    b = jwt.decode(tok, JWT_SECRET, algorithms=["HS256"])

    if a == b:
        query = cursor.fetchall()
        return json_response(books = query)
    else:
        return json_response(data = {"message": "Unable to authenticate JWT."}, status='bad')
        
@app.route("/buy",methods=["GET"])
def buy():
    title = request.args.get("book_title")
    cursor = global_db_con.cursor()
    cursor.execute("UPDATE purchases SET pur = pur + 1 WHERE title LIKE'"+title+"%'" )
    global_db_con.commit();
    return json_response(data = {"message": "Purchase Successful!"}, status = 'good')

@app.route("/signup",methods=["POST"])
def signup():
    user =  request.form["username"]
    pw = request.form["password"]
    saltedpw = bcrypt.hashpw(bytes(pw, "utf-8"),bcrypt.gensalt(10))
    cur = global_db_con.cursor()
    cur.execute("INSERT INTO users (username,password) VALUES('"+ str(user) + "','" + saltedpw.decode("utf-8") + "');")
    global_db_con.commit()

    return json_response(data={"message": "Sign up complete."},status='good')


app.run(host="0.0.0.0", port=80)

