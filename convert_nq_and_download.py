import os.path
import json
# import random
import gzip
from io import StringIO
import requests

outfile = open('modified_GNQ_all.json', 'w')

entry_list = []
ans_list = []
j = 0
no_short = 0

for i in range(50):
    if i < 10: gzipname = 'v1.0_train_nq-train-'+'0'+str(i)+'.jsonl.gz'
    else: gzipname = 'v1.0_train_nq-train-'+str(i)+'.jsonl.gz'
    
    # download publically available files if not already downloaded
    if (not os.path.isfile(gzipname)):
        url = 'https://storage.googleapis.com/natural_questions/v1.0/train/nq-train-'+str(i)+'.jsonl.gz'
        r = requests.get(url)
        open(gzipname, 'wb').write(r.content)
    
    print("file name:", gzipname)

    with gzip.open(gzipname, 'rb') as f:
        for line in f:
            infile = json.loads(line)
            if infile["annotations"][0]["short_answers"] == []: #if there is no short answer, ignore this data point
                no_short += 1
                continue
            is_impossible = False
            #title = infile["example_id"]
            text = infile["document_html"]
            question = infile["question_text"]
            #question_id = random.randint(100000000,999999999)
            question_id = infile["example_id"]
        
            tok_ans = ""
            ans_idx = 0
            text_no_html = ""
            prev_token = ''
            h1start = False
            title = ""

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
                
                if token["token"] == '<H1>':
                    h1start = True
                
                if token["token"] == '</H1>' and title != "":
                    h1start = False

                if not token["html_token"]:
                    if prev_token != '' and prev_token != '(' and prev_token != '``' and prev_token != "'" and prev_token != '-' and prev_token != '--'  and (token["token"] == '(' or token["token"] == '``' or token["token"] == "'" or (token["token"].replace('.', '').isalnum())):
                        text_no_html += (' ' + token["token"])
                        if overlap:
                            ans_idx += 1
                            tok_ans += token["token"]
                        elif before_ans:
                            ans_idx += len(token["token"]) + 1
                        elif in_ans:
                            tok_ans += (' ' + token["token"])
                        if h1start:
                            if title == "":
                                title += token["token"]
                            else:
                                title += (' ' + token["token"])
                    else:
                        text_no_html += (token["token"])
                        if before_ans:
                            ans_idx += len(token["token"])
                        elif in_ans:
                            tok_ans += token["token"]
                        if h1start:
                            if title == "":
                                title += token["token"]
                            else:
                                title += token["token"]
                prev_token = token["token"]
                # elif in_ans: #accounts for the possibility that there could be html tokens within the answer token indexes, doesnt seem to be necissary
                #     if prev_token != '``' and prev_token != "'" and prev_token != '-' and prev_token != '--' and (prev_token != ':') and (token["token"] == '(' or token["token"] == '``' or token["token"] == "'" or (token["token"].replace('.', '').isalnum() and (prev_token == '' or prev_token != '('))):
                #         tok_ans += (' ' + token["token"])
                #     else:
                #         tok_ans += token["token"]
            # print(title)
            #print(text_no_html)
            #print(text_no_html[ans_idx:ans_idx+10])
            entry_list.append({"title" : title, "paragraphs" : [{"qas": [{"question": question, "id": question_id, "answers": [{"text": tok_ans, "answer_start": ans_idx}], "is_impossible": is_impossible}], "context": text_no_html}]})
            #ans_list.append((question, tok_ans))
            #print(tok_ans)
            j += 1
            print(j)
print("total examples: ", j+no_short)
final_string = {"version": "v2.0", "data": entry_list}
#with open('modified_GNQ_test.json', 'w') as outfile:
json.dump(final_string, outfile)