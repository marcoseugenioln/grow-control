-- =========================
-- Tabelas de referência
-- =========================

CREATE TABLE IF NOT EXISTS photoperiod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    description VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS gender (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    description VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS intensity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    description VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS training_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    description VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS damage_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    description VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS sensor_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    description VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS effector_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    description VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(300) UNIQUE,
    password VARCHAR(64),
    is_admin TINYINT(1) DEFAULT 0
);

-- =========================
-- Tabelas principais
-- =========================

CREATE TABLE IF NOT EXISTS grow (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    lenght FLOAT,
    width FLOAT,
    height FLOAT,
    CONSTRAINT fk_grow_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sensor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grow_id INT NOT NULL,
    ip VARCHAR(20),
    name VARCHAR(50) NOT NULL,
    sensor_type_id INT NOT NULL,
    last_value FLOAT DEFAULT 0,
    CONSTRAINT fk_sensor_grow FOREIGN KEY (grow_id) REFERENCES grow(id) ON DELETE CASCADE,
    CONSTRAINT fk_sensor_type FOREIGN KEY (sensor_type_id) REFERENCES sensor_type(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS effector (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grow_id INT NOT NULL,
    effector_type_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    ip VARCHAR(20),
    normal_on TINYINT(1) DEFAULT 0,
    power_on TINYINT(1) DEFAULT 0,
    scheduled TINYINT(1) DEFAULT 0,
    on_time TIME,
    off_time TIME,
    bounded TINYINT(1) DEFAULT 0,
    bounded_sensor_id INT,
    threshold FLOAT,
    CONSTRAINT fk_effector_type FOREIGN KEY (effector_type_id) REFERENCES effector_type(id),
    CONSTRAINT fk_effector_sensor FOREIGN KEY (bounded_sensor_id) REFERENCES sensor(id),
    CONSTRAINT fk_effector_grow FOREIGN KEY (grow_id) REFERENCES grow(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    value FLOAT NOT NULL,
    datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sensordata_sensor FOREIGN KEY (sensor_id) REFERENCES sensor(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS plant (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grow_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    photoperiod_id INT NOT NULL,
    gender_id INT NOT NULL,
    harvested TINYINT(1) DEFAULT 0,
    yield FLOAT DEFAULT 0,
    CONSTRAINT fk_plant_grow FOREIGN KEY (grow_id) REFERENCES grow(id) ON DELETE CASCADE,
    CONSTRAINT fk_plant_photoperiod FOREIGN KEY (photoperiod_id) REFERENCES photoperiod(id),
    CONSTRAINT fk_plant_gender FOREIGN KEY (gender_id) REFERENCES gender(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS training (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plant_id INT NOT NULL,
    date DATE NOT NULL,
    training_type_id INT NOT NULL,
    CONSTRAINT fk_training_plant FOREIGN KEY (plant_id) REFERENCES plant(id),
    CONSTRAINT fk_training_type FOREIGN KEY (training_type_id) REFERENCES training_type(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS watering (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plant_id INT NOT NULL,
    date DATE NOT NULL,
    mililiter INT NOT NULL,
    CONSTRAINT fk_watering_plant FOREIGN KEY (plant_id) REFERENCES plant(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS feeding (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plant_id INT NOT NULL,
    date DATE NOT NULL,
    dosage INT NOT NULL,
    nitrogen INT NOT NULL,
    phosphorus INT NOT NULL,
    potassium INT NOT NULL,
    concentration INT NOT NULL,
    CONSTRAINT fk_feeding_plant FOREIGN KEY (plant_id) REFERENCES plant(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS transplanting (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plant_id INT NOT NULL,
    date DATE NOT NULL,
    lenght FLOAT DEFAULT 0,
    width FLOAT DEFAULT 0,
    height FLOAT DEFAULT 0,
    radius FLOAT DEFAULT 0,
    CONSTRAINT fk_transplanting_plant FOREIGN KEY (plant_id) REFERENCES plant(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS damage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plant_id INT NOT NULL,
    date DATE NOT NULL,
    damage_type_id INT NOT NULL,
    intensity_id INT NOT NULL,
    CONSTRAINT fk_damage_plant FOREIGN KEY (plant_id) REFERENCES plant(id),
    CONSTRAINT fk_damage_type FOREIGN KEY (damage_type_id) REFERENCES damage_type(id),
    CONSTRAINT fk_damage_intensity FOREIGN KEY (intensity_id) REFERENCES intensity(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- Trigger
-- =========================

CREATE TRIGGER last_sensor_data_value
AFTER INSERT ON sensor_data
FOR EACH ROW
BEGIN
    UPDATE sensor
    SET last_value = NEW.value
    WHERE id = NEW.sensor_id;

    DELETE FROM sensor_data
    WHERE sensor_id = NEW.sensor_id
      AND datetime < (NOW() - INTERVAL 1 DAY);
END;

-- =========================
-- Inserts iniciais
-- =========================

INSERT IGNORE INTO gender (name, description) VALUES
('Male', ''),
('Female', ''),
('Hermaphrodite', ''),
('Unknown', '');

INSERT IGNORE INTO photoperiod (name, description) VALUES
('Germination', ''),
('Seedling', ''),
('Vegetative', ''),
('Flowering', ''),
('Autoflower', '');

INSERT IGNORE INTO training_type (name, description) VALUES
('Low Stress Training', ''),
('High Stress Training', ''),
('Apical Pruning', ''),
('Lollipop Pruning', ''),
('FIM Pruning', '');

INSERT IGNORE INTO damage_type (name, description) VALUES
('Physical Damage', ''),
('Light Burning', ''),
('Wind Burning', ''),
('Overwatering', ''),
('Overfeeding', ''),
('Low watering', ''),
('Low Light', ''),
('Mold', ''),
('Parasites', '');

INSERT IGNORE INTO intensity (name, description) VALUES
('Very Low', ''),
('Low', ''),
('Medium', ''),
('High', ''),
('Very High', '');

INSERT IGNORE INTO sensor_type (name, description) VALUES
('Air Temperature', ''),
('Air Humidity', ''),
('Soil Temperature', ''),
('Soil Humidity', ''),
('Soil HP', ''),
('Water HP', ''),
('PPFD', '');

INSERT IGNORE INTO effector_type (name, description) VALUES
('Fan', ''),
('Lights', ''),
('Water Supplier', ''),
('Exhauster', ''),
('Blower', ''),
('Humidifier', ''),
('Dehumidifier', '');

INSERT IGNORE INTO user (email, password, is_admin) VALUES
('root@root.com', 'root', 1),
('user@user.com', 'user', 0);
