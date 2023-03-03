from flask import Flask, render_template, request, redirect, session
from models.emissions import get_all_emissions

app = Flask(__name__)

# prevents confusion between web server gateway interface instances 
if __name__ == "__main__":
    app.run(debug = True)

# TODO - add the following routes


@app.route('/')
def index():
    return render_template('index.html') 


@app.route('/view-emissions')
def view_emissions():
    #co2_rates = get_co2_rates()
    emissions = get_all_emissions()
    return render_template('emissions.html', emissions = emissions) 