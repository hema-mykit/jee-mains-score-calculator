import score
import os, shutil, tempfile
from flask import *

app = Flask(__name__)
app.secret_key = "hemamk"
app.config["UPLOAD_FOLDER"] = "./assets/"

fpath = app.config["UPLOAD_FOLDER"]


@app.route('/')
def index():    
    ''' intialize all variables'''
    score.data = []
    score.records = []
    score.scores = [0 for i in range(4)]   
    ''' remove all files in assets '''
    for filename in os.listdir(fpath):
        if os.path.isfile(os.path.join(fpath, filename)):
            os.remove(os.path.join(fpath, filename))
    return render_template('index.html')


@app.route('/result', methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        try:
            f1 = request.files['file1']
            f1.save(fpath + f1.filename)   
            f2 = request.files['file2']
            f2.save(fpath + f2.filename)  

            score.get_data(fpath + f2.filename)
            score.get_records(fpath + f1.filename)
            score.find_score()   

            os.remove(fpath + f1.filename) 
            os.remove(fpath + f2.filename)        
        except Exception as e:   
            flash("Oops! Something went wrong! Retry!")     
            return redirect(url_for('index'))        
        return render_template('score.html', scores = score.scores, candidate = score.candidate)


@app.route('/download',methods=["GET","POST"])
def download():     
    try:
        csv_fname = score.candidate[2].partition(" Name ")[2] + "_JEE_SCORE.csv"         
        path = fpath + csv_fname
        score.create_csv(path)
        cache = tempfile.NamedTemporaryFile()
        with open(path, 'rb') as fp:
            shutil.copyfileobj(fp, cache)
            cache.flush()
        cache.seek(0)
        os.remove(path)
        return send_file(cache, download_name=csv_fname)         
    except Exception as e:
        flash("Oops! Something went wrong! Retry!")     
        return redirect(url_for('index'))
    
if __name__ == '__main__':
   app.run(debug=True)        



