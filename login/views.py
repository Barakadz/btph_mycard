from flask import Flask,render_template, Blueprint, jsonify, request,redirect,url_for,make_response
from flaskext.mysql import MySQL
import pymysql
 
 


 
login=Blueprint('login',__name__,template_folder='templates',static_folder='static',static_url_path='/login/static')
app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST'] = 'db'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'mydatabase'

mysql = MySQL(app)




 
 

@login.route('/')
def index():
    if(request.cookies.get('btph@groupe-hasnaoui.com')):
        
        cursor = mysql.get_db().cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS mycard (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), image VARCHAR(255), fonction VARCHAR(255), nom_entreprise VARCHAR(255), groupe_s VARCHAR(255),sou_traitont VARCHAR(255))")
        mysql.get_db().commit()
        cursor.close()

        response = redirect(url_for("dashboard.ff"))
        return response
     
    else:
        cursor = mysql.get_db().cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS mycard (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), image VARCHAR(255), fonction VARCHAR(255), nom_entreprise VARCHAR(255), groupe_s VARCHAR(255),sou_traitont VARCHAR(255))")
        mysql.get_db().commit()
        cursor.close()
 
       
        return render_template('index.html',error='')

@login.route('/login', methods=['POST','GET'])
def ggggg():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if(username !='btph@groupe-hasnaoui.com'  and password !='dsi2024'):
            error="Mail ou mot de passe incorrect"
            return render_template('index.html',error=error)
        else:
            response = redirect(url_for("dashboard.ff"))
            response.set_cookie(username,password)
            return response
    else: 
        return render_template('index.html',error='')



