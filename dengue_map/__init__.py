from flask import Flask

import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost/vietnam_dengue'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from dengue_map import views
