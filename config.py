# Emission rates with category info 
emission_rates_by_category = {
    'Energy': 
        {'Electricity (VIC)': 1600,
        'Natural Gas': 69},
    'Transport': 
        {'Bus': 22,
        'Car - Plug In Hybrid': 51,
        'Car - Battery Electric': 0,
        'Car - Typical Petrol': 164,
        'Car - Typical Diesel': 176,
        'Car - Micro': 116,
        'Car - Light': 132,
        'Car - Medium': 137,
        'Car - Large': 198,
        'Car - People Mover': 212,
        'Car - Small/Medium SUV': 156,
        'Car - Large SUV': 195,
        'Motorbike': 110,
        'Plane': 158,
        'Train': 22},
    'Offset':
        {'Offset': -1}, # Offsets are treated as negative emissions
    'Other': 
        {'Other': 1}
}

# Emission rates without category info 
emission_rates = {}
for emission_rate in emission_rates_by_category.values():
    emission_rates.update(emission_rate)

