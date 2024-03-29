from flask import Flask, render_template, request, redirect, session
from models.emissions import get_all_emissions, get_one_emission, get_emissions_by_date, get_first_emission_date, get_pie_chart_data, get_combo_chart_data, get_line_chart_data, add_emission, edit_emission, delete_emission, emissions_accumulator, get_metrics, Emission
from models.users import login_user_action, signup_user_action, isValidEmail
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import config
import os
import re


SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY 

# Gokul: "Prevents confusion between web server gateway interface instances"
if __name__ == "__main__":
    app.run(debug = True)

# Enables the conversion from usage into kg CO2 
emission_rates = config.emission_rates 

@app.before_request
def is_user_logged_in():
    path = request.path
    routes_not_requiring_auth = ['/login', '/signup', '/', '/static/css/styles.css', '/static/img/iceberg.jpg', '/static/img/carbon_footprint.png', '/static/img/calculator_icon.png', '/static/img/graph_icon.png', '/static/img/bill_icon.png', '/static/javascript/form-validation.js', '/about']
    if path not in routes_not_requiring_auth and session.get('user_id') is None: 
        return redirect('/login')
    

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
    try:
        if user_email != 'no_email' and user_password != 'no_password':
            result = login_user_action(user_email)
            email_matches = result is not None and len(result.name) > 0
        if email_matches: 
            user_password_hash = result.password_hash 
            password_matches = check_password_hash(user_password_hash, user_password)
            if password_matches:
                session['user_id'] = result.id 
                session['user_email'] = result.email 
                session['user_name'] = result.name 
                return redirect('/dashboard')
    except: 
        print('something went wrong')
        return render_template('login.html')
    return render_template('login.html', user_name = session.get('user_name', 'UNKNOWN'), incorrect_password = True)
    
@app.route('/logout')
def logout_user():
    session.pop('user_id')
    session.pop('user_name')
    session.pop('user_email')
    return redirect('/login')

@app.route('/view-emissions')
def view_emissions():
    user_id = session['user_id']
    sort_by = request.args.get('sortby') 
    print('we got B')
    match sort_by: 
        case "id-asc": 
            sort_by = 'id ASC'
        case "id-desc":
            sort_by = 'id DESC'
        case "date-asc":
            sort_by = 'date ASC'
        case "date-desc":
            sort_by = 'date DESC'
        case "interval-asc":
            sort_by = 'LOWER(interval) ASC'
        case "interval-desc":
            sort_by = 'LOWER(interval) DESC'
        case "amount-asc":
            sort_by = 'amount ASC'
        case "amount-desc":
            sort_by = 'amount DESC'
        case "type-asc":
            sort_by = 'LOWER(type) ASC'
        case "type-desc":
            sort_by = 'LOWER(type) DESC'
        case "description-asc":
            sort_by = 'LOWER(description) ASC'
        case "description-desc":
            sort_by = 'LOWER(description) DESC'
        case _:
            sort_by = 'id ASC'
    emissions = get_all_emissions(user_id, sort_by)
    return render_template('emissions.html', emissions = emissions) 

@app.route('/dashboard')
def dashboard():
    user_id = session['user_id']

    # Fetch data for the below time period
    max_number_of_months = 6 
        
    # delta is the interval over which we'll present the data to the user on the combo chart (i.e. data is provided as a total for each month)
    delta = datetime.timedelta(days=30) 
    end_date = datetime.date.today()
    start_date_max_number_of_months = end_date - (delta * max_number_of_months)
    
    start_date_first_emission = get_first_emission_date(user_id)
    if not start_date_first_emission:
        return render_template('dashboard-empty.html')
    
    # Take the earliest emission, but dont show any more than 'max number of months'
    start_date = max(start_date_first_emission, start_date_max_number_of_months)


    try: 
        # We run accumulator once for the full range, then grab out the data from each month needed
        # this is more efficient as it avoids overlap / recalculating multiple times
        # (e.g. the process of checking 3 months after the end date, would lead to duplication)
        [emissions_df, usage_df] = emissions_accumulator(start_date, end_date, user_id)

        # Put data into a suitable format for the Google Charts Pie Chart
        pie_chart_data = get_pie_chart_data(emissions_df) 

        # Get month by month data, and put into suitable format for the Google combo chart
        combo_chart_data = get_combo_chart_data(start_date, delta, max_number_of_months, emissions_df)

        # Get line chart data (week by week), and put into suitable format for Google Charts Line Chart
        delta = datetime.timedelta(days=7) 
        max_number_of_weeks = 26
        start_date_max_number_of_weeks = end_date - (delta * max_number_of_weeks)
        start_date = max(start_date_first_emission, start_date_max_number_of_weeks)
        line_chart_data = get_line_chart_data(start_date, delta, max_number_of_weeks, emissions_df)
            
        # Get data in format to enable calculation of metrics
        # i.e. sum all values from the emissions and usage dataframes 
        total_usage = usage_df.sum()
        total_emissions = emissions_df.sum()
        metrics_dict = get_metrics(total_emissions, total_usage) 
        return render_template('dashboard.html', combo_chart_data = combo_chart_data, pie_chart_data = pie_chart_data, metrics_dict = metrics_dict, line_chart_data = line_chart_data) #, emissions = emissions) 
    
    except: 
        return render_template('dashboard-empty.html')

# Render the add emission page
@app.route('/add-emission-view')
def add_emission_view():
    return render_template('add-emission.html', emission_rates = config.emission_rates_by_category, mode = 'add') 

# Add the new emission to the db 
@app.post('/add-emission-write')
def add_emission_write():
    try: 
        user_id = session['user_id']
        type = request.form['type']
        amount = int(request.form['amount'])
        interval = request.form['interval'].upper()
        date = request.form['date'] 
        description = request.form['description']
        emissions_data = [user_id, date, interval, amount, type, description]
        add_emission(emissions_data)
    except: 
        return redirect('/')
    return redirect('/view-emissions')

# Render the edit emission page
@app.route('/edit-emission-view')
def edit_emission_view():
    try:
        emission_types = [key for key in config.emission_rates]
        emission_id = int(request.args.get('id'))
        user_id = session['user_id']
        emission_data = get_one_emission(user_id, emission_id)
    except:
        return redirect('/')
    return render_template('edit-emission.html', event = emission_data, emission_types = emission_types, mode = 'edit')

# Update db with the updated emission data 
@app.post('/edit-emission-write')
def edit_emission_write():
    try:
        user_id = session['user_id']
        event_id = request.form['id'] 
        type = request.form['type']
        amount = int(request.form['amount'])
        interval = request.form['interval'].upper()
        date = request.form['date'] 
        description = request.form['description']
        emissions_data = [user_id, date, interval, amount, type, description, event_id]
        edit_emission(emissions_data)
    except:
        return redirect('/')
    return redirect('/view-emissions')


@app.route('/delete-emission-view')
def delete_emission_view():
    try:
        user_id = session['user_id'] 
        emission_id = int(request.args.get('id'))
        emission = get_one_emission(user_id, emission_id)
    except:
        return redirect('/')  
    return render_template('delete-emission.html', event = emission)

    
@app.post('/delete-emission-write')
def delete_emission_write():
    try:
        user_id = session['user_id'] 
        print('uid', user_id)
        emission_id = int(request.form.get('id'))
        print('eid', emission_id)
        delete_emission(user_id, emission_id)
    except:
        return redirect('/')  
    return redirect('/view-emissions')


@app.route('/about')
def about():
    return render_template('about.html', user_name = session.get('user_name', 'UNKNOWN')) 


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    try:
        user_name = request.form.get('name', 'no_name') 
        user_email = request.form.get('email', 'no_email') 
        user_password = request.form.get('password', 'no_password') 
        user_password_confirm = request.form.get('password-confirm', 'no_password') 
        password_confirm_matches = user_password == user_password_confirm 
        
        if not password_confirm_matches:
            return render_template('signup.html', password_confirm_matches = False)
        
        email_valid = isValidEmail(user_email)
        if not email_valid:
            return render_template('signup.html', valid_email = False)
        
        
        if user_name != 'no_name' and user_email != 'no_email' and user_password != 'no_password':
            user_password_hash = generate_password_hash(user_password)
            signup_user_action(user_name, user_email, user_password_hash)
            result = login_user_action(user_email)
            session['user_id'] = result.id 
            session['user_email'] = result.email 
            session['user_name'] = result.name 
            return redirect('/view-emissions')
    except:
        return redirect('/')
    return redirect('/login') 