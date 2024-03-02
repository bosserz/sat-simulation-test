from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime



app = Flask(__name__)
app.secret_key = 'intsightedu'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sat_simulation_test_user:b0vlxEmUfEgoQ0jtrFdCtmTaZU5rE8Kl@dpg-cn822qq1hbls73d8aq10-a.singapore-postgres.render.com/sat_simulation_test'
db = SQLAlchemy(app)
# Session(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class UserLogin(db.Model):
    __tablename__ = 'user_login'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_authenticated = db.Column(db.Boolean, default=True)

    def get_id(self):
        return str(self.id)

class Question(db.Model):
    __tablename__ = 'sat_questions'
    question_id = db.Column(db.Integer, primary_key=True)
    question_no = db.Column(db.Integer, nullable=False)
    section = db.Column(db.Integer, nullable=False)
    module = db.Column(db.Integer, nullable=False)
    question_group = db.Column(db.String(10), nullable=False)
    question_type = db.Column(db.String(10), nullable=False)
    question_level = db.Column(db.Integer, nullable=False)
    question_header = db.Column(db.String(10000), nullable=True)
    question_query = db.Column(db.String(10000), nullable=False)
    question_img = db.Column(db.String(1000), nullable=True)
    question_img_2 = db.Column(db.String(1000), nullable=True)
    answer_a = db.Column(db.String(1000), nullable=True)
    answer_b = db.Column(db.String(1000), nullable=True)
    answer_c = db.Column(db.String(1000), nullable=True)
    answer_d = db.Column(db.String(1000), nullable=True)
    category = db.Column(db.String(100), nullable=False)

class Answer(db.Model):
    __tablename__ = 'sat_answers'
    answer_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Answer(answer_id={self.answer_id}, username='{self.username}', question_id={self.question_id}, answer='{self.answer}', timestamp='{self.timestamp}')>"

# Dummy user data (replace with a database in a real application)
users = {'admin@gmail.com': '1234'}

@app.route('/')
def home():
    return 'Welcome to the home page'

@login_manager.user_loader
def load_user(user_id):
    user = UserLogin.query.get(int(user_id))
    if user and user.is_active:
        return user
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # test_key = request.form['test_key']
        user = UserLogin.query.filter_by(username=username, password=password).first()

        if not user:
            warning_message = "Please contact admin for supports."
            # flash('Please contact admin to support.')
            return render_template('login.html', warning=warning_message)

        if (user.is_authenticated) :
            login_user(user)
            session["user"] = username
            session['logged_in'] = True
            session["key"] = 'intsight_edu'
            # return redirect(url_for('test_info'))
            return render_template('test-info.html', username=current_user)
        else:
            flash('Please contact admin to support.')
    return render_template('login.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         if users.get(email) == password:
#             return redirect(url_for('home'))
#         else:
#             return 'Invalid username or password'
#     return render_template('login.html')

@app.route('/test-info')
@login_required
def test_info():
    return render_template('test-info.html', username=current_user)


@app.route('/update-timer', methods=['POST'])
def update_timer():
    data = int(request.form.get('remaining_time'))
    # remaining_seconds = data.get('remaining_time')
    # print(f"Remaining time received: {minutes} minutes, {seconds} seconds")
    # Process the remaining time further if needed
    return remaining_seconds

# Initialize responses as an empty dictionary
responses = {}

@app.route('/submit-success', methods=['POST'])
@login_required
def submit():
    current_user.is_authenticated = False
    db.session.commit()
    # session.pop("user", None)
    return render_template('submission-success.html')

@app.route('/new-exam/<module>', methods=['GET', 'POST'])
@login_required
def new_exam(module):
    if current_user is None:
        return redirect(url_for('login'))
    else:
        questions = Question.query.order_by((Question.question_id)).filter_by(module=module).all()
        questions_list = [{"question_id": q.question_id
                            , "question_no": q.question_no
                            , "question_header": q.question_header
                            , "question_query": q.question_query
                            , "question_img": q.question_img
                            , "question_img_2": q.question_img_2
                            , "answer_a": q.answer_a
                            , "answer_b": q.answer_b
                            , "answer_c": q.answer_c
                            , "answer_d": q.answer_d
                            , "section": q.section
                            , "module": q.module
                            , "type": q.question_type
                            } for q in questions]
        # module = 'verbal-1'
        time_duration = get_time_duration(module)
        return render_template('new-exam.html', questions=questions_list, time_duration=time_duration, module=module,
        username=current_user)

@app.route('/save-answers', methods=['POST'])
@login_required
def save_answers():
    user_answers = request.json
    username = current_user.username
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    answers_to_save = []
    for question_id, answer in user_answers.items():
        answers_to_save.append({'username': username, 'question_id': question_id, 'answer': answer, 'timestamp': timestamp})
        answer = Answer(username=username, 
                        question_id=question_id, 
                        answer=answer, 
                        timestamp=timestamp,
                        )
        db.session.add(answer)
    print(answers_to_save)
    db.session.commit()

    

    # Save the answers to the database
    # database_module.save_answers(answers_to_save)

    # Save the userAnswers to the database
    # Example: database.save(user_answers)
    return jsonify({'message': 'Answers saved successfully'}), 200


@app.route('/submit-module/<module>')
def submit_module(module):
    if module == 'verbal-1':
        return render_template('verbal1-module-submission.html')
    elif module == 'verbal-2':
        return render_template('verbal2-module-submission.html')
    elif module == 'math-1':
        return render_template('math1-module-submission.html')
    else:
        return render_template('math2-module-submission.html')


def get_time_duration(module):

    if 'math' in module:

        return 35 * 60
    
    else:

        return 32 * 60

def process_responses(responses):
    for question_id, answer in responses.items():
        # Process each response, e.g., save to a database
        # For demonstration, print the response to the console
        print(f"Question {question_id} - Answer: {answer}")


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    # sess.init_app(app)
    app.run(debug=True)