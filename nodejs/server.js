'use strict';
var http = require('http');
const express = require('express');
const path = require('path');
// Constants
const PORT = 8080;
const HOST = '0.0.0.0';
function myFunc(res) {
    var body = document.body;
    var node = document.createElement("LI");                 // Create a <li> node
    var textnode = document.createTextNode("Water");         // Create a text node
    node.appendChild(textnode);                              // Append the text to <li>
    body.appendChild(node);     // Append <li> to <ul> with id="myList" 
  }
// App
const app = express();
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname+'/index.html'));
    console.log("Maricslkdmdskfon");
    myFunc(res);
    /*
    var MongoClient = require('mongodb').MongoClient;
    var url = "mongodb://root:example@mongo:27017/";
    console.log(req.body);
    MongoClient.connect(url, function(err, db) {
    if (err) throw err;
    var dbo = db.db("nike");
    var query = { "State": "Comprar" };
    dbo.collection("zapas_nike").find(query).toArray(function(err, result) {
        if (err) throw err;
        console.log(result);
        res.send(result)
        db.close();
    });
    });*/
});

app.get('/zapasnike', (req, res) => {
    
    var MongoClient = require('mongodb').MongoClient;
    var url = "mongodb://root:example@mongo:27017/";
    console.log(req.body);
    MongoClient.connect(url, function(err, db) {
    if (err) throw err;
    var dbo = db.db("nike");
    var query = { "State": "Comprar" };
    dbo.collection("zapas_nike").find(query).toArray(function(err, result) {
        if (err) throw err;
        console.log(result);
        res.send(result)
        db.close();
    });
    });
});

app.get('/zapasstockx', (req, res) => {
    
    var MongoClient = require('mongodb').MongoClient;
    var url = "mongodb://root:example@mongo:27017/";
    console.log(req.body);
    MongoClient.connect(url, function(err, db) {
    if (err) throw err;
    var dbo = db.db("nike");
    var query = {"Nombre":"*"}
    dbo.collection("zapas_stockx").find(query).toArray(function(err, result) {
        if (err) throw err;
        console.log(result);
        res.send(result)
        db.close();
    });
    });
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);
