from flask import Flask, render_template, request, redirect, url_for, session
import json
import random

app = Flask(__name__)
app.secret_key = 'some_secret_key'  # Secret key for session

# Function to load questions from JSON and shuffle answers
def load_questions(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    questions = data['questions']
    
    # Shuffle the options for each question
    for question in questions:
        random.shuffle(question['options'])
    
    return questions

# Route for choosing question type
@app.route('/')
def choose_type():
    return render_template('choose_type.html')

# Save chosen question type and redirect to quiz
@app.route('/set_type', methods=['POST'])
def set_type():
    question_type = request.form.get('question_type')
    if question_type == 'adfo':
        session['question_file'] = 'ADFOquestions.json'
    elif question_type == 'ocifo':
        session['question_file'] = 'OCIFOquestions.json'
    return redirect(url_for('index'))

# Display quiz questions based on chosen type
@app.route('/quiz')
def index():
    question_file = session.get('question_file')
    if not question_file:
        return redirect(url_for('choose_type'))

    questions = load_questions(question_file)
    return render_template('index.html', questions=questions)

# Evaluate answers and display results
@app.route('/submit', methods=['POST'])
def submit():
    question_file = session.get('question_file')
    questions = load_questions(question_file)
    user_answers = request.form

    correct_count = 0
    results = []
    for question in questions:
        qid = str(question['id'])
        correct = False
        if question['type'] == 'single':
            user_answer = user_answers.get(qid)
            if user_answer and user_answer == question['correct_answer']:
                correct = True
        elif question['type'] == 'multiple':
            selected_answers = user_answers.getlist(qid)
            if selected_answers and set(selected_answers) == set(question['correct_answers']):
                correct = True

        results.append({
            'question': question['question'],
            'correct': correct,
            'user_answer': user_answers.getlist(qid),
            'correct_answer': question.get('correct_answers') if question['type'] == 'multiple' else question['correct_answer']
        })

        if correct:
            correct_count += 1

    score_percentage = round((correct_count / len(questions)) * 100)
    return render_template('result.html', results=results, score=score_percentage)

if __name__ == '__main__':
    app.run(debug=True)
