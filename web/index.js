const http = require('http');
var express = require('express');

// Load data
var data = require('../data/justemenemoi.json');

var app = express();
// app.use(express.static('public'));
// Image folder is out of tree
app.use('/images', express.static(__dirname + '../../data/pics/'));

app.get('/', function (request, response) {
        response.writeHead(200, {"Content-Type": "text/html"});
        response.write('<html><head><title>Display results!</title> \
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\
                </head><body>');

        response.write('<table width="100%" style="border: 1px solid black;">');
        for (var i in data) {
                if (data[i]['desc'].length === 0)
                        continue

                response.write('<tr>');
                response.write(`<td><a href="${data[i]['profile']}">\
                        <img src="/images/${data[i]['img']}"</a></td>`);

                var attrs = ['name', 'city', 'age', 'desc', 'shop']
                for (var k in attrs) {
                        response.write('<td style="border: 1px solid black;">');
                        // Esiste un mdo piu intelligente ??
                        response.write(data[i][attrs[k]])
                        response.write('</td>');
                }
                response.write('</tr>');
        }
        response.write('</table>');
        response.write('</body></html>');
        response.end();
        });


app.listen(3000);

