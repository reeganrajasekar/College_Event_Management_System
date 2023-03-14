from flask import Flask, render_template , request , redirect, session , make_response , Response
import sqlite3
import io , csv
from werkzeug.utils import secure_filename
app = Flask(__name__, static_url_path='/static')
app.secret_key = "crth5yjt7ynp98un"

@app.route("/")  
def index():
    return render_template("index.html")

@app.route("/login", methods =["GET", "POST"])  
def login():
    if request.method == "POST":
        con = sqlite3.connect("database.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from user WHERE email=? AND password=?",(request.form["email"],request.form["password"]))  
        rows = cur.fetchall()
        if len(rows)>0:
            for row in rows:
                session['user']=row["id"]
            return redirect("/home")
        else:
            return redirect("/?err=email or password is wrong!")
    return redirect("/?err=email or password is wrong!")

@app.route("/home")  
def home():
    if 'user' in session:
        user = session['user']
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from event WHERE did=? AND file='No' AND date between date('now','-2 days') AND date('now','0 days') ORDER BY id DESC",(str(user)))  
    rows = cur.fetchall()
    cur.execute("select * from event WHERE did=? AND date<date('now','-1 days') AND file='No' ORDER BY id DESC",(str(user)))  
    old = cur.fetchall()
    return render_template("home.html",rows=rows,old=old)

@app.route("/event")  
def event():
    if 'user' in session:
        user = session['user']
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from event WHERE did=? AND file='No' AND date>date('now','0 years') ORDER BY id DESC",(str(user)))  
    rows = cur.fetchall()
    cur.execute("select * from event WHERE did=? AND NOT file='No' ORDER BY id DESC",(str(user)))  
    old = cur.fetchall()
    return render_template("event.html",rows=rows,old=old)

@app.route("/event/add",methods=["GET","POST"])  
def event_add():
    if request.method == "POST":
        if 'user' in session:
            user = session['user']
        con = sqlite3.connect("database.db")
        con.execute("INSERT into event(event,desc,date,file,did) values (?,?,?,?,?)",(request.form["event"],request.form["desc"],request.form["date"],"No",user))
        con.commit()
        return redirect("/event?msg=Event added Successfully!")
    return redirect("/")

@app.route("/event/upload",methods=["GET","POST"])  
def event_upload():
    if request.method == "POST":
        f = request.files['file']
        file_name = secure_filename(f.filename)
        f.save("static/uploads/"+file_name)
        con = sqlite3.connect("database.db")
        con.execute("UPDATE event SET file=? WHERE id=?",(file_name,request.form["id"]))
        con.commit()
        return redirect("/home?msg=Event Document added Successfully!")
    return redirect("/")

@app.route("/admin")  
def admin():
    return render_template("admin/login.html")

@app.route("/admin/login", methods =["GET", "POST"])  
def admin_login():
    if request.method == "POST":
        if request.form["email"]=="admin@gmail.com" and request.form["password"]=="admin":
            return redirect("/admin/home")
        else:
            return redirect("/admin?err=email or password is wrong!")
    return redirect("/admin?err=email or password is wrong!")

@app.route("/admin/home")  
def admin_home():  
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from event WHERE date<date('now','-1 days') AND file='No' ORDER BY id DESC")  
    rows = cur.fetchall()
    return render_template("admin/home.html",rows = rows)

@app.route("/admin/event/enable",methods=["GET","POST"])  
def event_enable():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("UPDATE event SET date=? WHERE id=?",(request.form["date"],request.form["id"]))
        con.commit()
        return redirect("/admin/home?msg=Event Access Granted Successfully!")
    return redirect("/")

@app.route("/admin/user")  
def admin_user():  
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from user ORDER BY id DESC")  
    rows = cur.fetchall()
    return render_template("admin/user.html",rows = rows)

@app.route("/admin/user/add", methods =["GET", "POST"])  
def admin_user_add():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("INSERT into user(dept, email, password) values (?,?,?)",(request.form["dept"],request.form["email"],request.form["password"]))
        con.commit()
        return redirect("/admin/user?msg=Department added Successfully!")
    return redirect("/admin")

@app.route("/admin/report")  
def admin_report():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()
    cur.execute("select DISTINCT id , dept from user")  
    rows = cur.fetchall()
    return render_template("admin/report.html",rows=rows)

@app.route("/admin/report/download", methods =["GET", "POST"])  
def admin_report_download():  
    if request.method == "POST":
        con = sqlite3.connect("database.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()
        cur.execute("select * from event WHERE did=? AND NOT file='No'",(request.form["id"]))  
        rows = cur.fetchall()
        if len(rows)>0:
            line ="Event Id, Event Title, Event Description ,Planned Date"
            for row in rows:
                line = line+"\n"+str(row["id"])+","+row["event"]+","+row["desc"]+","+row["date"]
            print(line)
            return Response(line, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=employee_report.csv"})
            return redirect("/admin/report?msg=Report Generated Successfully!")
        else:
            return redirect("/admin/report?err=Zero Events Found!")
    return redirect("/")

@app.route("/table")
def table():
    con = sqlite3.connect("database.db")
    con.execute("CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT,dept TEXT NOT NULL,email TEXT NOT NULL,password TEXT NOT NULL)")
    con.execute("CREATE TABLE event(id INTEGER PRIMARY KEY AUTOINCREMENT,did INTEGER NOT NULL,date DATE NOT NULL,file TEXT NOT NULL,event TEXT NOT NULL,desc TEXT NOT NULL)")
    return "Table Created"