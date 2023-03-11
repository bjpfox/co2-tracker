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

-- The password of 'password' has this hash: 
INSERT INTO users (name, email, password_hash, state) VALUES ('John', 'john@hello.com', 'pbkdf2:sha256:260000$Ddi8dkwadOEMA5qt$b623c59e726528417d9fa762b71d2c834b3369996fcc30290fc0d432c390b5ae', 'VIC');
INSERT INTO users (name, email, password_hash, state) VALUES ('Alice', 'alice@acme.com', 'pbkdf2:sha256:260000$Ddi8dkwadOEMA5qt$b623c59e726528417d9fa762b71d2c834b3369996fcc30290fc0d432c390b5ae', 'VIC');
INSERT INTO users (name, email, password_hash, state) VALUES ('Martin Smith', 'martin@hello.com', 'pbkdf2:sha256:260000$Ddi8dkwadOEMA5qt$b623c59e726528417d9fa762b71d2c834b3369996fcc30290fc0d432c390b5ae', 'QLD');
INSERT INTO users (name, email, password_hash, state) VALUES ('Jude', 'jude@hello.com', 'pbkdf2:sha256:260000$Ddi8dkwadOEMA5qt$b623c59e726528417d9fa762b71d2c834b3369996fcc30290fc0d432c390b5ae', 'NSW');
INSERT INTO users (name, email, password_hash, state) VALUES ('Mario', 'mario@hello.com', 'pbkdf2:sha256:260000$Ddi8dkwadOEMA5qt$b623c59e726528417d9fa762b71d2c834b3369996fcc30290fc0d432c390b5ae', 'TAS');
INSERT INTO users (name, email, password_hash, state) VALUES ('Cam Jones', 'cameron@hello.com', 'pbkdf2:sha256:260000$Ddi8dkwadOEMA5qt$b623c59e726528417d9fa762b71d2c834b3369996fcc30290fc0d432c390b5ae', 'NSW');

INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-07', 'QUARTERLY', '3400', 'Natural Gas', 'Gas Bill');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-07', 'MONTHLY', '226', 'Electricity (VIC)', 'Electricity Bill');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-02', 'DAILY', '50', 'Car - Medium', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-03', 'DAILY', '50', 'Car - Medium', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-04', 'DAILY', '50', 'Car - Medium', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-05', 'DAILY', '50', 'Car - Medium', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('1', '2023-02-06', 'DAILY', '400', 'Plane', 'Trip to NSW');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('2', '2023-02-02', 'QUARTERLY', '4400', 'Natural Gas', 'Gas Bill');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('2', '2023-02-02', 'MONTHLY', '446', 'Electricity (VIC)', 'Electricity Bill');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('2', '2023-02-02', 'DAILY', '100', 'Car - Micro', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('2', '2023-02-04', 'DAILY', '100', 'Car - Micro', 'Commute to office');
INSERT INTO emissions(user_id, date, interval, amount, type, description) VALUES ('2', '2023-02-05', 'DAILY', '100', 'Car - Micro', 'Commute to office');