import json

json1 = json.load(open('questions_entro.json'))
json2 = json.load(open('questions_entro_old.json'))

nums1 = [q['num'] for q in json1]
nums2 = [q['num'] for q in json2]

def find_question(question_number):
    for question in json2:
        if question['num'] == question_number:
            return question

for n in nums2:
    if n not in nums1:
        json1.append(find_question(n))
        print('Added question', n)

with open('questions_entro.json', 'w') as f:
    json.dump(json1, f, indent=4)
