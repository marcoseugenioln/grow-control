
create table if not exists photoperiod(
    id INTEGER PRIMARY KEY,
    name text(50),
    description TEXT(300) NOT NULL
);

create table if not exists training_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text(50) NOT NULL,
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
    mililiter INTEGER NOT NULL
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

