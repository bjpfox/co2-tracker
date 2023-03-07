from flask import Flask, render_template, request, redirect, session
from models.emissions import get_all_emissions, get_one_emission, get_emissions_by_date, get_first_emission_date, add_emission, edit_emission, delete_emission, emissions_accumulator, get_metrics, Emission
from models.users import login_user_action, signup_user_action
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import config

# TODO - get functions to calculate for different months ...should this be user controlled or do we just show 3 months of data for now?
# TODO - check code isnt counting dates that are start/end of a month range in both ranges
# TODO - should emission factors be stored in db or does this slow things down, can they just be stored in the python app since they wont change? 
# TODO - read other todos
# TODO - add ability to sort list 
# TODO - can dashboard be more interactive? split combo chart? add guage? 
# TODO - view should only list items from the logged in user - DONE
# TODO - fix up CSS to be more responsive to smaller screen sizes, etc - use viewport size instead of xx-large etc 
# TODO - show the calculated rate before user adds it (but JS calculated may not exactly match db calculated) 
# TODO - make login page on home page? 
# TODO - add form error checking for adit/edit form data - currently will throw error
# TODO - add some try except statements 
# TODO - layout - can the nav buttons side to the left of the foot, so more compact?
# TODO add a button to change charts, e.g. switch to 6 monthly, or turn offsets on/off
# TODO some metrics are off by <1% try and figure out why?
# or change size
# https://developers.google.com/chart/interactive/docs/animation
# export to csv toolbars: https://developers.google.com/chart/interactive/docs/gallery/toolbar


app = Flask(__name__)
app.config['SECRET_KEY'] = 'no one will ever guess this'

# Gokul: "Prevents confusion between web server gateway interface instances"
if __name__ == "__main__":
    app.run(debug = True)


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
    user_id = session['user_id']
    emissions = get_all_emissions(user_id)
    return render_template('emissions.html', emissions = emissions) 

@app.route('/dashboard')
def dashboard():
    user_id = session['user_id']

    # Fetch data for the below time period
    max_number_of_months = 6 # TODO make this customisable?
        
    # delta is the interval over which we'll present the data to the user on the combo chart (i.e. data is provided as a total for each month)
    delta = datetime.timedelta(days=30) # TODO, delta doesnt support months...can we make this robust?
    end_date = datetime.date.today()
    start_date_max_number_of_months = end_date - (delta * max_number_of_months)
    start_date_first_emission = get_first_emission_date(user_id)

    # Take the earliest emission, but dont show any more than 'max number of months'
    start_date = max(start_date_first_emission, start_date_max_number_of_months)

    emissions = get_emissions_by_date(start_date, end_date, user_id)
    if len(emissions) > 0: 
        
        # We run accumulator once for the full range, then grab out the data from each month needed
        # this is more efficient as it avoids overlap / recalculating multiple times
        # (e.g. the process of checking 3 months after the end date, would lead to duplication)
        [emissions_df, usage_df] = emissions_accumulator(start_date, end_date, user_id)

        # Put data into a suitable format for the Google Charts Pie Chart
        total_vals = emissions_df.sum().tolist()
        total_cols = emissions_df.sum().keys().tolist()
        pie_chart_data = [[x,abs(y)] for x,y in zip(total_cols, total_vals)] 

        # Get month by month data, and put into suitable format for the Google combo chart
        em_vals_data = []
        date_counter = start_date
        plot_empty_months = False
        for i in range(max_number_of_months):
            date_string = [f"{date_counter.year}/{date_counter.month}"]
            em_current_month = emissions_df[(emissions_df.Date.dt.month == date_counter.month) & (emissions_df.Date.dt.year == date_counter.year)].sum().tolist()
            
            # Once we find a non empty month, we don't need to check for future empty months (these will be plotted regardless)
            if sum(em_current_month)!= 0 or plot_empty_months:
                em_vals_data += [date_string + em_current_month]
                plot_empty_months = True

            date_counter += delta

        total_cols = ['Month'] + total_cols
        combo_chart_data = [total_cols] + em_vals_data
        
        # Get data in format to enable calculation of metrics
        # i.e. sum all values from the emissions and usage dataframes 
        total_usage = usage_df.sum()
        total_val_data = emissions_df.sum()
        metrics_dict = get_metrics(total_val_data, total_usage) 
        
        return render_template('dashboard.html', combo_chart_data = combo_chart_data, pie_chart_data = pie_chart_data, metrics_dict = metrics_dict) #, emissions = emissions) 
    
    else:
        return render_template('dashboard-empty.html')


# Enables the conversion from usage into kg CO2 
emission_rates = config.emission_rates 


@app.route('/add-emission-view')
def add_emission_view():
    emission_types = [key for key in emission_rates]
    return render_template('add-emission.html', emission_types = emission_types, mode = 'add') 


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
        print("Error4 - not found")
        return redirect('/')  
    return redirect('/view-emissions')


@app.route('/about')
def about():
    return render_template('about.html', user_name = session.get('user_name', 'UNKNOWN')) 

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    user_name = request.form.get('name', 'no_name') 
    user_email = request.form.get('email', 'no_email') 
    
    user_password = request.form.get('password', 'no_password') 
    user_password_confirm = request.form.get('password-confirm', 'no_password') 
    password_confirm_matches = user_password == user_password_confirm 
    if not password_confirm_matches:
        return render_template('signup.html', password_confirm_matches = False)
    
    if user_name != 'no_name' and user_email != 'no_email' and user_password != 'no_password':
        user_password_hash = generate_password_hash(user_password)
        signup_user_action(user_name, user_email, user_password_hash)
        return redirect('/view-emissions')
    
    return redirect('/login') 