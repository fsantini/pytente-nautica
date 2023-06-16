import json

def find_question(question_number):
    for question in questions:
        if question['num'] == question_number:
            return question

with open('questions_entro.json', 'r') as f:
    questions = json.load(f)

nums = [q['num'] for q in questions]
for i in range(1, 1473):
    if i not in nums:
        print(f'Question {i} not found')

print(len(questions))

with open('quiz_figure.txt', 'r') as f:
    for line in f:
        line = line[1:].strip()
        fig_number, questions_line = line.split('.')
        questions_line = questions_line.strip()
        question_numbers = questions_line.split('+')
        fig_number = int(fig_number.strip())
        question_numbers = [int(q) for q in question_numbers]
        print(fig_number, question_numbers)
        for q in question_numbers:
            find_question(q).update({'image': f'fig{fig_number:03d}.png'})

with open('questions_entro.json', 'w') as f:
    json.dump(questions, f, indent=4)