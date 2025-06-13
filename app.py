import requests
import time
import pymysql
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# ✨ הגדרת SQLAlchemy מחוץ ל־Flask
db = SQLAlchemy()

# 🕒 פונקציה שמוודאת שה-MySQL מוכן
def wait_for_mysql():
    host = os.getenv("DB_HOST", "flask_db")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "pass")
    database = os.getenv("DB_NAME", "flask")

    for i in range(30):  # עד 90 שניות
        try:
            conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            conn.close()
            print("✅ Connected to MySQL successfully!")
            return
        except pymysql.err.OperationalError:
            print(f"⏳ MySQL not ready yet ({i+1}/30)... Retrying in 3 seconds.")
            time.sleep(3)
    raise Exception("❌ Could not connect to MySQL.")

# ✨ מוודאים שה-MySQL מוכן לפני שממשיכים
wait_for_mysql()

app = Flask(__name__)

# הגדרת החיבור לבסיס נתונים
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    os.getenv('DB_USER', 'root'),
    os.getenv('DB_PASSWORD', 'pass'),
    os.getenv('DB_HOST', 'flask_db'),
    os.getenv('DB_NAME', 'flask')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✨ התחברות ל־SQLAlchemy רק עכשיו
db.init_app(app)

# הגדרת טבלה
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)

# יצירת טבלאות עם עליית השרת
with app.app_context():
    db.create_all()

# ראוטים
@app.route('/', methods=["GET"])
def index():
    t = Todo.query.all()

    try:
        response = requests.get('https://zenquotes.io/api/random')
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                quote = data[0]['q']
                author = data[0]['a']
            else:
                quote = "ציטוט לא זמין כרגע"
                author = "המערכת"
        else:
            quote = "ציטוט לא זמין כרגע"
            author = "המערכת"
    except Exception as e:
        print(f"Error fetching quote: {e}")
        quote = "ציטוט לא זמין כרגע"
        author = "המערכת"

    return render_template("index.html", list_todo=t, quote=quote, author=author)

@app.route('/add', methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/update/<int:todo_id>')
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))

# הרצת השרת
if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'), debug=True)
