from flask import Flask, flash, redirect, request, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt, check_password_hash
import logging
from logging.handlers import RotatingFileHandler
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///members.db'
app.config['SQLALCHEMY_DATABASE_URI2'] = 'sqlite:///bookdetails.db'
app.config['SQLALCHEMY_DATABASE_URI3'] = 'sqlite:///adminmembers.db'
app.config['SQLALCHEMY_DATABASE_URI4'] = 'sqlite:///quizleaderboard.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.secret_key = '35fc5897d63448a32f9e8c2130fa08b7467c221774ded58171468b42238ee74c'



class Members(db.Model):

    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return 'Username' + 'Password' +  str(self.id)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class BookDetails(db.Model):
    __tablename__ = 'book_details'

    id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.Text, nullable=False)
    book_description = db.Column(db.Text, nullable=False)
    book_cover = db.Column(db.Text, nullable=False)
    book_quote_one = db.Column(db.Text, nullable=False)
    book_quote_two = db.Column(db.Text, nullable=False)
    book_quote_three = db.Column(db.Text, nullable=False)
    book_quote_four = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'Book Title: {self.book_title}, Book Description: {self.book_description}, Book Cover: {self.book_cover}, Book Quote One: {self.book_quote_one}, Book Quote Two: {self.book_quote_two}, Book Quote Three: {self.book_quote_three}, Book Quote Four: {self.book_quote_four}, ID: {self.id}'



class AdminMembers(db.Model):
    __tablename__ = 'admin_members'

    id = db.Column(db.Integer, primary_key=True)
    admin_username = db.Column(db.Text, nullable=False)
    admin_password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'Admin Username: {self.admin_username}, Admin Password Hash: {self.admin_password_hash}, ID: {self.id}'
    
    def check_admin_password(self, admin_password):
        return check_password_hash(self.admin_password_hash, admin_password)

class QuizLeaderboard(db.Model):
    __tablename__ = 'quiz_leaderboard'

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Score: {self.score}, ID: {self.id}'

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bookgallery/', methods = ['GET'])
def book_gallery():
    book_gallery = BookDetails.query.all()

    for book in book_gallery:
        file_name = f"{book.book_cover}"
        file_path_route = '/static/img/' + file_name

        print(file_path_route)

        book.file_path_route = file_path_route

    file_path_route = '/static/img/' + book_gallery[-1].book_cover

    return render_template('book_gallery.html', book_gallery = book_gallery, file_path_route=file_path_route)

@app.route('/bookgallery/<int:id>', methods = ['GET'])
def book(id):
    book_gallery_obj = BookDetails.query.get(id)

    if book_gallery_obj:
        file_name = f"{book_gallery_obj.book_cover}"
        file_path_route = '/static/img/' + file_name

        print(file_path_route)

        return render_template('percy_jackson_book.html', book_gallery_obj = book_gallery_obj, file_path_route = file_path_route)
    else:
        return redirect(url_for('book_gallery'))

questions = [
        {

            'question_id': 1,
            'question': 'What is the full name of the girl who picks on Grover and Percy in school?',
            'options': ['Sarah Betty', 'Annabeth Chase', 'Nancy Bobofit', 'Clarisse La Rue'],
            'correct_answer': 'Nancy Bobofit'

        },
        {
            'question_id': 2,
            'question': 'What is the fake undercover name for the Fury that attacked Percy in the museum?',
            'options': ['Fury 101', 'Mrs. Kerr', 'Mrs. Dodds', 'Alecto'],
            'correct_answer': 'Mrs. Dodds'

            },
        {
            'question_id': 3,
            'question': 'What can Riptide be turned into?',
            'options': ['Nothing (It stays as a sword)' , 'A football', 'A ballpoint pen', 'A hat'],
            'correct_answer': 'A ballpoint pen'
            },
            {
            'question_id': 4,
            'question': 'Where do Percy Jackson and his mum go on holiday?',
            'options': ['Montauk', 'They did not go on holiday', 'Camp-half blood' , 'Miami'],
            'correct_answer': 'Montauk'
                },
            {
            'question_id': 5,
            'question': 'In what condition were Percys mum, Grover and Percy, respectively, when they entered Camp-hald blood?',
            'options': ['Dead(or so presumed), unconscious, exhausted', 'Unconscious, missing leg, dead', 'Dead, dead, dead', 'Exhausted, exhausted, unconscious'],
            'correct_answer': 'Dead(or so presumed), unconscious, exhausted'
                }            




        ]

user_score = 0

@app.route('/games/', methods = ['GET', 'POST'])
def games():
    global user_score

    if request.method == 'POST':

        user_score = 0

        for question in questions:
            selected_option = request.form.get(str(question['question_id']))
            if selected_option == question['correct_answer']:
                user_score += 1

        save_score_to_database(user_score)

    games = QuizLeaderboard.query.order_by(QuizLeaderboard.score.desc()).all()


    return render_template('games.html', questions = questions, score=user_score, games = games)


def save_score_to_database(score):
    user_score_entry = QuizLeaderboard(score=score)
    db.session.add(user_score_entry)
    db.session.commit()




@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        login = Members.query.filter_by(username=username).first()
        if login is not None and login.check_password(password):
            session['logged_in'] = 'user_status'
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout/')
def user_logout():
    if 'logged_in' in session:
        user_status = session['logged_in']
        session.pop('logged_in', None)
        return redirect(url_for('index'))
    return render_template('no_access.html')

@app.route('/adminlogin/', methods = ['GET' , 'POST' ])
def admin_login(admin_status = None):
    if request.method == 'POST':
        admin_username = request.form['adminUsername']
        admin_password = request.form['adminPassword']

        admin_login = AdminMembers.query.filter_by(admin_username=admin_username).first()
        if admin_login is not None and admin_login.check_admin_password(admin_password):
            session['admin_status'] = 'admin'
            return redirect (url_for('add_members'))
        else:
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/register/', methods = ['GET' , 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        register = Members(username = username, password_hash = password_hash)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/administration/members/', methods=['GET'])
def add_members(): 
    if 'admin_status' in session:
        admin_status = session['admin_status']
        add_members = Members.query.all()
        return render_template('members.html', add_members=add_members)
    return render_template('no_access.html')

@app.route('/administration/logout/')
def logout():
    if 'admin_status' in session:
        admin_status = session['admin_status']
        session.pop('admin_status', None)
        return redirect(url_for('index'))
    return render_template('no_access.html')

@app.route('/administration/members/delete/<int:id>')
def delete_members(id):
    if 'admin_status' in session:
        admin_status = session['admin_status']
        username_obj = Members.query.get(id)
        db.session.delete(username_obj)
        db.session.commit()
        return redirect('/administration/members/')
    return render_template('no_access.html')

@app.route('/administration/highscores/', methods = ['GET'])
def high_scores():
    if 'admin_status' in session:
        admin_status = session['admin_status']
        high_scores = QuizLeaderboard.query.all()
        return render_template('high_scores.html', high_scores = high_scores)
    return render_template('no_access.html')

@app.route('/administration/bookdetails/', methods = ['POST', 'GET'])
def add_book_details():
    if 'admin_status' in session:
        admin_status = session['admin_status']
        if request.method == 'POST':
            db.session.add(BookDetails(
                book_title=request.form['bookTitle'],
                book_description=request.form['bookDescription'],
                book_cover=request.form['bookCover'],
                book_quote_one=request.form['bookquoteOne'],
                book_quote_two=request.form['bookquoteTwo'],
                book_quote_three=request.form['bookquoteThree'],
                book_quote_four=request.form['bookquoteFour'],
            ))
            db.session.commit()
            return redirect('/administration/bookdetails/')

        add_book_details = BookDetails.query.all()
        return render_template('book_details.html', add_book_details=add_book_details)
    return render_template('no_access.html') 

@app.route('/administration/bookdetails/edit/<int:id>', methods = ['GET', 'POST'])
def edit_book_details(id):
    if 'admin_status' in session:
        admin_status = session['admin_status']
        book_title_obj = BookDetails.query.get(id)
        if request.method == 'POST':
            book_title_obj.book_title = request.form['bookTitle']
            book_title_obj.book_description = request.form['bookDescription']
            book_title_obj.book_cover = request.form['bookCover']
            book_title_obj.book_quote_one = request.form['bookquoteOne']
            book_title_obj.book_quote_two = request.form['bookquoteTwo']
            book_title_obj.book_quote_three = request.form['bookquoteThree']
            book_title_obj.book_quote_four = request.form['bookquoteFour']
            db.session.commit()
            return redirect('/administration/bookdetails/')
        else:
            return render_template('book_details_edit.html', book_title=book_title_obj, book_description=book_title_obj, book_cover=book_title_obj, book_quote_one=book_title_obj, book_quote_two=book_title_obj, book_quote_three=book_title_obj, book_quote_four=book_title_obj)

    return render_template('no_access.html')

@app.route('/administration/bookdetails/delete/<int:id>')
def delete_book_details(id):
    if 'admin_status' in session:
        admin_status = session['admin_status']
        book_title_obj = BookDetails.query.get(id)
        db.session.delete(book_title_obj)
        db.session.commit()
        return redirect('/administration/bookdetails/')
    return render_template('no_access.html')

@app.route('/administration/highscores/delete/<int:id>')
def delete_high_scores(id):
    if 'admin_status' in session:
        admin_status = session['admin_status']
        high_scores_obj = QuizLeaderboard.query.get(id)
        db.session.delete(high_scores_obj)
        db.session.commit()
        return redirect('/administration/highscores/')
    return render_template('no_access.html')

@app.route('/administration/adminmembers/', methods = ['POST' , 'GET'])
def admin_members():
    if 'admin_status' in session:
        admin_status = session['admin_status']
        if request.method == 'POST':
            admin_username = request.form['adminUsername']
            admin_password = request.form['adminPassword']
            
            hashed_admin_password = bcrypt.generate_password_hash(admin_password)

            db.session.add(AdminMembers(
                admin_username = admin_username,
                admin_password_hash = hashed_admin_password,
                ))
            db.session.commit()
            return redirect('/administration/adminmembers/')
        admin_members = AdminMembers.query.all()
        return render_template('admin_members.html', admin_members=admin_members)

    return render_template('no_access.html')

@app.route('/administration/adminmembers/delete/<int:id>')
def delete_admin_members(id):
    if 'admin_status' in session:
        admin_status = session['admin_status']
        admin_members_obj = AdminMembers.query.get(id)
        db.session.delete(admin_members_obj)
        db.session.commit()
        return redirect('/administration/adminmembers/')
    return render_template('no_access.html')

if __name__ == "__main__":
    app.run(ssl_context=context, host='0.0.0.0', debug=True)


