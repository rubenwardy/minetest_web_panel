from flask import *

app = Flask(__name__)
app.config.from_pyfile('../config.cfg')

import views
