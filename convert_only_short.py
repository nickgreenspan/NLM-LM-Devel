import json
import random
import gzip
from io import StringIO
from bs4 import BeautifulSoup

entry_list = []
i = 0
with gzip.open('v1.0_train_nq-train-00.jsonl.gz', 'rb') as f:
    for line in f:
        # print(line) #testing purposes
        infile = json.loads(line)
        # print(infile)
        is_impossible = False
        title = infile["example_id"]
        text = infile["document_html"]
        # html_stripped = strip_tags(infile["document_html"]) #called document_text in the short version
        soup = BeautifulSoup(text, 'html.parser')
        html_stripped = soup.get_text()        
        question = infile["question_text"]
        question_id = random.randint(100000000,999999999)
        start_idxs = []
        answers = []
        if infile["annotations"][0]["short_answers"] != []:
            for short_answer in infile["annotations"][0]["short_answers"]:
                start_idx_i = short_answer["start_byte"]
                end_idx_i = short_answer["end_byte"]
                temp_ans = BeautifulSoup(text[start_idx_i:end_idx_i], 'html.parser')
                answer_i = temp_ans.get_text()
                start_idxs.append(start_idx_i)
                answers.append(answer_i)
        else: 
            continue

        start_idxs_no_html = []
        for idx in start_idxs:
            idx_no_html = idx
            for token in infile["document_tokens"]:
                if token["start_byte"] < idx and token["html_token"]:
                    diff = token["end_byte"] - token["start_byte"]
                    idx_no_html -= diff
                else:
                    break
            start_idxs_no_html.append(idx_no_html)

        if len(answers) > 1:
            entry_list.append({"title" : title, "paragraphs" : [{"qas": [{"question": question, "id": question_id, "answers": [{"text": answers, "answer_start": start_idxs_no_html}], "is_impossible": is_impossible}], "context": html_stripped}]})
            # print({"title" : title, "paragraphs" : [{"qas": [{"question": question, "id": question_id, "answers": [{"text": answers, "answer_start": start_idxs_no_html}], "is_impossible": is_impossible}], "context": html_stripped}]})
        else:
            entry_list.append({"title" : title, "paragraphs" : [{"qas": [{"question": question, "id": question_id, "answers": [{"text": answers[0], "answer_start": start_idxs_no_html[0]}], "is_impossible": is_impossible}], "context": html_stripped}]})
            #print({"title" : title, "paragraphs" : [{"qas": [{"question": question, "id": question_id, "answers": [{"text": answers[0], "answer_start": start_idxs_no_html[0]}], "is_impossible": is_impossible}], "context": html_stripped}]})
        print(i)
        i += 1
final_string = {"version": "v2.0", "data": entry_list}
with open('modified_GNQ_real.json', 'w') as outfile:
    json.dump(final_string, outfile)