create table if not exists wind(
    id integer unique,
    auto boolean,
    ventilation integer,
    circulation integer,
    act_time time,
    deact_time time
);

create table if not exists environment(
    id integer unique,
    temperature integer,
    humidity integer
);

INSERT OR IGNORE INTO wind (id, auto, ventilation, circulation, act_time, deact_time) VALUES
(1, 0, 50, 50, time('00:00'), time('00:00'));

INSERT OR IGNORE INTO environment(id, temperature, humidity) VALUES
(1,0,0);