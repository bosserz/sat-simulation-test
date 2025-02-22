from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.secret_key = 'intsightedu'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
app.config['SESSION_FILE_DIR'] = "./flask_session/"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sat_simulation_test_user:b0vlxEmUfEgoQ0jtrFdCtmTaZU5rE8Kl@dpg-cn822qq1hbls73d8aq10-a.singapore-postgres.render.com/sat_simulation_test'
db = SQLAlchemy(app)
# Session(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class UserLogin(db.Model):
    __tablename__ = 'user_login'
    # id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(50), unique=True, nullable=False)
    # password = db.Column(db.String(255), nullable=False)
    # is_active = db.Column(db.Boolean, default=True)
    # is_authenticated = db.Column(db.Boolean, default=True)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(255), nullable=False)
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

class CorrectAnswer(db.Model):
    __tablename__ = 'correct_answers'
    question_id = db.Column(db.Integer, primary_key=True)
    correct_answer = db.Column(db.String(1000), nullable=True)

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
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    user = UserLogin.query.get(int(user_id))
    if user and user.is_active:
        return user
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.clear()
        username = request.form['username']
        password = request.form['password']

        # user = UserLogin.query.filter_by(username=username, password=password).first()
        # Find user by email
        user = UserLogin.query.filter_by(username=username).first()

        # if not user:
            # warning_message = "Please contact admin for supports."
            # flash('Please contact admin to support.')
            # return render_template('login.html', warning=warning_message)

        # Validate user and check hashed password
        if not user or not check_password_hash(user.password_hash, password):
            warning_message = "Invalid email or password. Please try again or contact admin for support."
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
    session.clear()
    # session.pop("user", None)
    return render_template('submission-success.html')

# @app.route('/new-exam/<module>', methods=['GET', 'POST'])
# @login_required
# def new_exam(module):
#     if current_user is None:
#         return redirect(url_for('login'))
    
#     # Save the start time and exam duration in the session if not already set
#     session_key = f"{module}_start_time"
#     duration_key = f"{module}_time_duration"
#     if not session.get(session_key):
#         session[session_key] = datetime.utcnow().isoformat()
#         session[duration_key] = get_time_duration(module)

#     # Compute the remaining time based on the stored start time
#     start_time = datetime.fromisoformat(session[session_key])
#     total_duration = session[duration_key]
#     elapsed = (datetime.utcnow() - start_time).total_seconds()
#     remaining_time = max(0, total_duration - elapsed)
    
#     questions = Question.query.order_by((Question.question_id)).filter_by(module=module).all()
#     questions_list = [{"question_id": q.question_id
#                         , "question_no": q.question_no
#                         , "question_header": q.question_header
#                         , "question_query": q.question_query
#                         , "question_img": q.question_img
#                         , "question_img_2": q.question_img_2
#                         , "answer_a": q.answer_a
#                         , "answer_b": q.answer_b
#                         , "answer_c": q.answer_c
#                         , "answer_d": q.answer_d
#                         , "section": q.section
#                         , "module": q.module
#                         , "type": q.question_type
#                         , "category": q.category
#                         } for q in questions]

#     return render_template('new-exam.html', questions=questions_list, time_duration=remaining_time, module=module,
#     username=current_user)

@app.route('/verbal/<module>', methods=['GET', 'POST'])
@login_required
def verbal(module):
    if current_user is None:
        return redirect(url_for('login'))
    
    # Save the start time and exam duration in the session if not already set
    session_key = f"{module}_start_time"
    duration_key = f"{module}_time_duration"
    if not session.get(session_key):
        session[session_key] = datetime.utcnow().isoformat()
        session[duration_key] = get_time_duration(module)

    # Compute the remaining time based on the stored start time
    start_time = datetime.fromisoformat(session[session_key])
    total_duration = session[duration_key]
    elapsed = (datetime.utcnow() - start_time).total_seconds()
    remaining_time = max(0, total_duration - elapsed)
    
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
                        , "category": q.category
                        } for q in questions]
    # module = 'verbal-1'

    return render_template('verbal.html', questions=questions_list, time_duration=remaining_time, module=module,
    username=current_user)

@app.route('/math/<module>', methods=['GET', 'POST'])
@login_required
def math(module):
    if current_user is None:
        return redirect(url_for('login'))
    
    # Save the start time and exam duration in the session if not already set
    session_key = f"{module}_start_time"
    duration_key = f"{module}_time_duration"
    if not session.get(session_key):
        session[session_key] = datetime.utcnow().isoformat()
        session[duration_key] = get_time_duration(module)

    # Compute the remaining time based on the stored start time
    start_time = datetime.fromisoformat(session[session_key])
    total_duration = session[duration_key]
    elapsed = (datetime.utcnow() - start_time).total_seconds()
    remaining_time = max(0, total_duration - elapsed)
    
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
                        , "category": q.category
                        } for q in questions]
    # module = 'verbal-1'

    return render_template('math.html', questions=questions_list, time_duration=remaining_time, module=module,
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
    
@app.route('/reference')
def reference():
    return render_template('reference.html')


def get_time_duration(module):

    if 'math' in module:

        return 35 * 60
    
    else:

        return 32 * 60

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate passwords
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Check if email already exists
        existing_user = UserLogin.query.filter_by(username=username).first()
        if existing_user:
            flash("Email is already registered!", "warning")
            return redirect(url_for('register'))

        # Insert user into database
        new_user = UserLogin(username=username, password_hash=hashed_password, name=name)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!", "success")
        return redirect(url_for('register'))  # Assuming you have a login page

    return render_template('register.html')

@app.route('/users', methods=['GET'])
def get_users():
    
    users = UserLogin.query.with_entities(UserLogin.username, UserLogin.name).all()
    
    return render_template('users.html', users=users)

def process_responses(responses):
    for question_id, answer in responses.items():
        # Process each response, e.g., save to a database
        # For demonstration, print the response to the console
        print(f"Question {question_id} - Answer: {answer}")

@app.route('/results')
@login_required
def results():
    username = current_user.username

    # Fetch student's answers
    student_answers = db.session.query(Answer.question_id, Answer.answer).filter_by(username=username).all()

    # Fetch correct answers
    correct_answers = db.session.query(CorrectAnswer.question_id, CorrectAnswer.correct_answer).all() 

    # Fetch question_type
    question_type = db.session.query(Question.question_id, Question.question_type).all()

    # Convert to dictionaries for easy lookup
    correct_dict = {q_id: ans for q_id, ans in correct_answers}
    question_type_dict = {q_id: q_type for q_id, q_type in question_type}

    def check_answer(answer, correct_answer, question_type):
        if question_type == 'blank':
            return float(answer) == float(correct_answer)
        else:
            return answer == correct_answer

    # Count correct answers per section
    section1_correct = sum(1 for q_id, ans in student_answers if q_id in correct_dict and check_answer(ans, correct_dict[q_id], question_type_dict[q_id]) and q_id <= 54)
    section2_correct = sum(1 for q_id, ans in student_answers if q_id in correct_dict and check_answer(ans, correct_dict[q_id], question_type_dict[q_id]) and 55 <= q_id <= 98)

    # Score interpolation ranges
    section1_ranges = [(20, 200), (30, 400), (40, 500), (50, 600), (54, 700)]
    section2_ranges = [(16, 200), (24, 400), (32, 500), (40, 600), (44, 700)]

    # Function for linear interpolation
    def interpolate_score(correct, ranges):
            for i in range(len(ranges) - 1):
                if ranges[i][0] <= correct <= ranges[i + 1][0]:
                    x1, y1 = ranges[i]
                    x2, y2 = ranges[i + 1]
                    # Linear interpolation formula: y = y1 + ((y2 - y1) / (x2 - x1)) * (x - x1)
                    return round(y1 + ((y2 - y1) / (x2 - x1)) * (correct - x1))
            return 200 if correct < ranges[0][0] else 800  # Min and max limits

    # Calculate section scores
    section1_score = round(interpolate_score(section1_correct, section1_ranges))
    section2_score = round(interpolate_score(section2_correct, section2_ranges))

    # Compute total score
    total_score = section1_score + section2_score

    return render_template("results.html", username=username,
                           section1_correct=section1_correct, section1_score=section1_score,
                           section2_correct=section2_correct, section2_score=section2_score,
                           total_score=total_score)

@app.route('/all-results')
def all_results():
    # Fetch all unique usernames who have taken the test
    users = db.session.query(Answer.username).filter(Answer.answer_id >= 1324).distinct().all()
    user_scores = []

    for user in users:
        username = user.username

        # Fetch student's answers
        student_answers = db.session.query(Answer.question_id, Answer.answer).filter_by(username=username).all()

        # Fetch correct answers
        correct_answers = db.session.query(CorrectAnswer.question_id, CorrectAnswer.correct_answer).all()  # Assuming answer_a is correct

        # Fetch question_type
        question_type = db.session.query(Question.question_id, Question.question_type).all()

        # Convert to dictionaries for easy lookup
        correct_dict = {q_id: ans for q_id, ans in correct_answers}
        question_type_dict = {q_id: q_type for q_id, q_type in question_type}

        def check_answer(answer, correct_answer, question_type):
            if answer is None or answer.strip() == "":
                return False
            if question_type == 'blank':
                try:
                    return eval(answer) == eval(correct_answer)
                except (ValueError, SyntaxError, NameError):
                    return False
            return answer == correct_answer

        # Count correct answers per section
        section1_correct = sum(1 for q_id, ans in student_answers if q_id in correct_dict and check_answer(ans, correct_dict[q_id], question_type_dict[q_id]) and q_id <= 54)
        section2_correct = sum(1 for q_id, ans in student_answers if q_id in correct_dict and check_answer(ans, correct_dict[q_id], question_type_dict[q_id]) and 55 <= q_id <= 98)
        # Score interpolation ranges
        section1_ranges = [(0, 200), (20, 400), (30, 500), (40, 600), (50, 700), (54, 800)]
        section2_ranges = [(0, 200), (16, 400), (24, 500), (32, 600), (40, 700), (44, 800)]

        # Function for linear interpolation
        def interpolate_score(correct, ranges):
            for i in range(len(ranges) - 1):
                if ranges[i][0] <= correct <= ranges[i + 1][0]:
                    x1, y1 = ranges[i]
                    x2, y2 = ranges[i + 1]
                    # Linear interpolation formula: y = y1 + ((y2 - y1) / (x2 - x1)) * (x - x1)
                    return round(y1 + ((y2 - y1) / (x2 - x1)) * (correct - x1), -1)
            return 200 if correct < ranges[0][0] else 800  # Min and max limits

        # Calculate section scores
        section1_score = round(interpolate_score(section1_correct, section1_ranges))
        section2_score = round(interpolate_score(section2_correct, section2_ranges))

        # Compute total score
        total_score = section1_score + section2_score

        # Append data for each user
        user_scores.append({
            "username": username,
            "section1_correct": section1_correct,
            "section1_score": section1_score,
            "section2_correct": section2_correct,
            "section2_score": section2_score,
            "total_score": total_score
        })

    # Sort users by total score (highest first)
    user_scores.sort(key=lambda x: x["total_score"], reverse=True)

    return render_template("all-results.html", user_scores=user_scores)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    # sess.init_app(app)
    app.run(debug=False)
