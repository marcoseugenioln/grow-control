
create table if not exists photoperiod(
    id INTEGER PRIMARY KEY,
    name text(50)
);

create table if not exists training_type(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name INTEGER NOT NULL,
    description  INTEGER NOT NULL
);

create table if not exists plant(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planting_date DATE,
    photoperiod INTEGER,
);

create table if not exists training(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    training_type_id  INTEGER NOT NULL,
    trainig_date DATE NOT NULL
);


create table if not exists watering(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    watering_datetime DATETIME NOT NULL,
    mililiter INTEGER NOT NULL
);

create table if not exists feeding(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    feeding_date DATE NOT NULL,
    dose INTEGER NOT NULL,
    concentration INTEGER NOT NULL,
    nitrogen INTEGER NOT NULL,
    phosphorus INTEGER NOT NULL,
    potassium INTEGER NOT NULL
);

