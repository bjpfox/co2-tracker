from db import sql_select_one, sql_select_all, sql_write
import datetime 
import pandas as pd


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
        print(event)
        emission = Emission(**event)
        print(emission)
        print('em units: ', emission.get_units())
        emissions_list.append(emission)
        # emissions_list.append(event)
    print(emissions_list)
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
    delta = datetime.timedelta(days=1)
    df_cols = ['Date', 'Electricity', 'Gas', 'Car', 'Motorbike', 'Train', 'Bus', 'Plane', 'Other', 'Offset']
    emissions_df = pd.DataFrame(columns=df_cols)
    usage_df = pd.DataFrame(columns=df_cols)

    while (start_date <= end_date):
        # print('sd: ', start_date)
        start_date += delta
        formatted_date = start_date.strftime("%Y-%m-%d")
        # print('fd: ', formatted_date)
        emissions = sql_select_all(f"SELECT * FROM emissions WHERE user_id = '%s' AND date = %s;", [user_id, formatted_date])
        # print(emissions)
        if len(emissions) > 0:
            for row in emissions:
                print('row: ', row)
                emission_type = row['type'] #['type']
                print(emission_type)
                usage_amount = row['amount']
                

                # cars_list = ['Car - Plug In Hybrid', 'Car - Battery Electric', 'Car - Typical Petrol', 'Car - Typical Diesel', 'Car - Micro', 'Car - Light', 'Car - Medium', 'Car - Large', 'Car - People Mover', 'Car - Small/Medium SUV', 'Car - Large SUV']
                # electricity_list = ['Electricity (VIC)'] # TODO add other states
                # if emission_type in cars_list:
                #     df_col = 'Car'
                # elif emission_type in electricity_list: 
                #     df_col = 'Electricity'    
                # else:
                #     df_col = emission_type
                if emission_type == 'Natural Gas' or emission_type == 'Electricity (VIC)':
                    emission_rate = sql_select_one(f"SELECT rate FROM emission_rates_energy WHERE name = %s;", [emission_type])['rate']
                elif emission_type != 'Offset' and emission_type != 'Other':
                    emission_rate = sql_select_one(f"SELECT rate FROM emission_rates_transport WHERE name = %s;", [emission_type])['rate']
                elif emission_type == 'Offset':
                    print('we found an offset!')
                    emission_rate = -1
                elif emission_type == 'Other':
                    print('we found an other!')
                    emission_rate = 1
                print('emission rate: ', emission_rate)
                emission_amount = usage_amount * emission_rate
                print('emission amt: ', emission_amount)  
                # print(emission_amount)
                emission_interval = row['interval']
                
                match emission_interval:
                    # Events covering multiple days are stored based on last date, hence they will always be captured
                    # But sometimes they may extend the time period of interest... that's OK. we just figure out the daily amount and add 
                    # it to the dates within the period of interest
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
                emission_end_date = row['date']
                emission_start_date = emission_end_date - (delta * number_days)
                while (emission_start_date < emission_end_date):
                    emissions_df = emissions_df.append({'Date': emission_start_date, emission_type: daily_emission}, ignore_index = True)
                    usage_df = usage_df.append({'Date': emission_start_date, emission_type: daily_usage}, ignore_index = True)
                    emission_start_date += delta
                    # print('emissions df is: ', emissions_df)
    print('emdf: ', emissions_df)
    print('usdf: ', usage_df)
    total = emissions_df.sum()
    
    # Need to convert to pandas datatime format 
    emissions_df['Date'] = emissions_df['Date'].apply(pd.to_datetime)
    usage_df['Date'] = usage_df['Date'].apply(pd.to_datetime)
    
    total_monthly_emissions = emissions_df[(emissions_df.Date.dt.month == 2) & (emissions_df.Date.dt.year == 2023)].sum()
    total_monthly_usage = usage_df[(usage_df.Date.dt.month == 2) & (usage_df.Date.dt.year == 2023)].sum()
    print('emissions df total is: ', total)
    print('emissions df total_monthly is: ', total_monthly_emissions)


    # print('col0', total_monthly.keys().tolist())
    # print('col1', total_monthly[1])
    return [total_monthly_emissions, total_monthly_usage]

def get_metrics(total_monthly_emissions, total_monthly_usage):
        # TODO should we use function above since work has already been done?          
        # just need to sum km, sum kg c02, sum MJ and sum kWh, sum offsets
        # TODO consider do we need dataframes 
            # Calc total g co2 metric
        co2_metric = int(sum(total_monthly_emissions)/1000)
        print('sum co2: ', co2_metric)
        
        # Calc total elec
        elec_metric = total_monthly_usage['Electricity (VIC)'] 
        print('sum elec', elec_metric) 
        
        # Calc total gas
        gas_metric = total_monthly_usage['Natural Gas'] 
        print('sum gas', gas_metric)  
        
        # Calc total km travelled
        excluded_columns = ['Electricity (VIC)', 'Natural Gas', 'Offset', 'Other']
        km_metric = total_monthly_usage.drop(excluded_columns).sum() 
        print('sum km', km_metric)   

        # Calc total offsets, divide by 1000 to convert from g to kg CO2  
        offsets_metric = int(total_monthly_emissions['Offset']/(-1000))
        print('sum offsets', offsets_metric)  

        metrics_dict = {
            'co2': co2_metric,
            'elec': elec_metric,
            'gas': gas_metric,
            'km': km_metric,
            'offsets': offsets_metric
            }
        return metrics_dict
    
