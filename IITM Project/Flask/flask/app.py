from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy  # type:ignore
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.secret_key = 'your_secret_key_here'  # Required for flash messages and sessions
db = SQLAlchemy(app)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.String)
    duration = db.Column(db.String)

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    noq = db.Column(db.Integer, nullable = False)
    date = db.Column(db.String)
    score = db.Column(db.String)

class Subject(db.Model):
    sub_id = db.Column(db.Integer, primary_key = True)
    sub_name = db.Column(db.String)
    sub_desc = db.Column(db.String)

class Chapter(db.Model):
    ch_id = db.Column(db.Integer, primary_key = True)
    ch_name = db.Column(db.String)
    noq = db.Column(db.String)

class Question(db.Model):
    qid = db.Column(db.Integer, primary_key = True)
    qtitle = db.Column(db.String, nullable = False)
    question = db.Column(db.String)
    qo1 = db.Column(db.String)
    qo2 = db.Column(db.String)
    qo3 = db.Column(db.String)
    qo4 = db.Column(db.String)
    qco = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    fullname = db.Column(db.String(100))
    qualification = db.Column(db.String(100))
    dob = db.Column(db.String(20))

with app.app_context():
    db.create_all()  

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate input
        if not email or not password:
            flash('Please enter both email and password')
            return render_template('login.html')
            
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            # Set session
            session['user_id'] = user.id
            session['user_email'] = user.email
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')
        
        # Validate input
        if not email or not password:
            flash('Please enter both email and password')
            return render_template('register.html')
            
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered')
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email, 
            password=hashed_password,
            fullname=fullname,
            qualification=qualification,
            dob=dob
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    return redirect(url_for('home'))

@app.route('/user_dashboard')
def user_dashboard():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access the dashboard')
        return redirect(url_for('login'))
        
    all_quizzes = Quiz.query.all()
    return render_template('user_dashboard.html', all_quizzes=all_quizzes)

@app.route('/viewquiz/<int:id>')
def view(id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access this page')
        return redirect(url_for('login'))
        
    required_quiz = Quiz.query.filter_by(id = id).first()
    return render_template('viewquiz.html', required_quiz = required_quiz)

@app.route('/start_exam/<int:id>')
def start_exam(id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to start an exam')
        return redirect(url_for('login'))
        
    exam = Quiz.query.filter_by(id = id).first()
    return render_template('start_exam.html', exam = exam)

@app.route('/scores')
def scroes():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to view scores')
        return redirect(url_for('login'))
        
    all_scores = Scores.query.all()
    return render_template('scores.html', all_scores = all_scores)

@app.route('/summary')
def summary():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to view summary')
        return redirect(url_for('login'))
        
    return render_template('summary.html')

@app.route('/admin')
def admin():
    all_chapters = Chapter.query.all()
    all_subjects = Subject.query.all()
    return render_template('admin.html', all_chapters=all_chapters, all_subjects=all_subjects)
 

@app.route('/new_chapter', methods=['GET', 'POST'])
def new_chapter():
    if request.method == 'POST':
        chname = request.form['chname']
        chnoq = request.form['chnoq']
        new_chapter = Chapter(ch_name=chname, noq=chnoq)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect('/admin')  # Redirect after adding
    return render_template('new_chapter.html')

    
@app.route('/delete_chapter/<ch_name>')
def delete(ch_name):
    chapter_to_delete = Chapter.query.filter_by(ch_name = ch_name).first()
    db.session.delete(chapter_to_delete)
    db.session.commit()
    return redirect('/admin')

@app.route('/new_subject', methods=['GET', 'POST'])
def new_subject():
    if request.method == 'POST':
        sub_name = request.form['subname']
        new_subject = Subject(sub_name=sub_name)
        db.session.add(new_subject)
        db.session.commit()
        return redirect('/admin')  # Redirect after adding
    return render_template('new_subject.html')

@app.route('/admin_summary')
def admin_summary():
    return render_template('admin_summary.html')

@app.route('/quiz_manager')
def quiz_manager():
    return render_template('quiz_manager.html')

@app.route('/new_question')
def new_question():
    return render_template('new_question.html')

@app.route('/new_quiz')
def new_quiz():
    return render_template('new_quiz.html')

@app.route('/profile')
def profile():
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            flash('Please log in to view your profile')
            return redirect(url_for('login'))
            
        # Get user information from database
        user = User.query.filter_by(id=session['user_id']).first()
        
        if not user:
            flash('User not found')
            return redirect(url_for('login'))
        
        # For demonstration, we're using dummy data for activity and achievements
        # In a real application, you would fetch this from the database
        
        return render_template('profile.html', user=user)
    except Exception as e:
        print(f"Error in profile route: {e}")
        flash('An error occurred while loading your profile')
        return redirect(url_for('user_dashboard'))

@app.route('/settings')
def settings():
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            flash('Please log in to access settings')
            return redirect(url_for('login'))
            
        # Get user information from database
        user = User.query.filter_by(id=session['user_id']).first()
        
        if not user:
            flash('User not found')
            return redirect(url_for('login'))
        
        return render_template('settings.html', user=user)
    except Exception as e:
        print(f"Error in settings route: {e}")
        flash('An error occurred while loading settings')
        return redirect(url_for('user_dashboard'))
    
if __name__ == '__main__':
    app.run(debug = True)