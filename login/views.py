from flask import Flask,render_template, Blueprint, jsonify, request,redirect,url_for,make_response
from flaskext.mysql import MySQL



login=Blueprint('login',__name__,template_folder='templates',static_folder='static',static_url_path='/login/static')

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'btph'
app.config['MYSQL_DATABASE_HOST'] = 'localhost' # or your MySQL host

mysql = MySQL()
mysql.init_app(app)
 
 

@login.route('/')
def index():
    if(request.cookies.get('btph@groupe-hasnaoui.com')):
        response = redirect(url_for("dashboard.ff"))
        return response
     
    else:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS btph")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mycard (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            image VARCHAR(255) NOT NULL,
            fonction VARCHAR(255) NOT NULL,
            nom_entreprise VARCHAR(255) NOT NULL,
            groupe_s VARCHAR(255) NOT NULL          
            )
        ''') 
        conn.commit()
        cursor.close()
        conn.close()
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



