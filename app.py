from flask import Flask, render_template, request, redirect, session
from models.emissions import get_all_emissions
from models.users import login_user_action
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'no one will ever guess this'

# prevents confusion between web server gateway interface instances 
if __name__ == "__main__":
    app.run(debug = True)

# TODO - add the following routes


@app.route('/')
def index():
    return render_template('index.html') 

@app.get('/login')
def render_login_page():
    if 'user_name' not in session: 
        return render_template('login.html', user_name = session.get('user_name', 'UNKNOWN'))
    else:
        return redirect('/')

@app.post('/login')
def login_user():
    user_email = request.form.get('email','no_email')
    user_password = request.form.get('password','no_password')
    if user_email != 'no_email' and user_password != 'no_password':
        result = login_user_action(user_email)
        email_matches = result is not None and len(result.name) > 0
        if email_matches: 
            user_password_hash = result.password_hash 
            password_matches = check_password_hash(user_password_hash, user_password)
            if password_matches:
                print('password matches')
                session['user_id'] = result.id 
                session['user_email'] = result.email 
                session['user_name'] = result.name 
                return redirect('/')
    return render_template('login.html', user_name = session.get('user_name', 'UNKNOWN'), incorrect_password = True)
    


@app.route('/view-emissions')
def view_emissions():
    #co2_rates = get_co2_rates()
    emissions = get_all_emissions()
    return render_template('emissions.html', emissions = emissions) 

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html') #, emissions = emissions) 