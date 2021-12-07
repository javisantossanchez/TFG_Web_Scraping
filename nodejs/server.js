'use strict';
var http = require('http');
const express = require('express');
const path = require('path');
// Constants
const PORT = 8080;
const HOST = '0.0.0.0';

// App
const app = express();
app.use(express.static(__dirname));
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname+'/index.html'));
});

app.get('/zapasnike', (req, res) => {
    
    var MongoClient = require('mongodb').MongoClient;
    var url = "mongodb://root:example@mongo:27017/";
    console.log(req.body);
    MongoClient.connect(url, function(err, db) {
    if (err) throw err;
    var dbo = db.db("nike");
    dbo.collection("zapas_nike").find({}).toArray(function(err, result) {
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
    var query = {"Nombre": $all}
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
