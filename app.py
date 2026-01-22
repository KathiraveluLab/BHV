from flask import Flask

app = Flask(__name__)

class Database:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        pass
    
    def disconnect(self):
        pass

class Auth:
    def __init__(self):
        pass
    
    def verify(self, token):
        pass

db = Database()
auth = Auth()

@app.before_first_request
def before_first_request():
    pass

@app.teardown_appcontext
def teardown_appcontext(exception):
    pass

@app.route('/')
def index():
    return 'BHV is running'

if __name__ == "__main__":
    app.run()
