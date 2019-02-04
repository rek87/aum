const url = require('url');
var express = require('express');
var merge = require('merge')
const fs = require('fs')

const storeData = (data, path) => {
    try {
        fs.writeFileSync(path, JSON.stringify(data))
    } catch (err) {
        console.error(err)
    }
}

function hasProp(obj, prop) {
    return Object.prototype.hasOwnProperty.call(obj, prop);
}

// Load data
var data = require('../data/justemenemoi.json');
var girls = require('../data/charme.json');

var app = express();
// Image folder is out of tree
app.use('/images', express.static(__dirname + '../../data/pics/'));

var ids = {}
app.get('/', function (request, response) {
    // Parse URL to get items to hide
    ids = merge(ids, url.parse(request.url, true).query);

    response.writeHead(200, { "Content-Type": "text/html" });
    response.write('<html><head><title>Display results!</title> \
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\
                </head><body>');

    response.write('<form action="/" method="get">');
    response.write('<table style="border: 1px solid black; width: 50%;">');
    for (var i in data) {
        // remove description and shopping list for hidden profiles
        if (hasProp(ids, i))
            continue;
        if (data[i]['desc'].length === 0)
            continue;

        response.write('<tr>');
        response.write(`<td><a href="${data[i]['profile']}">\
                        <img src="/images/${data[i]['img']}"</a></td>`);

        // Name with check box to hide
        response.write('<td style="border: 1px solid black;">');
        response.write(data[i]['name'])
        response.write(`<br><input type="checkbox" name="${i}">Hide me!`)
        response.write('</td>');

        var attrs = ['city', 'age', 'desc', 'shop']
        for (var k in attrs) {
            response.write('<td style="border: 1px solid black;">');
            // Esiste un mdo piu intelligente ??
            response.write(data[i][attrs[k]])
            response.write('</td>');
        }
        response.write('</tr>');
    }
    response.write('</table>');
    response.write('<input type="submit" value="Hide selected">');
    response.write('</form>');
    response.write('<form action="/store" method="get"><input type="submit" value="Confirm removal"></form>');
    response.write('</body></html>');
    response.end();
});

app.get('/store', function (request, response) {
    response.writeHead(200, { "Content-Type": "text/html" });
    response.write('<html><head><title>Display results!</title> \
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\
                </head><body>');

    // Get IDs has been confirmed to be removed
    const to_remove = url.parse(request.url, true).query;

    response.write('<form action="/store" method="get">');
    response.write('<table style="border: 1px solid black; width: 100%;">');
    for (var i in ids) {
        if (hasProp(to_remove, i)) {
            data[i]['desc'] = "";
            data[i]['shop'] = "";
        }
        response.write('<tr>');
        response.write(`<td><a href="${data[i]['profile']}">\
                        <img src="/images/${data[i]['img']}"</a></td>`);

        response.write('<td style="border: 1px solid black;">');
        response.write(data[i]['name'])
        response.write(`<br><input type="checkbox" name="${i}" checked>Remove me!`)
        response.write('</td>');

        var attrs = ['city', 'age', 'desc', 'shop']
        for (var k in attrs) {
            response.write('<td style="border: 1px solid black;">');
            // Esiste un mdo piu intelligente ??
            response.write(data[i][attrs[k]])
            response.write('</td>');
        }
        response.write('</tr>');
    }
    response.write('</table>');
    response.write('<input type="submit" value="Remove">');
    response.write('</form>');
    response.write('</body></html>');
    response.end();

    // Write back file if something has been removed
    if (Object.keys(to_remove).length !== 0)
        storeData(data, '../data/justemenemoi.json');
});

app.get('/girls', function (request, response) {
    response.writeHead(200, { "Content-Type": "text/html" });
    response.write('<html><head><title>Charmed girls</title> \
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\
                </head><body>');

    response.write('<table style="border: 1px solid black; width: 100%;">');
    for (var i in girls) {
        response.write('<tr>');
        response.write(`<td><a href="${girls[i]['profile']}">\
                        <img src="/images/${girls[i]['img']}"</a></td>`);

        // Name with check box to hide
        response.write('<td style="border: 1px solid black;">');
        response.write(girls[i]['name'] + '<br><br>')
        response.write(girls[i]['city'] + '<br><br>')
        response.write(girls[i]['age'] + '<br><br>')
        response.write(girls[i]['charmed'])
        response.write('</td>');

        response.write('<td style="border: 1px solid black; width: 40%;">' + girls[i]['desc'] + '</td>');
        response.write('<td style="border: 1px solid black; width: 40%;">' + girls[i]['shop'] + '</td>');
        response.write('</tr>');
    }
    response.write('</table>');
    response.write('</body></html>');
    response.end();
});

app.listen(3000);

