from flask import Flask, render_template, request, redirect, url_for, Response
from functools import wraps
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import tweepy
import config

basePath = "/srv/http/pickapump.com/PapTwitter/"
templatePath = basePath + "templates/"

bearer_token=config.BEARER_TOKEN
access_token=config.ACCESS_KEY
access_token_secret=config.ACCESS_SECRET
consumer_key=config.COMSUMER_KEY
consumer_secret=config.CONSUMER_SECRET

currentCoords = None
middle = ''
data = None

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == config.USERNAME and password == config.PASSPHRASE

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/map', methods=['GET', 'POST'])
def mapPage():
    return render_template("map.html", title='PickAPump Map') 

@app.route('/fuel', methods=['GET', 'POST'])
@requires_auth
def index(results={}):
    global data
    global middle
    data = None
    middle = ''

    if request.method == "GET":
        try:
            #CREATE DATABASE CONNECTION DEVELOPER
            # conn = mysql.connector.connect(user='root', password='97551',
            #                             host='localhost',
            #                             database='pickapump')

            #CREATE DATABASE CONNECTION PRODUCTION
            conn = mysql.connector.connect(user=config.username, password=config.password,
                                        host='localhost',
                                        database='pickapump_app')
            print("Database Connection Made!")
            #CREATE MAGICAL CURSOR OBJECT
            cursor = conn.cursor()
            #TELL MYSQL TO USE PICKAPUMP_APP DATABASE
            cursor.execute("USE pickapump_app;")
            cursor.execute("SELECT * FROM stations;")
            data = cursor.fetchall()
            print(data)

            for entries in data:
                print(entries)
                middle = middle + "<option value=\"{}\"> {} </option> \n".format(entries[0],str(entries))

            #CLOSE CONNECTIONS
            conn.commit()
            cursor.close()  
            conn.close()


        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            conn.close()

        f = open('/srv/http/pickapump.com/PapTwitter/templates/fuelForm.html','w')
        start = """<html lang="en">
                    <head>
                        <!-- Required meta tags -->
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <link rel="icon" href="../static/favicon.ico"/>
                        <!-- Latest compiled and minified CSS -->
                        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">    </head>
                        <!-- Custom CSS -->
                        <link rel="stylesheet" href="static/styles/stylesheet.css">
                    </head>
                    <body>
                        <div class="basicFormat">
                            <form method="post" enctype="multipart/form-data">
                                <div class="mb-3">
                                <label class="form-check-label" for="station">Choose Station</label>
                                    <select class="form-check-input" name="station" id="station">"""

        finish = """                
                                    </select>
                                    </div>
                                    <div class="mb-3">
                                    <label for="petrol" class="form-label">Petrol</label>
                                    <input type="number" step="0.1"class="form-control" name="petrol" id="petrol">
                                    </div>
                                    <div class="mb-3">
                                        <label for="diesel" class="form-label">Diesel</label>
                                        <input type="number" step="0.1" class="form-control" name="diesel" id="diesel">
                                    </div>
                                    <div class="mb-3">
                                        <label for="kero" class="form-label">Kero</label>
                                        <input type="number" value="0" step="0.1" class="form-control" name="kero" id="kero">
                                    </div>
                                    <div class="mb-3">
                                    <label for="petrolplus" class="form-label">Petrol Plus</label>
                                    <input type="number" value="0" step="0.1"class="form-control" name="petrolplus" id="petrolplus">
                                    </div>
                                    <div class="mb-3">
                                        <label for="dieselplus" class="form-label">Diesel Plus</label>
                                        <input type="number" value="0" step="0.1" class="form-control" name="dieselplus" id="dieselplus">
                                    </div>
                                    <div class="mb-3 form-check">
                                    <label class="form-check-label" for="sterling">Choose Currency</label>
                                    <select class="form-check-input" name="currency" id="currency">
                                        <option value="sterling">Sterling</option>
                                        <option value="euro">Euro</option>
                                    </select>
                                    </div>
                                    <div>
                                    <button type="submit" class="btn btn-primary">Submit</button>
                                    </div>
                                </form>
                            </div>
                            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.min.js" integrity="sha384-QJHtvGhmr9XOIpI6YVutG+2QOK9T+ZnN4kzFN1RtK3zEFEIsxhlmWl5/YESvpZ13" crossorigin="anonymous"></script>
                        </body>
                    </html>"""

        all = start + middle + finish
        f.write(all)
        f.close()

        return render_template("fuelForm.html", title='PickAPump Fuel Entry') 

    results.update({"station":request.form["station"]})  
    results.update({"petrol":request.form["petrol"]})  
    results.update({"diesel":request.form["diesel"]})  
    results.update({"kero":request.form["kero"]})  
    results.update({"petrolplus":request.form["petrolplus"]})  
    results.update({"dieselplus":request.form["dieselplus"]})  
    results.update({"currency":request.form["currency"]})  

    date_added = datetime.now()

    fuel_data = {
    'idstationName': results["station"],
    'petrol': results["petrol"],
    'diesel': results["diesel"],
    'kero': results["kero"],
    'petrolplus': results["petrolplus"],
    'dieselplus': results["dieselplus"],
    'date': date_added,
    'currency': results["currency"],
    }

    try:
        #CREATE DATABASE CONNECTION DEVELOPER
        # conn = mysql.connector.connect(user='root', password='97551',
        #                             host='localhost',
        #                             database='pickapump')

        #CREATE DATABASE CONNECTION PRODUCTION
        conn = mysql.connector.connect(user=config.username, password=config.password,
                                    host='localhost',
                                    database='pickapump_app')

        #CHECK DATABASE CONNECTION
        if conn.is_connected() == True:
            print("Database Connection Made!")

            #CREATE MAGICAL CURSOR OBJECT
            cursor = conn.cursor()

            #CREATE FUEL INSERT STRING
            add_fuel = ("INSERT INTO fuel "
                        "(idstationname, petrolprice, dieselprice, keroprice, petrolplusprice, dieselplusprice, currency, dateadded) "
                        "VALUES (%(idstationName)s, %(petrol)s, %(diesel)s, %(kero)s, %(petrolplus)s, %(dieselplus)s, %(currency)s, %(date)s);")
            
            #TELL MYSQL TO USE PICKAPUMP_APP DATABASE
            cursor.execute("USE pickapump_app")
            cursor.execute(add_fuel, fuel_data)

            #CLOSE CONNECTIONS
            conn.commit()
            cursor.close()  
            conn.close()

            response = send_tweet(fuel_data)
            print(response)
        

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        conn.close()

    return redirect("https://pickapump.com")

 
@app.route('/station', methods=['GET', 'POST'])
@requires_auth
def station(results={}):
    if request.method == "GET":
        return render_template("index.html", title='PickAPump Fuel Entry')   

    results.update({"stationName":request.form["stationName"]})
    results.update({"address":request.form["address"]})  
    results.update({"town":request.form["town"]}) 
    results.update({"county":request.form["county"]})   
    results.update({"postCode":request.form["postCode"]}) 
    results.update({"country":request.form["country"]})  
    results.update({"coords":request.form["coords"]}) 
    results.update({"telephone":request.form["telephone"]}) 
    results.update({"maplink":request.form["maplink"]}) 

    station_data = {
    'stationName': results["stationName"],
    'address': results["address"],
    'town': results["town"],
    'county': results["county"],
    'postcode': results["postCode"],
    'country': results["country"],
    'coords': results["coords"],
    'telephone': results["telephone"],
    'maplink': results["maplink"],
    }
 
    try:
        #CREATE DATABASE CONNECTION DEVELOPER
        # conn = mysql.connector.connect(user='root', password='97551',
        #                             host='localhost',
        #                             database='pickapump')

        #CREATE DATABASE CONNECTION PRODUCTION
        conn = mysql.connector.connect(user=config.username, password=config.password,
                                    host='localhost',
                                    database='pickapump_app')

        #CHECK DATABASE CONNECTION
        if conn.is_connected() == True:
            print("Database Connection Made!")
            #CREATE MAGICAL CURSOR OBJECT
            cursor = conn.cursor()
            #CREATE STATION INSERT STRING
            add_station = ("INSERT INTO stations "
               "(stationName, address, town, county, postcode, country, coords, telephone, maplink) "
               "VALUES (%(stationName)s, %(address)s, %(town)s, %(county)s, %(postcode)s, %(country)s, %(coords)s, %(telephone)s, %(maplink)s);")
            #TELL MYSQL TO USE PICKAPUMP_APP DATABASE
            cursor.execute("USE pickapump_app")
            #ADD STATION DATA
            print("Adding new station")
            cursor.execute(add_station, station_data)
            print("New Station added")
            
            #CLOSE CONNECTIONS
            conn.commit()
            cursor.close()  
            conn.close()
        

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        conn.close()

    
    print(results)
    return redirect('/fuel')


def send_tweet(fuel_data):
    if fuel_data['currency'] == 'sterling':
        currency = 'p'
    elif fuel_data['currency'] == 'euro':
        currency = 'c'
    else:
        currency = ''

    station_data = {
    'idstationname': None,
    'stationName': None,
    'address': None,
    'town': None,
    'county': None,
    'postcode': None,
    'country': None,
    'coords': None,
    'telephone': None,
    'maplink': None,
    }
    
    try:
        #CREATE DATABASE CONNECTION DEVELOPER
        # conn = mysql.connector.connect(user='root', password='97551',
        #                             host='localhost',
        #                             database='pickapump')

        #CREATE DATABASE CONNECTION PRODUCTION
        conn = mysql.connector.connect(user=config.username, password=config.password,
                                    host='localhost',
                                    database='pickapump_app')

        #CHECK DATABASE CONNECTION
        if conn.is_connected() == True:
            print("Database Connection Made!")
            #CREATE MAGICAL CURSOR OBJECT
            cursor = conn.cursor()#TELL MYSQL TO USE PICKAPUMP_APP DATABASE
            cursor.execute("USE pickapump_app")
            cursor.execute("SELECT * FROM stations WHERE idstationname={}".format(fuel_data['idstationName']))
            data = cursor.fetchall()
            station_data['idstationname']=data[0][0]
            station_data['stationName']=data[0][1]
            station_data['address']=data[0][2]
            station_data['town']=data[0][3]
            station_data['county']=data[0][4]
            station_data['postcode']=data[0][5]
            station_data['country']=data[0][6]
            station_data['coords']=data[0][7]
            station_data['telephone']=data[0][8]
            station_data['maplink']=data[0][9]
            print(station_data)

            #CLOSE CONNECTIONS
            conn.commit()
            cursor.close()  
            conn.close()
        
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        conn.close()

    client = tweepy.Client(bearer_token=bearer_token, access_token=access_token, access_token_secret=access_token_secret, consumer_key=consumer_key, consumer_secret=consumer_secret)
    if float(fuel_data['petrol']) > 0 and float(fuel_data['diesel']) > 0 and float(fuel_data['kero']) > 0 and float(fuel_data['petrolplus']) > 0 and float(fuel_data['dieselplus']) > 0:
        response = client.create_tweet(text="Petrol: {}{}\nDiesel: {}{}\nPetrol+: {}{}\nDiesel+: {}{}\nKero: {}{}\n\n{}\n{}, {}, {}, {}, {}\nTel:{}\n\nShow on Map:{}\n\n#PetrolPrice #DieselPrice #FuelPrice #PickaPump #Ireland #NorthernIreland".format(str(fuel_data['petrol']),currency,str(fuel_data['diesel']),currency, str(fuel_data['petrolplus']),currency,str(fuel_data['dieselplus']),currency,str(fuel_data['kero']),currency,station_data['stationName'],station_data['address'],station_data['town'],station_data['county'],station_data['postcode'],station_data['country'],str(station_data['telephone']),station_data['maplink']))
        return response
    elif float(fuel_data['petrol']) > 0 and float(fuel_data['diesel']) > 0 and float(fuel_data['petrolplus']) > 0 and float(fuel_data['dieselplus']) > 0:
        response = client.create_tweet(text="Petrol: {}{}\nDiesel: {}{}\nPetrol+: {}{}\nDiesel+: {}{}\n\n{}\n{}, {}, {}, {}, {}\nTel:{}\n\nShow on Map:{}\n\n#PetrolPrice #DieselPrice #FuelPrice #Ireland #NorthernIreland".format(str(fuel_data['petrol']),currency,str(fuel_data['diesel']),currency, str(fuel_data['petrolplus']),currency,str(fuel_data['dieselplus']),currency,station_data['stationName'],station_data['address'],station_data['town'],station_data['county'],station_data['postcode'],station_data['country'],str(station_data['telephone']),station_data['maplink']))
        return response
    elif float(fuel_data['petrol']) > 0 and float(fuel_data['diesel']) > 0 and float(fuel_data['kero']) > 0:
        response = client.create_tweet(text="Petrol: {}{}\nDiesel: {}{}\nKero: {}{}\n\n{}\n{}, {}, {}, {}, {}\nTel:{}\n\nShow on Map:{}\n\n#PetrolPrice #DieselPrice #FuelPrice #PickaPump #Ireland #NorthernIreland".format(str(fuel_data['petrol']),currency,str(fuel_data['diesel']),currency, str(fuel_data['kero']), currency, station_data['stationName'],station_data['address'],station_data['town'],station_data['county'],station_data['postcode'],station_data['country'],str(station_data['telephone']),station_data['maplink']))
        return response
    elif float(fuel_data['petrol']) > 0 and float(fuel_data['diesel']) > 0:
        response = client.create_tweet(text="Petrol: {}{}\nDiesel: {}{}\n\n{}\n{}, {}, {}, {}, {}\nTel:{}\n\nShow on Map:{}\n\n#PetrolPrice #DieselPrice #FuelPrice #PickaPump #Ireland #NorthernIreland #FuelPricesIreland #FuelPricesUK".format(str(fuel_data['petrol']),currency,str(fuel_data['diesel']),currency,station_data['stationName'],station_data['address'],station_data['town'],station_data['county'],station_data['postcode'],station_data['country'],str(station_data['telephone']),station_data['maplink']))
        return response
    elif float(fuel_data['diesel']) > 0:
        response = client.create_tweet(text="Diesel: {}{}\n\n{}\n{}, {}, {}, {}, {}\nTel:{}\n\nShow on Map:{}\n\n#PetrolPrice #DieselPrice #FuelPrice #PickaPump #Ireland #NorthernIreland #FuelPricesIreland #FuelPricesUK".format(str(fuel_data['diesel']),currency,station_data['stationName'],station_data['address'],station_data['town'],station_data['county'],station_data['postcode'],station_data['country'],str(station_data['telephone']),station_data['maplink']))
        return response

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5247, ssl_context='adhoc')