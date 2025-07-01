
create table if not exists photoperiod(
    id INTEGER PRIMARY KEY,
    name text(50) UNIQUE,
    description TEXT(500)
);

create table if not exists gender(
    id INTEGER PRIMARY KEY,
    name text(50) UNIQUE,
    description TEXT(500)
);

create table if not exists intensity(
    id INTEGER PRIMARY KEY,
    name text(50) UNIQUE,
    description TEXT(500)
);

create table if not exists training_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text(50) UNIQUE,
    description TEXT(500)
);

create table if not exists damage_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text(50) UNIQUE,
    description TEXT(500)
);

create table if not exists sensor_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text(50) UNIQUE,
    description TEXT(500)
);

create table if not exists effector_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text(50) UNIQUE,
    description TEXT(500)
);

create table if not exists user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
	email TEXT(300) UNIQUE,
	password TEXT(64),
	is_admin BOOLEAN DEFAULT (0)
);

create table if not exists grow(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT(50) NOT NULL,
    lenght FLOAT,
    width FLOAT,
    height FLOAT,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

create table if not exists effector(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grow_id INTEGER NOT NULL,
    effector_type_id INTEGER NOT NULL,
    name TEXT(50) NOT NULL,
    ip TEXT(20),
    normal_on BOOLEAN DEFAULT(0),
    power_on BOOLEAN DEFAULT(0),
    scheduled BOOLEAN DEFAULT(0),
    on_time TIME,
    off_time TIME,
    bounded BOOLEAN DEFAULT(0),
    bounded_sensor_id INTEGER,
    threshold FLOAT,
    FOREIGN KEY (effector_type_id) REFERENCES effector_type(id),
    FOREIGN KEY (bounded_sensor_id) REFERENCES sensor(id),
    FOREIGN KEY (grow_id) REFERENCES grow(id) ON DELETE CASCADE
);

create table if not exists sensor(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grow_id INTEGER NOT NULL,
    ip TEXT(20),
    name TEXT(50) NOT NULL,
    sensor_type_id INTEGER NOT NULL,
    last_value FLOAT DEFAULT(0),
    FOREIGN KEY (grow_id) REFERENCES grow(id) ON DELETE CASCADE,
    FOREIGN KEY (sensor_type_id) REFERENCES sensor_type(id)
);

create table if not exists sensor_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    value FLOAT NOT NULL,
    datetime  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensor(id)
);

create table if not exists plant(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grow_id INTEGER NOT NULL,
    name TEXT(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    photoperiod_id INTEGER NOT NULL,
    gender_id INTEGER NOT NULL,
    harvested BOOLEAN DEFAULT(0),
    yield FLOAT DEFAULT(0),
    FOREIGN KEY (grow_id) REFERENCES grow(id) ON DELETE CASCADE,
    FOREIGN KEY (photoperiod_id) REFERENCES photoperiod(id),
    FOREIGN KEY (gender_id) REFERENCES gender(id)
);

create table if not exists training(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    date DATE NOT NULL,
    training_type_id  INTEGER NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(id)
    FOREIGN KEY (training_type_id) REFERENCES training_type(id)
);

create table if not exists watering(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    date DATE NOT NULL,
    mililiter INTEGER NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

create table if not exists feeding(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    date DATE NOT NULL,
    dosage INTEGER NOT NULL,
    nitrogen INTEGER NOT NULL,
    phosphorus INTEGER NOT NULL,
    potassium INTEGER NOT NULL,
    concentration INTEGER NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

create table if not exists transplanting(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    date DATE NOT NULL,
    lenght FLOAT DEFAULT(0),
    width FLOAT DEFAULT(0),
    height FLOAT DEFAULT(0),
    radius FLOAT DEFAULT(0),
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

create table if not exists damage(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    date DATE NOT NULL,
    damage_type_id INTEGER NOT NULL,
    intensity_id INTEGER NOT NULL,
    FOREIGN KEY (damage_type_id) REFERENCES damage_type(id),
    FOREIGN KEY (intensity_id) REFERENCES intensity(id),
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

CREATE TRIGGER IF NOT EXISTS last_sensor_data_value
AFTER INSERT ON sensor_data
FOR EACH ROW
BEGIN
    UPDATE sensor set last_value = NEW.value WHERE id = NEW.sensor_id;
END;

INSERT OR IGNORE INTO gender (name, description) VALUES
('Male', ''),
('Female', ''),
('Hermaphrodite', ''),
('Unknown', '');

INSERT OR IGNORE INTO photoperiod (name, description) VALUES
('Germination', ''),
('Seedling', ''),
('Vegetative', ''),
('Flowering', ''),
('Autoflower', '');

INSERT OR IGNORE INTO training_type (name, description) VALUES
('Low Stress Training', ''),
('High Stress Training', ''),
('Apical Pruning', ''),
('Lollipop Pruning', ''),
('FIM Pruning', '');

INSERT OR IGNORE INTO damage_type (name, description) VALUES
('Physical Damage', ''),
('Light Burning', ''),
('Wind Burning', ''),
('Overwatering', ''),
('Overfeeding', ''),
('Low watering', ''),
('Low Light', ''),
('Mold', ''),
('Parasites', '');

INSERT OR IGNORE INTO intensity (name, description) VALUES
('Very Low', ''),
('Low', ''),
('Medium', ''),
('High', ''),
('Very High', '');

INSERT OR IGNORE INTO sensor_type (name, description) VALUES
('Air Temperature', ''),
('Air Humidity', ''),
('Soil Temperature', ''),
('Soil Humidity', ''),
('Soil HP', ''),
('Water HP', ''),
('PPFD', '');

INSERT OR IGNORE INTO effector_type (name, description) VALUES
('Fan', ''),
('Lights', ''),
('Water Supplier', ''),
('Exhauster', ''),
('Blower', ''),
('Humidifier', ''),
('Dehumidifier', '');

INSERT OR IGNORE INTO user (email, password, is_admin) VALUES
('root@root.com', 'root', 1),
('user@user.com', 'user', 0);
