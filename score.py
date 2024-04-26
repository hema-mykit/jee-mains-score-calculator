import requests
from bs4 import BeautifulSoup
import pdfplumber
import csv

data = []
records = []
scores = [0 for i in range(4)]

def get_data(fname):   
    ''' gets data from answer key html file'''   
    with open(fname, "r") as fp:
        contents = fp.read() 
        soup = BeautifulSoup(contents, 'html5lib')
        table = soup.find("table")
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if cells:
                data.append([cell.text for cell in cells])   


def get_records(fname):  
    with pdfplumber.open(fname) as pdf:    
        text = ''
        for pg in range(len(pdf.pages)):
            text = text + pdf.pages[pg].extract_text()        
        
        #split based on question
        ques_split = text.split('Q.')
        global candidate
        candidate = ques_split.pop(0).split('\n')       

        questions = []
        for ques in ques_split:
            if ques:
                lines= ques.split('\n')            
                if lines:
                    questions.append(lines)          
             
        for q in questions:   
            record = ['qno', 'question_type', 'question_id', 'q_status', 'chosen_opt', 'correct_opt', 'a_status', 'marks']   
            record[0] = q[0]
            opt_ids = []
                    
            for l in q:
                if "Question Type" in l:
                    record[1] = l.split('Question Type :')[1].strip()
                        
                if "Question ID" in l:
                    ques_id = l.split('Question ID :')[1].strip()
                    record[2] = ques_id
                            
                if "Status" in l:
                    record[3] = l.split('Status :')[1].strip()
                    if record[3] == '':
                        record[3] = "Not Attempted and Marked for Review"
                        
                if "Given" in l:
                    record[4] = l.split("Given")[1].strip()                    
                if "Option 1 ID" in l:
                    opt_ids.append(l.split('Option 1 ID : ')[1].strip())
                if "Option 2 ID" in l:
                    opt_ids.append(l.split('Option 2 ID : ')[1].strip())
                if "Option 3 ID" in l:
                    opt_ids.append(l.split('Option 3 ID : ')[1].strip())
                if "Option 4 ID" in l:
                    opt_ids.append(l.split('Option 4 ID : ')[1].strip())                    
                if "Chosen Option" in l:
                    opt = l.split("Chosen Option :")[1].strip()
                    if opt != "--":
                        record[4] = opt_ids[int(opt)-1]
                    else:
                        record[4] = opt                    
            records.append(record)   

    #************************* comparing response and anskeys **********************
    for rec in records:    
        for row in data:
            if row[0] == rec[2]:     #matching question id in data and records
                rec[5] = row[1]
                    
                if rec[4] == "--":
                    rec[6] = "Not Answered"
                    rec[7] = 0
                elif rec[1] == "MCQ" and rec[5] in rec[4] or rec[1] == "SA" and rec[5] == rec[4]:
                    rec[6] = "Correct"
                    rec[7] = 4
                else:
                    rec[6] = "Incorrect"
                    rec[7] = -1
                break
        
def find_score():    
    for i in range(30):       
        scores[0] += records[i][7]
        scores[1] += records[i+30][7]
        scores[2] += records[i+60][7]
    scores[3] = scores[0] + scores[1] + scores[2]    

def create_csv(fname):
    f = open(fname, 'w', newline='')  
    wobj = csv.writer(f)
    for i in range(1, 4):
        wobj.writerow([candidate[i]])
    wobj.writerow(['Qno', 'Question Type', 'Question ID', 'Status', 'Chosen Option', 'Correct Option', 'Answer Status', 'Marks'])
    for rec in records:
        wobj.writerow(rec)
    wobj.writerow([f"Mathematics: {scores[0]}"])
    wobj.writerow([f"Physics: {scores[1]}"])
    wobj.writerow([f"Chemistry: {scores[2]}"])
    wobj.writerow([f"Total Score: {scores[3]}"])
    f.close()





