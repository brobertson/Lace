from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

users = {
    "john": "Hello",
    "susan": "byebye"
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

#end authentication
