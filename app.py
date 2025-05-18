from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import time
import pymysql
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    os.getenv('DB_USER', 'root'),
    os.getenv('DB_PASSWORD', 'pass'),
    os.getenv('DB_HOST', 'flask_db'),
    os.getenv('DB_NAME', 'flask')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


def wait_for_db(host, port, user, password, db_name):
    while True:
        try:
            connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db_name
            )
            connection.close()
            print("馃煝 Database is ready!")
            break
        except pymysql.err.OperationalError:
            print("馃敶 Database not ready yet, waiting...")
            time.sleep(2)



wait_for_db(
    host=os.getenv('DB_HOST', 'flask_db'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', 'pass'),
    db_name=os.getenv('DB_NAME', 'flask')
)



class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)



with app.app_context():
    db.create_all()



@app.route('/', methods=["GET"])
def index():
    t = Todo.query.all()
    print(f"Todos: {t}")

    url = "https://api.chucknorris.io/jokes/random"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=5)

    print(f"Response status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Joke: {data['value']}")
        return render_template("index.html", list_todo=t, joke=data['value'])
    else:
        print("Error fetching joke")
        return "Error fetching joke"


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


if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'), debug=True)