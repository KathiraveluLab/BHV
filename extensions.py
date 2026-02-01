from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth

csrf = CSRFProtect()
oauth = OAuth() 
