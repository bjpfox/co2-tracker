-- Deletes data in table but not table itself
TRUNCATE TABLE users CASCADE;
TRUNCATE TABLE emissions CASCADE;
TRUNCATE TABLE emission_rates_transport CASCADE;
TRUNCATE TABLE emission_rates_energy CASCADE;

-- Resets the auto incrementing primary keys 
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE emissions_id_seq RESTART WITH 1;
ALTER SEQUENCE emission_rates_transport_id_seq RESTART WITH 1;
ALTER SEQUENCE emission_rates_energy_id_seq RESTART WITH 1;

INSERT INTO users (name, email, state) VALUES ('John', 'john@hello.com', 'VIC');
INSERT INTO users (name, email, state) VALUES ('Mary', 'mary@hello.com', 'VIC');
INSERT INTO users (name, email, state) VALUES ('Martin Smith', 'martin@hello.com', 'QLD');
INSERT INTO users (name, email, state) VALUES ('Jude', 'jude@hello.com', 'NSW');
INSERT INTO users (name, email, state) VALUES ('Mario', 'mario@hello.com', 'TAS');
INSERT INTO users (name, email, state) VALUES ('Cam Jones', 'cameron@hello.com', 'NSW');

INSERT INTO emission_rates_transport (name, rate) VALUES ('Train', '22');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Bus', '22');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Plane', '158');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - Plug In Hybrid', '51');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - Battery Electric', '0');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - Typical Petrol', '164');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - Typical Diesel', '176');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - Micro', '116');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - Light', '132');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - Medium', '137');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - Large', '198');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - People Mover', '212');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - Small/Medium SUV', '156');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Car - Large SUV', '195');
INSERT INTO emission_rates_transport (name, rate) VALUES ('Motorbike', '110');

-- TODO add data for other states
INSERT INTO emission_rates_energy(name, rate) VALUES ('Electricity (VIC)', '1600');
INSERT INTO emission_rates_energy(name, rate) VALUES ('Natural Gas', '69');

INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-02', 'QUARTERLY', '3400', 'Natural gas', 'Gas Bill');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-02', 'MONTHLY', '226', 'Electricity (VIC)', 'Electricity Bill');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-02', 'DAILY', '50', 'Car - Medium', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-03', 'DAILY', '50', 'Car - Medium', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-04', 'DAILY', '50', 'Car - Medium', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-05', 'DAILY', '50', 'Car - Medium', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-06', 'DAILY', '4000', 'Plane', 'Trip Melb to Perth');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('2', '2023-02-02', 'QUARTERLY', '4400', 'Natural gas', 'Gas Bill');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('2', '2023-02-02', 'MONTHLY', '446', 'Electricity (VIC)', 'Electricity Bill');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('2', '2023-02-02', 'DAILY', '100', 'Car - Micro', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('2', '2023-02-04', 'DAILY', '100', 'Car - Micro', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('2', '2023-02-05', 'DAILY', '100', 'Car - Micro', 'Commute to office');