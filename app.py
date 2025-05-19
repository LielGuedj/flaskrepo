import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# הגדרת החיבור לבסיס נתונים
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    os.getenv('DB_USER', 'root'),
    os.getenv('DB_PASSWORD', 'pass'),
    os.getenv('DB_HOST', 'flask_db'),
    os.getenv('DB_NAME', 'flask')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# הגדרת טבלה
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)



# ראוטים
@app.route('/', methods=["GET"])
def index():
    t = Todo.query.all()

    # נסיון להתחבר ל-API ולהביא ציטוט
    try:
        response = requests.get('https://zenquotes.io/api/random')

        # הדפסת התגובה הגולמית מה-API
        print("API Response Status Code:", response.status_code)  # סטטוס קוד של התגובה
        print("API Response Text:", response.text)  # התגובה הגולמית

        # אם הסטטוס קוד הוא 200 (הצלחה), נמשיך לפענח את התגובה
        if response.status_code == 200:
            data = response.json()  # המרת התגובה לפורמט JSON

            # הדפסת נתוני JSON שהתקבלו
            print("Data received from API:", data)

            # אם התגובה היא רשימה, ניגש לציטוט מתוך הנתונים
            if isinstance(data, list) and len(data) > 0:
                quote = data[0]['q']
                author = data[0]['a']
            else:
                quote = "ציטוט לא זמין כרגע"
                author = "המערכת"
        else:
            # אם הסטטוס קוד הוא לא 200, הציטוט לא יגיע
            print(f"Failed to fetch quote, status code: {response.status_code}")
            quote = "ציטוט לא זמין כרגע"
            author = "המערכת"

    except Exception as e:
        # אם יש בעיה בעת ביצוע הבקשה ל-API
        print(f"Error fetching quote: {e}")
        quote = "ציטוט לא זמין כרגע"
        author = "המערכת"

    # שולחים את הציטוט והמחבר ל-HTML
    print(f"Final Quote: {quote}, Author: {author}")  # הדפסת הציטוט לפני שמחזירים את התשובה
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
