
create table if not exists photoperiod(
    id INTEGER PRIMARY KEY,
    name text(50) UNIQUE,
    description TEXT(500) NOT NULL
);

create table if not exists gender(
    id INTEGER PRIMARY KEY,
    name text(50) UNIQUE,
    description TEXT(500) NOT NULL
);

create table if not exists training_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text(50) UNIQUE,
    description TEXT(500) NOT NULL
);

create table if not exists damage_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text(50) UNIQUE,
    description TEXT(500) NOT NULL
);

create table if not exists plant(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT(50) NOT NULL,
    date DATE NOT NULL,
    alive BOOLEAN DEFAULT(1),
    harvested BOOLEAN DEFAULT(0),
    photoperiod_id INTEGER NOT NULL,
    gender_id INTEGER NOT NULL,
    FOREIGN KEY (photoperiod_id) REFERENCES photoperiod(id)
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
    width INTEGER DEFAULT(0),
    height INTEGER DEFAULT(0),
    radius INTEGER DEFAULT(0),
    depth INTEGER DEFAULT(0),
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

create table if not exists damage(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    date DATE NOT NULL,
    damage_type_id INTEGER NOT NULL,
    FOREIGN KEY (damage_type_id) REFERENCES damage_type(id),
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

create table if not exists harvest(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    date DATE NOT NULL,
    yield INTEGER NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

INSERT OR IGNORE INTO gender (name, description) VALUES
('male', ''),
('female', ''),
('hermaphrodite', ''),
('unknown', '');

INSERT OR IGNORE INTO photoperiod (name, description) VALUES
('germination', ''),
('seedling', ''),
('vegetative', ''),
('flowering', ''),
('autoflower', '');

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
