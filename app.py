from csv import field_size_limit
from email.policy import default
from fileinput import filename
from flask import Flask, redirect, render_template,request,send_file,send_from_directory,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
import os
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MyDB.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.secret_key="Don't Tell Anyone"
db=SQLAlchemy(app)

class MyFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    fileSize = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)
    dateTime=db.Column(db.Date, default=datetime.utcnow())
    url=db.Column(db.String(2083))
# Max size of the file
# app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

@app.route("/")
def ShowHTML():
    records_=ShowAllRecords()
    return render_template('MainPage.html',records=records_)

@app.route('/upload', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        if file_length <=0:
            return redirect('/')
        elif file_length>10000000:  #If File size is greater than 10mb
            flash("File Size is greater than 10mb")
            return redirect('/')
        else:
            size=convert_size(file_length)
            spliting_ = (str(request.base_url)).split("u")
            NextId=FindNextID()
            url=spliting_[0]+'download/'+str(NextId)
            upload = MyFile(filename=file.filename,fileSize=size, data=file.read(),url=url)
            db.session.add(upload)
            db.session.commit()
            # return f'Uploaded: {file.filename}'
    records_=ShowAllRecords()
    render_template('MainPage.html',records=records_)
    return redirect('/')

@app.route('/download/<upload_id>')
def download(upload_id):
    upload = MyFile.query.filter_by(id=upload_id).first()
    return send_file(BytesIO(upload.data), attachment_filename=upload.filename, as_attachment=True)

def ShowAllRecords():
    allRecords=MyFile.query.all()
    return allRecords

def FindNextID():
    NextId=len(MyFile.query.all())+1
    return NextId
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

if __name__ == "__main__":
    app.run(debug=True)