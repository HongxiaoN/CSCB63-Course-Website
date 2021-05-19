import sqlite3
from flask import Flask, render_template, request, redirect, session, g

# the resource that we use: https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/

DATABASE = './assignment3.db'

app = Flask(__name__)
app.secret_key = "cscb20"

def get_db():
    database = getattr(g, '_database', None)
    if database is None:
        database = g._database = sqlite3.connect(DATABASE)
    return database

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def insert_db(query, args=()):
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    db.commit()
    cur.close()
    db.close()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/login')
def login():

    if len(request.args) == 0: 
        return render_template('login.html')

    username = request.args['username']
    password = request.args['password']


    database = get_db()
    database.row_factory = make_dicts
    user = query_db('SELECT * FROM User WHERE username=? AND password=?',
                    [username, password], one=True)
    database.close()

    if user:
        session['username'] = user['username']
        
        if user['instructor'] == "YES":
            session['instructor'] = "YES"
        else:
            session['instructor'] = "NO"
        return redirect('/')
    else:
        return render_template('login.html', error=True)

@app.route('/signup')
def signup():
    if len(request.args) == 0: 
        return render_template('signup.html')

    username = request.args['username']
    password = request.args['password']
    instructor = request.args['instructor']

    database = get_db()
    database.row_factory = make_dicts
    user = query_db('SELECT * FROM User WHERE username=?',
                    [username], one=True)
    
    if user:
        database.close()
        return render_template('signup.html', error=True)

    if instructor == "YES" or instructor == "NO":

        insert_db('INSERT INTO User VALUES(?, ?, ?)', (username, password, instructor))
        return redirect('/login')

    else:
        database.close()
        return render_template('signup.html', error=True)

@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session['username'], instructor=session['instructor'])
    else:
        return redirect('/login')

@app.route('/index')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'], instructor=session['instructor'])
    else:
        return redirect('/login')

@app.route('/assignments')
def assignments():
    if 'username' in session:
        return render_template('assignments.html', username=session['username'], instructor=session['instructor'])
    else:
        return redirect('/login')

@app.route('/calendar')
def calendar():
    if 'username' in session:
        return render_template('calendar.html', username=session['username'], instructor=session['instructor'])
    else:
        return redirect('/login')

@app.route('/course_team')
def course_team():
    if 'username' in session:
        return render_template('course_team.html', username=session['username'], instructor=session['instructor'])
    else:
        return redirect('/login')

@app.route('/labs')
def labs():
    if 'username' in session:
        return render_template('labs.html', username=session['username'], instructor=session['instructor'])
    else:
        return redirect('/login')

@app.route('/lectures')
def lectures():
    if 'username' in session:
        return render_template('lectures.html', username=session['username'], instructor=session['instructor'])
    else:
        return redirect('/login')

@app.route('/successful_submit')
def successful_submit():
    if 'username' in session:
        return render_template('successful_submit.html', username=session['username'], instructor=session['instructor'])
    else:
        return redirect('/login')

@app.route('/tests')
def tests():
    if 'username' in session:
        return render_template('tests.html', username=session['username'], instructor=session['instructor'])
    else:
        return redirect('/login')

@app.route('/tutorials')
def tutorials():
    if 'username' in session:
        return render_template('tutorials.html', username=session['username'], instructor=session['instructor'])
    else:
        return redirect('/login')

@app.route('/marks')
def marks():
    if 'username' not in session:
        return redirect('/login')

    database = get_db()
    database.row_factory = make_dicts

    if session['instructor'] == "NO":
        marks = query_db('SELECT * FROM Mark WHERE username=?', [session['username']])
    else:
        marks = query_db('SELECT * FROM Mark')

    database.close()

    return render_template('marks.html', username=session['username'], marks=marks, instructor=session['instructor'])

@app.route('/request_remark')
def request_remark():

    if 'username' not in session:
        return redirect('/login')

    if not request.args:
        return redirect('/marks')

    id_mark= request.args['id_mark']
    reason = request.args['reason']
    
    if reason == "":
        return render_template('successful_submit.html', error=True)

    try:
        insert_db('INSERT INTO Remark VALUES(?, ?)', (id_mark, reason))
    except:
        return redirect('/marks')

    return redirect('/successful_submit')

@app.route('/view_remark')
def view_remark():

    if 'username' not in session:
        return redirect('/login')
    
    if session['instructor'] == "NO":
        return redirect('/')
    
    database = get_db()
    database.row_factory = make_dicts
    remarks = query_db(
        'SELECT * FROM Remark, Mark WHERE Remark.id_mark = Mark.id_mark')
    database.close()
    return render_template('view_remark.html', remarks=remarks, username=session['username'])

@app.route('/new_mark')
def new_mark():

    if 'username' not in session:
        return redirect('/login')
    
    if session['instructor'] == "NO":
        return redirect('/')
    
    if not request.args:
        
        database = get_db()
        database.row_factory = make_dicts
        students = query_db('SELECT DISTINCT username FROM User WHERE instructor ="NO"')
        database.close()

        return render_template('new_mark.html', students=students, username=session['username'])

    else:
        name = request.args['name']
        grade = float(request.args['grade'])
        username = request.args['username']

        insert_db('INSERT INTO Mark (name, grade, username) VALUES (?, ?, ?)', (name, grade, username))
        return redirect('/marks')

@app.route('/give_feedback')
def give_feedback():

    if 'username' not in session:
        return redirect('/login')
    
    if session['instructor'] == "YES":
        return redirect('/')

    if not request.args:
    
        database = get_db()
        database.row_factory = make_dicts
        instructors = query_db('SELECT username FROM User WHERE instructor = "YES"')
        database.close()
        return render_template('give_feedback.html', instructors = instructors, username=session['username'])
    
    else:

        instructor = request.args['username']
        questionA = request.args['questionA']        
        questionB = request.args['questionB']
        questionC = request.args['questionC']
        questionD = request.args['questionD']

        insert_db('INSERT INTO Feedback VALUES (?, ?, ?, ?, ?)', (instructor, questionA, questionB, questionC, questionD))

        return redirect('/successful_submit')

@app.route('/view_feedbacks')
def view_feedbacks():

    if 'username' not in session:
        return redirect('/login')
    
    if session['instructor'] == "NO":
        return redirect('/')
    
    database = get_db()
    database.row_factory = make_dicts
    feedbacks = query_db('SELECT * FROM Feedback WHERE instructor=?', [session['username']])
    database.close()

    return render_template('view_feedbacks.html', feedbacks=feedbacks, username=session['username'])


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)