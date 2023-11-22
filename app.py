from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://asafbilker:4289190498@localhost/taskmanager'
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)  # Add this line


# Create User model
class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)


# Create Task model
class Task(db.Model):
    __tablename__ = 'task'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('public.user.id'), nullable=False)


@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', welcome_message=f"Welcome back to Your ToDo App, {user.username}!")
    else:
        return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            return jsonify({'success': True, 'redirect': url_for('login')})

        elif existing_user:
            return jsonify({'yesUserE': True})
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return jsonify({'loggedIn': True, 'redirect': url_for('home')})
        elif user:
            return jsonify({'passE': True})
        elif not user:
            return jsonify({'userE': True})
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        content = request.form['content']
        new_task = Task(content=content, user_id=user.id, completed=False)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('tasks'))
    return redirect(url_for('login'))


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user_id' in session:
        task = Task.query.get(task_id)
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('tasks'))
    return redirect(url_for('login'))


"""
@app.route('/toggle_task', methods=['POST'])
def toggle_task():
    if 'user_id' in session:
        try:
            # Get the task ID and completed status from the request JSON
            data = request.get_json()
            task_id = data.get('taskId')
            completed = data.get('completed')

            # Update the task in the database
            task = Task.query.get(task_id)

            if task:
                task.completed = completed
                db.session.commit()
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Task not found'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'success': False, 'error': 'User not authenticated'})



@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

        if request.method == 'POST':
            # Handle form submission for updating completed tasks
            task_ids = request.form.getlist('task_ids[]')
            for task_id in task_ids:
                task = Task.query.get(task_id)
                task.completed = not task.completed

            db.session.commit()
            return jsonify({'success': True})

        # Handle initial page load and return HTML
        tasks = Task.query.filter_by(user_id=user.id).all()
        return render_template('tasks.html', tasks=tasks)

    return redirect(url_for('login'))
"""


@app.route('/toggle_task', methods=['POST'])
def toggle_task():
    if 'user_id' in session:

        # Get the task ID and completed status from the request JSON
        data = request.get_json()
        task_id = data.get('taskId')


        # Update the task in the database
        task = Task.query.get(task_id)

        # If completed status is provided, update it; otherwise, toggle it

        task.completed = not task.completed

        db.session.commit()
        return jsonify({'success': True})
    return redirect(url_for('login'))


@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

        # Handle initial page load and return HTML
        tasks = Task.query.filter_by(user_id=user.id).all()
        return render_template('tasks.html', tasks=tasks)

    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
