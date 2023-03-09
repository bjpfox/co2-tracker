from db import sql_select_one, sql_select_all, sql_write

# Hides future warnings (currently appearing for pandas)
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import datetime 
import pandas as pd
import config

class Emission:
    def __init__(self, id, user_id, date, interval, amount, type, description):
        self.id = id
        self.user_id = user_id
        self.date = date
        self.interval = interval
        self.amount = amount
        self.type = type
        self.description = description
    def get_units(self):
        match self.type:
            case 'Electricity (VIC)':
                return 'kWh'
            case 'Natural Gas':
                return 'MJ'
            case 'Other':
                return 'g CO2'
            case 'Offset':
                return 'g CO2'
            case _:
                return 'km'
    def get_date(self):
        return self.date.strftime('%m %B, %Y')


def get_all_emissions(user_id, sort_by=None):
    if sort_by is not None:
        emissions = sql_select_all(f"SELECT * FROM emissions WHERE user_id = {user_id} ORDER BY {sort_by};") 
    else: 
        emissions = sql_select_all(f"SELECT * FROM emissions WHERE user_id = {user_id}") 
    emissions_list = []
    for event in emissions:
        emission = Emission(**event)
        emissions_list.append(emission)
    return emissions_list
    # id SERIAL PRIMARY KEY, -- list id
    # user_id INT,
    #     CONSTRAINT fk_emissions_users
    #     FOREIGN KEY (user_id)
    #     REFERENCES users(id), 
    # date DATE, -- where event spans more than 1 day, this is taken to be the last day 
    # interval VARCHAR(10), -- OPTIONS: DAILY, WEEKLY, MONTHLY, QUARTERLY
    # amount INT, -- g_c02 equivalent for the emissions event 
    # -- amount_daily INT, -- g_c02 equivalent for a single day event 
    # -- amount_weekly INT, -- g_c02 equivalent total across a week (e.g. a weeks worth of commuting - TODO add later)
    # -- amount_monthly INT, -- g_c02 equivalent total for a month (e.g. elec bill)
    # -- amount_quarterly INT, -- g_c02 equivalent total for a quarter (e.g. gas bill)
    # type VARCHAR(100), -- e.g. car, plane, train, electricity, natural gas
    # description VARCHAR(300)

def get_emissions_by_date(start_date, end_date, user_id):
    emissions = sql_select_all("SELECT * FROM emissions WHERE user_id = '%s' AND date BETWEEN %s AND %s;", [user_id, start_date, end_date]) 
    emissions_list = []
    for event in emissions:
        emission = Emission(**event)
        emissions_list.append(emission)
    return emissions_list


def get_one_emission(user_id, emission_id):
    emission_response = sql_select_one("SELECT * FROM emissions WHERE user_id = '%s' AND id = '%s';", [user_id, emission_id]) 
    emission = Emission(**emission_response)
    return emission


def get_first_emission_date(user_id):
    first_emission_date = sql_select_one("SELECT date FROM emissions WHERE user_id = '%s' ORDER BY date ASC LIMIT 1", [user_id])
    print(first_emission_date)
    if (first_emission_date is not None) and ('date' in first_emission_date):
        return first_emission_date['date']
    else:
        return False #datetime.date.today()


def delete_emission(user_id, emission_id):
    sql_write("DELETE FROM emissions WHERE user_id = '%s' AND id = '%s';", [user_id, emission_id])


def add_emission(emissions_data):
    sql_write("INSERT INTO emissions (user_id, date, interval, amount, type, description) VALUES (%s, %s, %s, %s, %s, %s)", emissions_data)


def edit_emission(emissions_data):
    sql_write("UPDATE emissions SET user_id = %s, date = %s, interval = %s, amount = %s, type = %s, description = %s WHERE id = %s;", emissions_data)


def distribute_emissions(emissions_df, usage_df, emissions, delta):
    if len(emissions) > 0:
        for event in emissions:
            emission_type = event.type #['type']
            usage_amount = event.amount
            emission_rates = config.emission_rates 
            emission_rate = int(emission_rates[emission_type])
            emission_amount = usage_amount * emission_rate
            emission_interval = event.interval
        
            # Note: this is approximate only, since # of days varies depending on
            # what month (28/30/31), quarter (Q1-Q4), and year (365/366) it is. 
            # Consider asking user for start and end date so we can caluclate exact number of days 
            match emission_interval:
                case "QUARTERLY":
                    number_days = int(365/4)
                    daily_emission = emission_amount / int(365 / 4)
                    daily_usage = usage_amount / int(365 / 4)
                case "MONTHLY":
                    number_days = int(365/12)
                    daily_emission = emission_amount / int(365 / 12)
                    daily_usage = usage_amount / int(365 / 12)
                case "DAILY":
                    number_days = 1
                    daily_emission = emission_amount
                    daily_usage = usage_amount
            emission_end_date = event.date
            emission_start_date = emission_end_date - (delta * number_days)

            # Distribute the emissions across the respective time period (e.g. for a 1 month elec bill, distribute it across the 30 days)
            while (emission_start_date < emission_end_date):
                emissions_df = emissions_df.append({'Date': emission_start_date, emission_type: daily_emission}, ignore_index = True)
                usage_df = usage_df.append({'Date': emission_start_date, emission_type: daily_usage}, ignore_index = True)
                emission_start_date += delta
    return [emissions_df, usage_df]


# Calculates the total co2 emissions from all sources, for a given start date and end date
def emissions_accumulator(start_date, end_date, user_id):
    # Events covering multiple days are stored based on their end date 
    # Longest emission event period is quarterly, so we need to check 91 days past the end date of interest, to ensure we capture any bills within the period 
    delta = datetime.timedelta(days=1)
    time_offset = 91 * delta # number of days past the end of period of interest that we need to fetch data for
    df_cols = []
    emissions_df = pd.DataFrame(columns=df_cols)
    usage_df = pd.DataFrame(columns=df_cols)
    
    # Fetch all emission events relevant to the period of interest
    emissions = get_emissions_by_date(start_date, end_date + time_offset, user_id)

    # Distribute the emissions from each event (e.g. a 3 month gas bill) across time
    [emissions_df, usage_df] = distribute_emissions(emissions_df, usage_df, emissions, delta)

    if 'Date' in emissions_df:
        emissions_df['Date'] = emissions_df['Date'].apply(pd.to_datetime)
    if 'Date' in usage_df:
        usage_df['Date'] = usage_df['Date'].apply(pd.to_datetime)
    
    return [emissions_df, usage_df]


def get_metrics(total_emissions, total_usage):
        # Calc total g co2 metric
        co2_metric = int(sum(total_emissions)/1000)
        
        # Calc total elec
        if 'Electricity (VIC)' in total_usage:
            elec_metric = total_usage['Electricity (VIC)'] 
        else:
            elec_metric = 0
        
        # Calc total gas
        if 'Natural Gas' in total_usage:
            gas_metric = total_usage['Natural Gas']
            print('gas metric: ', gas_metric)
        else: 
            gas_metric = 0
        
        # Calc total km travelled
        excluded_columns = ['Electricity (VIC)', 'Natural Gas', 'Offset', 'Other']
        km_metric = total_usage.drop(excluded_columns, errors='ignore').sum() 

        # Calc total offsets, divide by 1000 to convert from g to kg CO2  
        if 'Offset' in total_emissions:
            offsets_metric = int(total_emissions['Offset']/(-1000))
        else: 
            offsets_metric = 0

        metrics_dict = {
            'co2': co2_metric,
            'elec': elec_metric,
            'gas': gas_metric,
            'km': km_metric,
            'offsets': offsets_metric
            }
        return metrics_dict
    
    
def get_pie_chart_data(emissions_df):
    total_vals = emissions_df.sum().tolist()
    column_names = emissions_df.sum().keys().tolist()
    pie_chart_data = [[x,abs(y)] for x,y in zip(column_names, total_vals)] 
    return pie_chart_data

            
def get_combo_chart_data(start_date, delta, max_number_of_months, emissions_df):
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
    column_names = emissions_df.sum().keys().tolist()
    column_names = ['Month'] + column_names 
    combo_chart_data = [column_names] + em_vals_data
    return combo_chart_data