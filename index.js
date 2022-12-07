
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
var PORT = 443
app.listen(PORT, () => {
    console.log("Server is Running. Listening to port " + PORT)
})