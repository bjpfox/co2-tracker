from flask import Flask, render_template, request, redirect, session
from models.emissions import get_all_emissions, get_one_emission, add_emission, edit_emission, delete_emission, emissions_accumulator, get_metrics, Emission
from models.users import login_user_action
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# TODO - add forms - 
# signup 
# add emissions to list - DONE
# edit an emission from list - DONE
# delete an emission from list - DONE
# TODO - get functions to calculate for different months ...should this be user controlled or do we just show 3 months of data for now?
# TODO - add offsets ability so that gets subtracted? Store as a negative number in db? should this be a separate form?
# TODO - should emission factors be stored in db or does this slow things down, can they just be stored in the python app since they wont change? 
# TODO - read other todos
# TODO - add ability to sort list 
# TODO - can dashboard be more interactive? 
# TODO - view should only list items from the logged in user - DONE
# TODO - fix up CSS to be more responsive to smaller screen sizes, etc - use viewport size instead of xx-large etc 
# TODO - show the calculated rate before user adds it (but JS calculated may not exactly match db calculated) 


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
    user_id = session['user_id']
    emissions = get_all_emissions(user_id) # TODO ideally this could have a time interval specified as well
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

    
emission_rates = {
    'Train': '22',
    'Bus': '22',
    'Plane': '158',
    'Car - Plug In Hybrid': '51',
    'Car - Battery Electric': '0',
    'Car - Typical Petrol': '164',
    'Car - Typical Diesel': '176',
    'Car - Micro': '116',
    'Car - Light': '132',
    'Car - Medium': '137',
    'Car - Large': '198',
    'Car - People Mover': '212',
    'Car - Small/Medium SUV': '156',
    'Car - Large SUV': '195',
    'Motorbike': '110',
    'Electricity (VIC)': '1600',
    'Natural Gas': '69'
}

@app.route('/add-emission-view')
def add_emission_view():
    emission_types = [key for key in emission_rates]
    print(emission_types)
    # selected_emission = "blank" # todo combine this with edit, todo - use emission rates from python, not db
    return render_template('add-emission.html', emission_types = emission_types, mode = 'add') #selected_emission = selected_emission, 


@app.post('/add-emission-write')
def add_emission_write():
    user_id = session['user_id']
    type = request.form['type']
    amount = int(request.form['amount'])
    interval = request.form['interval'].upper()
    date = request.form['date'] 
    description = request.form['description']
    emissions_data = [user_id, date, interval, amount, type, description]
    add_emission(emissions_data)
    
    return redirect('/view-emissions')


@app.route('/edit-emission-view')
def edit_emission_view():
    emission_types = [key for key in emission_rates]
    emission_id = int(request.args.get('id'))
    user_id = session['user_id']
    emission_data = get_one_emission(user_id, emission_id)
    print('ed: ', emission_data)
    return render_template('add-emission.html', event = emission_data, emission_types = emission_types, mode = 'edit')

    
@app.post('/edit-emission-write')
def edit_emission_write():
    user_id = session['user_id']
    event_id = request.form['id'] 
    type = request.form['type']
    amount = int(request.form['amount'])
    interval = request.form['interval'].upper()
    date = request.form['date'] 
    description = request.form['description']
    emissions_data = [user_id, date, interval, amount, type, description, event_id]
    edit_emission(emissions_data)
    return redirect('/view-emissions')


@app.route('/delete-emission-view')
def delete_emission_view():
    try:
        user_id = session['user_id'] 
        emission_id = int(request.args.get('id'))
        emission = get_one_emission(user_id, emission_id)
    except:
        print("Error3 - not found")
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
        print("Error3 - not found")
        return redirect('/')  
    return redirect('/view-emissions')



@app.route('/about')
def about():
    return render_template('about.html', user_name = session.get('user_name', 'UNKNOWN')) 
