-- To initiatilise we run
-- createdb co2_tracker 
-- psql -d co2_tracker < schema.sql
-- psql -d co2_tracker < seed.sql

DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS emissions CASCADE;
DROP TABLE IF EXISTS emission_rates_transport CASCADE;
DROP TABLE IF EXISTS emission_rates_energy CASCADE;


-- Lists all of the users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,-- id 
    name VARCHAR(320),
    email VARCHAR(320), 
    state VARCHAR(3) -- NSW, VIC, TAS, etc - TODO - make this load as default electricity rate?
); 


-- Contains the emissions rate data for transport 
CREATE TABLE emission_rates_transport (
    id SERIAL PRIMARY KEY, 
    name VARCHAR(100), -- e.g. Train, Plane, Bus, ec
    rate INT  -- g CO2 equivalent per km  
);

-- Contains the emissions rate data for energy 
CREATE TABLE emission_rates_energy (
    id SERIAL PRIMARY KEY, 
    name VARCHAR(100), -- e.g. Electricity, Natural Gas 
    rate INT  -- g CO2 equivalent per kWh (Elec) or per MJ (gas)
);

CREATE TABLE emissions (
    id SERIAL PRIMARY KEY, -- list id
    user_id INT,
        CONSTRAINT fk_emissions_users
        FOREIGN KEY (user_id)
        REFERENCES users(id), 
    date DATE, -- where event spans more than 1 day, this is taken to be the last day 
    interval VARCHAR(10), -- OPTIONS: DAILY, WEEKLY, MONTHLY, QUARTERLY
    amount INT, -- g_c02 equivalent for the emissions event 
    -- amount_daily INT, -- g_c02 equivalent for a single day event 
    -- amount_weekly INT, -- g_c02 equivalent total across a week (e.g. a weeks worth of commuting - TODO add later)
    -- amount_monthly INT, -- g_c02 equivalent total for a month (e.g. elec bill)
    -- amount_quarterly INT, -- g_c02 equivalent total for a quarter (e.g. gas bill)
    type VARCHAR(100), -- e.g. car, plane, train, electricity, natural gas
    description VARCHAR(300) -- e.g. Interstate trip to NSW
    -- TODO add derived column for daily emission derived? Or just use python to calculate this 
);


