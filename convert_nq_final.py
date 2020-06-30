import json
import random
import gzip
from io import StringIO

entry_list = []
ans_list = []
j = 0
no_short = 0
outfile = open('modified_GNQ_test.json', 'w')
with gzip.open('v1.0_train_nq-train-00.jsonl.gz', 'rb') as f:
    for line in f:
        #if j == 10:
           #break
        infile = json.loads(line)
        if infile["annotations"][0]["short_answers"] == []: #if there is no short answer, ignore this data point
            no_short += 1
            continue
        is_impossible = False
        title = infile["example_id"]
        text = infile["document_html"]
        question = infile["question_text"]
        question_id = random.randint(100000000,999999999)
       
        tok_ans = ""
        ans_idx = 0
        text_no_html = ""
        prev_token = ''
        for i in range(len(infile["document_tokens"])):
            token = infile["document_tokens"][i]
            before_ans = False
            in_ans = False
            overlap = False
        
            if i < infile["annotations"][0]["short_answers"][0]["start_token"]:
                before_ans = True
            elif infile["annotations"][0]["short_answers"][0]["start_token"] <= i < infile["annotations"][0]["short_answers"][0]["end_token"]:
                in_ans = True
            if i == infile["annotations"][0]["short_answers"][0]["start_token"]:
                overlap = True

            if not token["html_token"]:
                if prev_token != '' and prev_token != '(' and prev_token != '``' and prev_token != "'" and prev_token != '-' and prev_token != '--'  and (token["token"] == '(' or token["token"] == '``' or token["token"] == "'" or (token["token"].replace('.', '').isalnum())):
                    text_no_html += (' ' + token["token"])
                    if overlap:
                        ans_idx += 1
                    if before_ans:
                        ans_idx += len(token["token"]) + 1
                    elif in_ans:
                         tok_ans += (' ' + token["token"])
                else:
                    text_no_html += (token["token"])
                    if before_ans:
                        ans_idx += len(token["token"])
                    elif in_ans:
                        tok_ans += token["token"]
            prev_token = token["token"]
            # elif in_ans: #accounts for the possibility that there could be html tokens within the answer token indexes, doesnt seem to be necissary
            #     if prev_token != '``' and prev_token != "'" and prev_token != '-' and prev_token != '--' and (prev_token != ':') and (token["token"] == '(' or token["token"] == '``' or token["token"] == "'" or (token["token"].replace('.', '').isalnum() and (prev_token == '' or prev_token != '('))):
            #         tok_ans += (' ' + token["token"])
            #     else:
            #         tok_ans += token["token"]
        #print(text_no_html)
        #print(text_no_html[ans_idx:ans_idx+10])
        entry_list.append({"title" : title, "paragraphs" : [{"qas": [{"question": question, "id": question_id, "answers": [{"text": tok_ans, "answer_start": ans_idx}], "is_impossible": is_impossible}], "context": text_no_html}]})
        #ans_list.append((question, tok_ans))
        print(j)
        j += 1
final_string = {"version": "v2.0", "data": entry_list}
#with open('modified_GNQ_test.json', 'w') as outfile:
print(j)
print(no_short)
json.dump(final_string, outfile)
#print(entry_list)
#print(ans_list)