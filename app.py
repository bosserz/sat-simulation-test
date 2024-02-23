from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sat_simulation_test_user:b0vlxEmUfEgoQ0jtrFdCtmTaZU5rE8Kl@dpg-cn822qq1hbls73d8aq10-a.singapore-postgres.render.com/sat_simulation_test'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

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
        user = UserLogin.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('exam'))
        else:
            flash('Invalid username or password')
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

@app.route('/exam', methods=['GET', 'POST'])
@login_required
def exam():
    questions = Question.query.order_by(Question.question_id).first()
    return render_template('exam.html', current_question=questions)

@app.route('/next', methods=['POST'])
def next_question():
    question_id = int(request.form['question_id'])
    questions = Question.query.get_or_404(question_id)
    # next_question = Question.query.filter(Question.question_id > question_id).first()
    if question_id == 40:
        return render_template('test-submit.html')
    else:
        return render_template('exam.html', current_question=questions)

    # if next_question:
    #     return render_template('exam.html', current_question=next_question)
    # else:
    #     return "End of test"  # Or redirect to a different page

# Initialize responses as an empty dictionary
responses = {}

@app.route('/submit-success', methods=['POST'])
@login_required
def submit():
    return render_template('submission-success.html')

@app.route('/test/<int:question_id>', methods=['GET', 'POST'])
@login_required
def test(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        # Handle the submitted answer
        answer = request.form['answer']
        responses[question_id] = answer
        # Redirect to the next question
        next_question_id = question_id + 1
        if next_question_id <= 10:  # Assuming 10 questions in total
            return redirect(url_for('test', question_id=next_question_id))
        else:
            # End of the test, process the responses
            process_responses(responses)
            return "End of the test. Responses collected."
    return render_template('test.html', question=question, answer=responses.get(question_id, ''))

def process_responses(responses):
    for question_id, answer in responses.items():
        # Process each response, e.g., save to a database
        # For demonstration, print the response to the console
        print(f"Question {question_id} - Answer: {answer}")

if __name__ == '__main__':
    app.run(debug=True)