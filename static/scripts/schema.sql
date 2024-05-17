create table if not exists wind(
    id integer unique,
    auto boolean,
    ventilation integer,
    circulation integer,
    act_time time,
    deact_time time
);

INSERT OR IGNORE INTO wind (id, auto, ventilation, circulation, act_time, deact_time) VALUES
(1, 0, 50, 50, time('00:00'), time('00:00'));