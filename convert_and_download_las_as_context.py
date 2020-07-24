import os.path
import json
import gzip
from io import StringIO
import requests

#new version with long answer as context

entry_list = []
ans_list = []
j = 0
no_short = 0
no_long = 0

# to reformat the training data
for i in range(50):
    if i < 10: gzipname = 'v1.0_train_nq-train-'+'0'+str(i)+'.jsonl.gz'
    else: gzipname = 'v1.0_train_nq-train-'+str(i)+'.jsonl.gz'
    
    # download publically available files if not already downloaded
    if (not os.path.isfile(gzipname)):
        url = 'https://storage.googleapis.com/natural_questions/v1.0/train/nq-train-'+str(i)+'.jsonl.gz'
        r = requests.get(url)
        open(gzipname, 'wb').write(r.content)

# to reformat the dev set, uncomment lines below and comment out lines 17-25  
#for i in range(5):
    #gzipname = 'nq-dev-0'+str(i)+'.jsonl.gz'
    
    print("file name:", gzipname)

    with gzip.open(gzipname, 'rb') as f:
        for line in f:
            # if you want to only reformat a certain number of examples, uncomment the next line and insert number
            #if j >= 1560: break
            infile = json.loads(line)
            is_impossible = False
            if infile["annotations"][0]["short_answers"] == []: #if there is no short answer
                no_short += 1
                is_impossible = True
            
            if infile["annotations"][0]["long_answer"]["start_token"] == -1: #need the long answer for context
                no_long += 1
                continue
            text = infile["document_html"]
            question = infile["question_text"]
            question_id = infile["example_id"] #can be negative
            la_start_token = infile["annotations"][0]["long_answer"]["start_token"]
            la_end_token = infile["annotations"][0]["long_answer"]["end_token"]
            tok_ans = ""
            ans_idx = 0
            text_no_html = ""
            prev_token = ''
            h1start = False
            title = ""
            for i in range(len(infile["document_tokens"])):
                token = infile["document_tokens"][i]
                if token["token"] == '<H1>':
                        h1start = True  
                if token["token"] == '</H1>' and title != "":
                        h1start = False
                        break
                if not token["html_token"]:
                    if prev_token != '' and prev_token != '(' and prev_token != '``' and prev_token != "'" and prev_token != '-' and prev_token != '--'  and (token["token"] == '(' or token["token"] == '``' or token["token"] == "'" or (token["token"].replace('.', '').isalnum())):
                        if h1start:
                            if title == "":
                                title += token["token"]
                            else:
                                title += (' ' + token["token"])
                    else:
                        if h1start:
                            if title == "":
                                title += token["token"]
                            else:
                                title += token["token"]
                    prev_token = token["token"]
            prev_token = ''

            if is_impossible:
                #print(line)
                for i in range(la_start_token, la_end_token):
                    token = infile["document_tokens"][i]
                    if not token["html_token"]:
                        if prev_token != '' and prev_token != '(' and prev_token != '``' and prev_token != "'" and prev_token != '-' and prev_token != '--'  and (token["token"] == '(' or token["token"] == '``' or token["token"] == "'" or (token["token"].replace('.', '').isalnum())):
                            text_no_html += (' ' + token["token"])
                        else:
                            text_no_html += (token["token"])      
                        prev_token = token["token"]

            else:
                for i in range(la_start_token, la_end_token):
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
                                tok_ans += token["token"]
                            elif before_ans:
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
            if is_impossible and text_no_html == "":
                print(la_start_token, la_end_token)


            if not is_impossible and text_no_html[ans_idx:ans_idx+2] != tok_ans[:2]:
                print("answer_idx")
                print(text_no_html[ans_idx:ans_idx+1])
                print("real_ans")
                print(tok_ans)
    
            if is_impossible:
                entry_list.append({"title" : title, "paragraphs" : [{"qas": [{"plausible_answers": [{}], "question": question, "id": question_id, "answers": [], "is_impossible": is_impossible}], "context": text_no_html}]})
            else:
                entry_list.append({"title" : title, "paragraphs" : [{"qas": [{"question": question, "id": question_id, "answers": [{"text": tok_ans, "answer_start": ans_idx}], "is_impossible": is_impossible}], "context": text_no_html}]})
            j += 1
            print(j)
final_string = {"version": "v2.0", "data": entry_list}
with open('modified_GNQ_test.json', 'w') as outfile:
    json.dump(final_string, outfile)