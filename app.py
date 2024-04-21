from flask import Flask
from dashboard.views import dash
import flask
from login.views import login

print(flask.__version__)

  
app= Flask(__name__)
app.register_blueprint(dash)

app.register_blueprint(login)

 