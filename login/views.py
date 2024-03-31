from flask import Flask,render_template, Blueprint, jsonify, request,redirect,url_for,make_response
 


login=Blueprint('login',__name__,template_folder='templates',static_folder='static',static_url_path='/login/static')

app = Flask(__name__)
 
 
 

@login.route('/')
def index():
    if(request.cookies.get('btph@groupe-hasnaoui.com')):
        response = redirect(url_for("dashboard.ff"))
        return response
    else:
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



