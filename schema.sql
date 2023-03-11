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
    password_hash TEXT,
    state VARCHAR(3) 
); 


CREATE TABLE emissions (
    id SERIAL PRIMARY KEY, -- list id
    user_id INT,
        CONSTRAINT fk_emissions_users
        FOREIGN KEY (user_id)
        REFERENCES users(id), 
    date DATE, -- where event spans more than 1 day, this is taken to be the last day 
    interval VARCHAR(10), -- OPTIONS: DAILY, WEEKLY, MONTHLY, QUARTERLY
    amount INT, -- stored in the units corresponding to the event type (travel = km, elec = kWh, other = g co2, etc) 
    type VARCHAR(100), -- e.g. car, plane, train, electricity, natural gas
    description VARCHAR(300) -- e.g. Interstate trip to NSW
);


