from flask import Flask, render_template, request, redirect, url_for, session
import json
import random

app = Flask(__name__)
app.secret_key = 'some_secret_key'  # Potřebné pro session


# Načítání otázek ze souborů JSON
def load_questions(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['questions']


# Úvodní stránka pro výběr typu otázek
@app.route('/')
def choose_type():
    return render_template('choose_type.html')


# Uloží vybraný typ otázek a přejde na první otázku
@app.route('/set_type', methods=['POST'])
def set_type():
    question_type = request.form.get('question_type')
    if question_type == 'adfo':
        session['question_file'] = 'ADFOquestions.json'
    elif question_type == 'ocifo':
        session['question_file'] = 'OCIFOquestions.json'
    return redirect(url_for('index'))


# Zobrazí náhodnou otázku
@app.route('/quiz')
def index():
    question_file = session.get('question_file')
    if not question_file:
        return redirect(url_for('choose_type'))  # Pokud není typ vybrán, vrátí se na výběr

    questions = load_questions(question_file)
    question = random.choice(questions)
    session['current_question'] = question
    return render_template('question.html', question=question)


# Vyhodnocení odpovědi
@app.route('/submit', methods=['POST'])
def submit():
    question = session.get('current_question')
    user_answer = request.form.getlist('answer')

    if question:
        correct_answer = question['correct_answers'] if question['type'] == 'multiple' else [question['correct_answer']]
        is_correct = set(user_answer) == set(correct_answer)

        result = {
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        }

        return render_template('singleresult.html', result=result)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
