from flask import Flask,render_template,request,url_for,redirect,jsonify,abort
from flask_mysqldb import MySQL
from flask_cors import CORS,cross_origin
import os
import psycopg2
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'images/'
conn = psycopg2.connect("postgres://fglsjwcckfrrvl:67273dcf40774a714b3886b7617a1f3931f77c5727efcc31d7bd5ec7185e73da@ec2-3-229-252-6.compute-1.amazonaws.com:5432/d434aon9972dqg")

def createTables():
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE REPORTS(
        ID serial  primary key,
        CATEGORY varchar(255), 
        LONGITUDE varchar(255),
        LATITUDE varchar(255),
        USER_ID int,
        IMAGENAME varchar(255),
        MESSAGE varchar(255))''')
    conn.commit()

def getCursor():
    return mysql.connection.cursor()
def commit():
    mysql.connection.commit()


@app.route("/create-table",methods=['GET'])
def createtables():
    createTables()
    return "created"


@app.route('/create-user',methods=['POST'])
def index():
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']
        password = data['password']
        cursor = conn.cursor()
        query=""" INSERT INTO USERS(name,email,password) VALUES(%s,%s,%s) """
        values = (name,email,password)
        cursor.execute(query,values)
        conn.commit()
        cursor.close()
        return data
    except:
        return jsonify(error="User was not created")

@app.route('/create-report',methods=['POST'])
def createReport():
    try:
        data = request.get_json()
        category = data['category']
        longitude = data['longitude']
        latitude = data['latitude']
        user_id = data['user_id']
        message = data['message']
        imageString = data["image"]
        image = Image.open(BytesIO(base64.b64decode(imageString)))
        day = datetime.now().day
        minute= datetime.now().minute
        name = str(day)+str(minute)+"image.jpg"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'],name))
        cursor = conn.cursor()
        query="""INSERT INTO REPORTS(category,longitude,latitude,user_id,message,imagename) VALUES(%s,%s,%s,%s,%s)"""
        values = (category,longitude,latitude,user_id,message,name)
        cursor.execute(query,values)
        conn.commit()
        cursor.close()
        return data
    except:
        return jsonify(error="Report was not created")

@app.route("/login",methods=['POST'])
def login():
    login_details = request.get_json()
    email = login_details['email']
    password = login_details['password']
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM USERS WHERE EMAIL =%s  AND PASSWORD=%s',(email,password))
    userData=cursor.fetchone()
    if userData is None:
        cursor.close()
        return jsonify(error="User not found")
    else:
        cursor.close()
        data ={}
        data['id']=userData[0]
        data['name']=userData[1]
        data['email']=userData[2]
        return data
 
@app.route("/get-count-by-category",methods=['GET'])
@cross_origin()
def getCountByCategory():
    cursor = conn.cursor()
    cursor.execute('SELECT category,count(*) FROM reports group by category')
    results = cursor.fetchall()
    graph_data =[]
    for result in results:
        data ={}
        data["name"]=result[0]
        data["value"]=result[1]
        graph_data.append(data)


    return graph_data
