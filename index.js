
// Importing express module
const { response } = require("express");
const express = require("express")
const sqlite3 = require("sqlite3");
const bodyParser = require("url");
const app     = express();

// Setup App
app.use(express.static(__dirname + '/'));

// CONSTANTS
const DATABASE = "database.db"
var db;

Date.prototype.addHours = function(h) {
    this.setTime(this.getTime() + (h*60*60*1000));
    return this;
}

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

    var date = new Date();

    date.addHours(-3);

    var su_1 = req.query.su_1;
    var su_2 = req.query.su_2;
    var su_3 = req.query.su_3;
    var su_4 = req.query.su_4;
    var au    = req.query.au;
    var t    = req.query.t;

    var post = `su_1=${su_1} su_2=${su_2} su_3=${su_3} su_4=${su_4} su_4=${su_4} au=${au} t=${t}`

    console.log(post);

    var db = new sqlite3.Database(DATABASE);
    
    var current_date = date.toISOString().split('T')[0] + ' ' + date.toISOString().split('T')[1].split('.')[0];
    console.log(current_date);

    var query = 

    `INSERT INTO Grow(
        soil_umidity_1, soil_umidity_2, soil_umidity_3, soil_umidity_4, air_umidity, temperature, date
    ) 
    VALUES (
        ${su_1}, ${su_2}, ${su_3}, ${su_4}, ${au}, ${t}, '${current_date}'
    )`;

    console.log(query)
    db.run(query)

    if (su_1 < 40) {
        res.send('1');
    }
    else{
        res.send('0');
    }
    
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


