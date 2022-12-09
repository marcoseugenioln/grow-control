
// Importing express module
const express = require("express")
const sqlite3 = require("sqlite3");
const bodyParser = require("url");
const app     = express();

// Setup App
app.use(express.static(__dirname + '/'));

// CONSTANTS
const DATABASE = "database.db"
var db;

// Server setup
var PORT = 3000
app.listen(PORT, () => {
    console.log("Server is Running listening to port: " + PORT)
})

  
// Handling GET /hello request
app.get("/hello", (req, res, next) => {
    res.send("This is the hello response");
})

// Handling GET /insert request
app.get("/insert", (req, res, next) => {

    var soil_umidity_1 = req.query.soil_umidity_1;
    var soil_umidity_2 = req.query.soil_umidity_2;
    var soil_umidity_3 = req.query.soil_umidity_3;
    var soil_umidity_4 = req.query.soil_umidity_4;
    var air_umidity    = req.query.air_umidity;
    var temperature    = req.query.temperature;
    var date           = req.query.date;

    var response = 
    `soil_umidity_1=${soil_umidity_1} 
    soil_umidity_2=${soil_umidity_2} 
    soil_umidity_3=${soil_umidity_3} 
    soil_umidity_4=${soil_umidity_4} 
    soil_umidity_4=${soil_umidity_4} 
    air_umidity=${air_umidity} 
    temperature=${temperature} 
    date=${date} `
    
    res.send(response);

    var db = new sqlite3.Database(DATABASE);

    db.run(
        `INSERT INTO Grow(
            soil_umidity_1, soil_umidity_2, soil_umidity_3, soil_umidity_4, air_umidity, temperature, date
            ) 
            VALUES (
                ${soil_umidity_1}, ${soil_umidity_2}, ${soil_umidity_3}, ${soil_umidity_4}, ${air_umidity}, ${temperature}, ${date}
                )`)
})

// Handling GET /run-query request
app.get("/run-query", (req, res, next) => {

    var script = req.query.script;
    var db = new sqlite3.Database(DATABASE);

    res.send("running: " + script);
    db.run(script);

})

// Handling GET /create-database request
app.get("/create-database", (req, res, next) => {

    res.send("Creating database.");

    new sqlite3.Database(DATABASE, sqlite3.OPEN_READWRITE, (err) => {
        if (err && err.code == "SQLITE_CANTOPEN") {
            createDatabase();
            return;
            } else if (err) {
                console.log("Getting error " + err);
                exit(1);
        }
        runQueries(db);
    });
})

function createDatabase() {

    var newdb = new sqlite3.Database(DATABASE, (err) => {
        
        if (err) {
            console.log("Getting error " + err);
            exit(1);
        }

        //createTables(newdb);
    });
}


