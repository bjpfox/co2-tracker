from db import sql_select_one, sql_select_all, sql_write

class User:
    def __init__(self, id, name, email, password_hash):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        

def login_user_action(user_email):
    user_response = sql_select_one("SELECT * FROM users WHERE email = %s;", [user_email])
    if user_response is not None and len(user_response) > 0:
        user = User(user_response['id'], user_response['name'], user_response['email'], user_response['password_hash'])
    else:
        user = None
    return user

def signup_user_action(name, email, password_hash):
    sql_write("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s);", [name, email, password_hash])
    