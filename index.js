
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

    var su_1 = req.query.su_1;
    var su_2 = req.query.su_2;
    var su_3 = req.query.su_3;
    var su_4 = req.query.su_4;
    var au    = req.query.au;
    var t    = req.query.t;
    var response = 
    `su_1=${su_1} 
    su_2=${su_2} 
    su_3=${su_3} 
    su_4=${su_4} 
    su_4=${su_4} 
    au=${au} 
    t=${t}`

    console.log(response);
    
    res.send(response);

    var db = new sqlite3.Database(DATABASE);

    db.run(
        `INSERT INTO Grow(
            su_1, su_2, su_3, su_4, au, t, date
        ) 
        VALUES (
            ${su_1}, ${su_2}, ${su_3}, ${su_4}, ${au}, ${t}, ${date}
        )`
    )
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


