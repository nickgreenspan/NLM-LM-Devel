import json
import random
from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

#add beautiful soup to parse html

original_GNQ = open('v1.0-simplified_simplified-nq-train.jsonl')
# modified_GNQ = open('googlenq_SQUAD_format')
#infile = json.load(original_GNQ)		
entry_list = []
for line in original_GNQ:
	# print(line) #testing purposes
	infile = json.loads(line)
	# print(infile)
	is_impossible = False
	title = infile["example_id"]
	html = strip_tags(infile["document_text"]) #called document_html in the long version, and might need to strip out html? Ask sonia
	question = infile["question_text"]
	question_id = random.randint(100000000,999999999)
	answer_start = 1 #character count from the begining of the context string, find a way to calculate it
	if infile["annotations"][0]["yes_no_answer"] != "NONE":
		answer = infile["annotations"][0]["yes_no_answer"]
	elif infile["annotations"][0]["short_answers"] != []:
		answer = infile["annotations"][0]["short_answers"][0]
	elif infile["annotations"][0]["long_answer"] != []:
		answer = infile["annotations"][0]["long_answer"]
	else: 
		answer = [] #probably won't be activated
		is_impossible = True
	entry_list.append({"title" : title, "paragraphs" : [{"qas": [{"question": question, "id": question_id, "answers": [{"text": answer, "answer_start": answer_start}], "is_impossible": is_impossible}], "context": html}]})
final_string = {"version": "v2.0", "data": entry_list}
with open('modified_GNQ.json', 'w') as outfile:
    json.dump(final_string, outfile)