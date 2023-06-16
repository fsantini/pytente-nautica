import json
import os

def isnumeric(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def main():
    question_number = None
    question_text = None
    question_answer_1 = None
    question_answer_2 = None
    question_answer_3 = None
    question_answer_TF1 = None
    question_answer_TF2 = None
    question_answer_TF3 = None

    table_data = []

    def reset_question():
        nonlocal question_number, question_text, question_answer_1, question_answer_2, question_answer_3, question_answer_TF1, question_answer_TF2, question_answer_TF3
        question_number = None
        question_text = None
        question_answer_1 = None
        question_answer_2 = None
        question_answer_3 = None
        question_answer_TF1 = None
        question_answer_TF2 = None
        question_answer_TF3 = None

    with open('allegato-a-dd-106-del-120522.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if question_number is None and not isnumeric(line):
                continue
            if question_number is None:
                question_number = int(line)
                continue
            if question_text is None:
                question_text = line
                continue
            if question_answer_1 is None:
                question_answer_1 = line
                continue
            if question_answer_TF1 is None:
                if line == 'V' or line == 'F':
                    question_answer_TF1 = line
                else:
                    question_answer_1 += ' ' + line
                continue
            if question_answer_2 is None:
                question_answer_2 = line
                continue
            if question_answer_TF2 is None:
                if line == 'V' or line == 'F':
                    question_answer_TF2 = line
                else:
                    question_answer_2 += ' ' + line
                continue
            if question_answer_3 is None:
                question_answer_3 = line
                continue
            # we are at question_answer_TF3
            missing_last = False
            if isnumeric(line):
                # missing last answer
                missing_last = True
                if question_answer_TF2 == 'F' and question_answer_TF1 == 'F':
                    question_answer_TF3 = 'V'
                else:
                    question_answer_TF3 = 'F'
            else:
                if line == 'V' or line == 'F':
                    question_answer_TF3 = line
                else:
                    question_answer_3 += ' ' + line
                    continue
            right_answer = 0
            if question_answer_TF2 == 'V':
                right_answer = 1
            elif question_answer_TF3 == 'V':
                right_answer = 2
            row_data = {
                'num': question_number,
                'question': question_text,
                'answers': [
                    question_answer_1,
                    question_answer_2,
                    question_answer_3,
                ],
                'right_answer': right_answer,
                'image': None
            }
            table_data.append(row_data)
            reset_question()
            if missing_last:
                question_number = int(line)


    with open('questions_entro.json', 'w') as f:
        json.dump(table_data, f, indent=4)

if __name__ == '__main__':
    main()
