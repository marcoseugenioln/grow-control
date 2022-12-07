
// Importing express module
const express = require("express")
const app = express()
  
// Handling GET / request
app.use(express.static(__dirname + '/')) 
  
// Handling GET /hello request
app.get("/hello", (req, res, next) => {
    res.send("This is the hello response");
})

// Server setup
app.listen(80, () => {
    console.log("Server is Running")
})