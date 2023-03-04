from flask import Flask, render_template, request, redirect, session
from models.emissions import get_all_emissions, emissions_accumulator, get_metrics
from models.users import login_user_action
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'no one will ever guess this'

# prevents confusion between web server gateway interface instances 
if __name__ == "__main__":
    app.run(debug = True)

# TODO - add the following routes


@app.route('/')
def index():
    return render_template('index.html', user_name = session.get('user_name', 'UNKNOWN')) 

@app.get('/login')
def render_login_page():
    if 'user_name' not in session: 
        return render_template('login.html', user_name = session.get('user_name', 'UNKNOWN'))
    else:
        return redirect('/dashboard')

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
                return redirect('/dashboard')
    return render_template('login.html', user_name = session.get('user_name', 'UNKNOWN'), incorrect_password = True)
    
@app.route('/logout')
def logout_user():
    session.pop('user_id')
    session.pop('user_name')
    session.pop('user_email')
    return redirect('/login')

@app.route('/view-emissions')
def view_emissions():
    #co2_rates = get_co2_rates()
    emissions = get_all_emissions()
    return render_template('emissions.html', emissions = emissions) 

@app.route('/dashboard')
def dashboard():
    start_date = datetime.date(2022, 12, 2)
    end_date = datetime.date(2023, 3, 2)
    user_id = session['user_id']
    [monthly_emissions, monthly_usage] = emissions_accumulator(start_date, end_date, user_id)
    metrics_dict = get_metrics(monthly_emissions, monthly_usage)
    print('monthly: ', monthly_emissions)
    print(type(monthly_emissions))
    # Google Charts requires in list format, rather than dataframe
    em_vals = monthly_emissions.tolist()
    em_cols = monthly_emissions.keys().tolist()
    print('c: ', em_cols)
    print('v: ', em_vals)
    pie_chart_data = [[x,y] for x,y in zip(em_cols, em_vals)]
    em_cols_data = ['Month'] + em_cols
    em_vals_data_1 = ['2023/01'] + em_vals
    em_vals_data_2 =  ['2023/02'] + em_vals
    em_vals_data_3 = ['2023/03'] + em_vals
    print('c: ', em_cols_data)
    print('v: ', em_vals_data_1)
    print('pie chart: ', pie_chart_data) 
    return render_template('dashboard.html', combo_chart_data = [em_cols_data, em_vals_data_1, em_vals_data_2, em_vals_data_3], pie_chart_data = pie_chart_data, metrics_dict = metrics_dict) #, emissions = emissions) 

    # TODO get this so its pulling three distinct months of data
    # eventually want it to auto update based on todays date
    # and do more than 3 months

    # TODO add functions for the metrics

@app.route('/about')
def about():
    return render_template('about.html', user_name = session.get('user_name', 'UNKNOWN')) 
