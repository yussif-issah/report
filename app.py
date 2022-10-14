from flask import Flask,render_template,request,url_for,redirect,jsonify,abort
from flask_mysqldb import MySQL
from flask_cors import CORS,cross_origin
app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] =''
app.config['MYSQL_DB'] = 'Report'
 
mysql = MySQL(app)

def createTables():
    cursor = mysql.connection.cursor()
    cursor.execute(''' CREATE TABLE USERS(
        ID  int primary key auto_increment,
        NAME varchar(255), 
        EMAIL varchar(255),
        PASSWORD varchar(255))
        ''')
    cursor.execute('''CREATE TABLE REPORTS(
        ID int  primary key auto_increment,
        CATEGORY varchar(255), 
        LONGITUDE double,
        LATITUDE double,
        USER_ID int,
        MESSAGE VARCHAR(255),
        constraint FK_USER_ID foreign key(USER_ID) references USERS(ID)
        ON DELETE CASCADE)
        ''')
    mysql.connection.commit()
    cursor.close() 

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
        cursor = mysql.connection.cursor()
        cursor.execute('''
        INSERT INTO USERS(name,email,password) VALUES(%s,%s,%s)
        ''',(name,email,password))
        commit()
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
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO REPORTS(category,longitude,latitude,user_id,message) VALUES(%s,%s,%s,%s,%s)
            ''',(category,longitude,latitude,user_id,message))
        commit()
        cursor.close()
        return data
    except:
        return jsonify(error="Report was not created")

@app.route("/login",methods=['POST'])
def login():
    login_details = request.get_json()
    email = login_details['email']
    password = login_details['password']
    cursor = mysql.connection.cursor()
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
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT category,count(*) FROM reports group by category')
    results = cursor.fetchall()
    graph_data =[]
    for result in results:
        data ={}
        data["name"]=result[0]
        data["value"]=result[1]
        graph_data.append(data)


    return graph_data

if __name__=="__main__":
    app.debug = True
    app.run(host="0.0.0.0",port=1000)