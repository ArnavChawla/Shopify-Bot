from __future__ import print_function
from flask import Flask
from flask import render_template
import requests
from flask import request
import json

from shopifytask import shopifytask
import glob, os
app = Flask(__name__)
stasks=[]

@app.route('/')
def hello():
        return render_template("blank_page.html")
@app.route('/creator')
def load():
    return render_template('blank_page.html')
@app.route('/', methods=['POST'])
def check_key():
    print(request.form)
    print(request.form['key'])
    data ={
            'key':request.form['key']
    }
    r = requests.post("http://www.redmond2828.club/check_auth", data=data)
    print(r.text)
    if(r.text == "true"):
        print("hi")
        return render_template('blank_page.html')
    return render_template('activation.html')
@app.route('/check_auth',methods=['POST'])
def checkKey():
    print(request.form)
    key = request.form["key"]
    f = open("keys.txt","r")
    lines = f.readlines()
    key = key+"\n"
    f.close()
    f = open("keys.txt","w")
    a = open("activated.txt","a+")
    print(key)
    for line in lines:
        print(line)
        if line == key:
            print("here")
            a.write(key)
            return 'true'
        else:
            f.write(line)
    f.close()
    a.close()

    return 'false'

@app.route('/create_profile', methods=['POST'])
def get_form():
    print(request.form)
    filePath = "./profiles/"+request.form["profile"]+".json"
    p = open(filePath, 'w+')
    json.dump(request.form, p)
    p.close()
    return render_template('blank_page.html')
@app.route('/task_create')
def create():
    data = []
    for file in glob.glob1(os.getcwd()+"/profiles", "*.json"):
        data.append(str(file).split(".")[0])
    return render_template('blank_page0.html',data=data)
@app.route('/start_task', methods=['POST'])
def task():
        print(request.form)
        print( request.form['profile'])
        task1 = supremetask.SupremeTask(request.form['profile'])
@app.route('/new_shopify', methods=['POST'])
def add():
    print(request.form)
    stasks.append(shopifytask(request.form["profile"],request.form["size"],request.form["keywords"],request.form["url"]))
    return render_template('task.html',data=stasks)
@app.route('/start_shopping', methods=['POST'])
def start_the_things():
    for task in stasks:
        task.run()
    return render_template('task.html', data=stasks)
if __name__ == "__main__":
    print ('oh hello')
    app.run(host='127.0.0.1', port=5000)
