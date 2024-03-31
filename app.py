from flask import Flask
from dashboard.views import dash

from login.views import login
 
app= Flask(__name__)
app.register_blueprint(dash)

app.register_blueprint(login)

 