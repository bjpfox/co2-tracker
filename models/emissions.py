from db import sql_select_one, sql_select_all, sql_write

# Hides the future warnings (currently appearing for pandas)
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


def get_all_emissions(user_id):
    emissions = sql_select_all("SELECT * FROM emissions WHERE user_id = '%s';", [user_id]) 
    emissions_list = []
    for event in emissions:
        emission = Emission(**event)
        emissions_list.append(emission)
    return emissions_list


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


def delete_emission(user_id, emission_id):
    sql_write("DELETE FROM emissions WHERE user_id = '%s' AND id = '%s';", [user_id, emission_id])


def add_emission(emissions_data):
    sql_write("INSERT INTO emissions (user_id, date, interval, amount, type, description) VALUES (%s, %s, %s, %s, %s, %s)", emissions_data)


def edit_emission(emissions_data):
    sql_write("UPDATE emissions SET user_id = %s, date = %s, interval = %s, amount = %s, type = %s, description = %s WHERE id = %s;", emissions_data)


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

    # Loop through day 
    # while (start_date <= end_date):
    # start_date += delta
    # formatted_date = start_date.strftime("%Y-%m-%d")
    # emissions = sql_select_all(f"SELECT * FROM emissions WHERE user_id = '%s' AND date = %s;", [user_id, formatted_date])

    if len(emissions) > 0:
        for event in emissions:
            #emission_type = row['type'] #['type']
            emission_type = event.type #['type']
            # usage_amount = row['amount']
            usage_amount = event.amount
            emission_rates = config.emission_rates 
            emission_rate = int(emission_rates[emission_type])
            emission_amount = usage_amount * emission_rate
            # emission_interval = row['interval']
            emission_interval = event.interval
            
            match emission_interval:
                case "QUARTERLY":
                    number_days = int(365/4)
                    daily_emission = emission_amount / (365 / 4)
                    daily_usage = usage_amount / (365 / 4)
                case "MONTHLY":
                    number_days = int(365/12)
                    daily_emission = emission_amount / (365 / 12)
                    daily_usage = usage_amount / (365 / 12)
                case "DAILY":
                    number_days = 1
                    daily_emission = emission_amount
                    daily_usage = usage_amount
            # emission_end_date = row['date']
            emission_end_date = event.date
            emission_start_date = emission_end_date - (delta * number_days)

            # Distribute the emissions across the respective time period (e.g. for a 1 month elec bill, distribute it across the 30 days)
            while (emission_start_date < emission_end_date):
                emissions_df = emissions_df.append({'Date': emission_start_date, emission_type: daily_emission}, ignore_index = True)
                usage_df = usage_df.append({'Date': emission_start_date, emission_type: daily_usage}, ignore_index = True)
                emission_start_date += delta
    total = emissions_df.sum()
    
    # Need to convert to pandas datatime format 
    # TODO consider do we really need dataframes / pandas?
    print('edf: ', emissions_df)
    if 'Date' in emissions_df:
        emissions_df['Date'] = emissions_df['Date'].apply(pd.to_datetime)
    if 'Date' in usage_df:
        usage_df['Date'] = usage_df['Date'].apply(pd.to_datetime)
    
    # total_monthly_emissions = emissions_df[(emissions_df.Date.dt.month == 2) & (emissions_df.Date.dt.year == 2023)].sum()
    # total_monthly_usage = usage_df[(usage_df.Date.dt.month == 2) & (usage_df.Date.dt.year == 2023)].sum()

    return [emissions_df, usage_df]

def get_metrics(total_monthly_emissions, total_monthly_usage):
        # Calc total g co2 metric
        co2_metric = int(sum(total_monthly_emissions)/1000)
        
        # Calc total elec
        if 'Electricity (VIC)' in total_monthly_usage:
            elec_metric = total_monthly_usage['Electricity (VIC)'] 
        else:
            elec_metric = 0
        
        # Calc total gas
        if 'Natural Gas' in total_monthly_usage:
            gas_metric = total_monthly_usage['Natural Gas']
        else: 
            gas_metric = 0
        
        # Calc total km travelled
        excluded_columns = ['Electricity (VIC)', 'Natural Gas', 'Offset', 'Other']
        km_metric = total_monthly_usage.drop(excluded_columns, errors='ignore').sum() 

        # Calc total offsets, divide by 1000 to convert from g to kg CO2  
        if 'Offset' in total_monthly_emissions:
            offsets_metric = int(total_monthly_emissions['Offset']/(-1000))
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
    
