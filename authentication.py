from flask_httpauth import HTTPBasicAuth
from users import users
auth = HTTPBasicAuth()

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

#end authentication
