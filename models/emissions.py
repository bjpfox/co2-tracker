from db import select_one, select_all, write

def get_all_emissions():
    emissions = select_all(f"SELECT * FROM emissions;") 
    emissions_list = []
    for event in emissions:
        emissions_list.append(event)
    return emissions