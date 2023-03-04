from db import sql_select_one, sql_select_all, sql_write
import datetime 
import pandas as pd

def get_all_emissions():
    emissions = sql_select_all(f"SELECT * FROM emissions;") 
    emissions_list = []
    for event in emissions:
        emissions_list.append(event)
    return emissions


# Calculates the total co2 emissions from all sources, for a given start date and end date
def emissions_accumulator(start_date, end_date, user_id):
    delta = datetime.timedelta(days=1)
    df_cols = ['Date', 'Electricity', 'Gas', 'Car', 'Motorbike', 'Train', 'Bus', 'Plane', 'Other', 'Offsets']
    emissions_df = pd.DataFrame(columns=df_cols)

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
                elif emission_type == 'Offset' or emission_type == 'Other':
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
                    case "MONTHLY":
                        number_days = int(365/12)
                        daily_emission = emission_amount / (365 / 12)
                    case "DAILY":
                        number_days = 1
                        daily_emission = emission_amount
                emission_end_date = row['date']
                emission_start_date = emission_end_date - (delta * number_days)
                while (emission_start_date < emission_end_date):
                    emissions_df = emissions_df.append({'Date': emission_start_date, emission_type: daily_emission}, ignore_index = True)
                    emission_start_date += delta
                    # print('emissions df is: ', emissions_df)
    print(emissions_df)
    total = emissions_df.sum()
    # Need to convert to pandas datatime format 
    emissions_df['Date'] = emissions_df['Date'].apply(pd.to_datetime)
    total_monthly = emissions_df[(emissions_df.Date.dt.month == 2) & (emissions_df.Date.dt.year == 2023)].sum()
    print('emissions df total is: ', total)
    print('emissions df total_monthly is: ', total_monthly)
    # print('col0', total_monthly.keys().tolist())
    # print('col1', total_monthly[1])
    print(type(total_monthly))
    return total_monthly
                    
