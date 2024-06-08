
create table if not exists photoperiod(
    id INTEGER PRIMARY KEY,
    name text(50) UNIQUE,
    description TEXT(300) NOT NULL
);

create table if not exists training_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text(50) UNIQUE,
    description TEXT(300) NOT NULL
);

create table if not exists plant(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planting_date DATE,
    photoperiod_id INTEGER,
    FOREIGN KEY (photoperiod_id) REFERENCES photoperiod(id)
);

create table if not exists training(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    training_type_id  INTEGER NOT NULL,
    trainig_date DATE NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

create table if not exists watering(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    watering_datetime DATETIME NOT NULL,
    mililiter INTEGER NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

create table if not exists feeding(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    feeding_date DATE NOT NULL,
    dose INTEGER NOT NULL,
    concentration INTEGER NOT NULL,
    nitrogen INTEGER NOT NULL,
    phosphorus INTEGER NOT NULL,
    potassium INTEGER NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

create table if not exists transplanting(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    transplanting_date DATE NOT NULL,
    dimensions text(100) NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(id)
);

INSERT OR IGNORE INTO photoperiod (name, description) VALUES
('seedling', 
'Initial growth period. The plant builds up structural integrity, stem and roots and may last 1-3 weeks.\n
During the early stages of growth, the plant will require a lot of nitrogen .\n
Early leaves will begin the photosynthesis process, absorbing sunlight and furthering the plant’s growth.'),

('vegetative', 
'Growth period. The plant build more foliage and grows in size. 
Under a 18/6 lights schedule cycle, plants can stay in the vegetative stage “indefinitely” but usually 8-15 weeks.\n
Training is allowed. Plants are more forgiving as they have time to recover.'),

('flowering', ''),

('autoflower', 
'Vegetative growth is limited to 3–4 weeks, regardless of light schedule.\n
Due to limited vegetative growth, plants are usually much smaller.\n
Intensive training, such as cutting and topping, is not recommended.\n
No control over growing and flowering stages.\n
Cannot be used for breeding.\n
Lower average yields than photoperiods.\n');