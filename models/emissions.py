from db import sql_select_one, sql_select_all, sql_write

def get_all_emissions():
    emissions = sql_select_all(f"SELECT * FROM emissions;") 
    emissions_list = []
    for event in emissions:
        emissions_list.append(event)
    return emissions