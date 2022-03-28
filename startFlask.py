from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import config

currentCoords = None
middle = ''

app = Flask(__name__)
@app.route('/fuel', methods=['GET', 'POST'])
def index(results={}):
    try:
        #CREATE DATABASE CONNECTION DEVELOPER
        # conn = mysql.connector.connect(user='root', password='97551',
        #                             host='localhost',
        #                             database='pickapump')

        #CREATE DATABASE CONNECTION PRODUCTION
        conn = mysql.connector.connect(user=config.username, password=config.password,
                                    host='localhost',
                                    database='pickapump')

        #CHECK DATABASE CONNECTION
        if conn.is_connected() == True:
            global middle
            print("Database Connection Made!")
            #CREATE MAGICAL CURSOR OBJECT
            cursor = conn.cursor()
            #TELL MYSQL TO USE PICKAPUMP_APP DATABASE
            cursor.execute("USE pickapump_app")
            #USE COORDS TO CHECK IF STATION EXISTS
            cursor.execute("SELECT * FROM stations")
            data = cursor.fetchall()

            for entries in data:
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

    f = open('./templates/fuelForm.html','w')
    start = """<html lang="en">
                <head>
                    <!-- Required meta tags -->
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <!-- Latest compiled and minified CSS -->
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">    </head>
                    <!-- Custom CSS -->
                    <link rel="stylesheet" href="stylesheet.css">
                </head>
                <body>
                    <div class="basicFormat">
                        <form method="post" enctype="multipart/form-data">
                            <div class="mb-3">
                            <label class="form-check-label" for="station">Choose Station</label>
                                <select class="form-check-input" name="station" id="station"> """

    finish = """                </select>
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
                                    <input type="number" step="0.1" class="form-control" name="kero" id="kero">
                                </div>
                                <div class="mb-3 form-check">
                                <label class="form-check-label" for="sterling">Choose Currency</label>
                                <select class="form-check-input" name="currency" id="currency">
                                    <option value="sterling">Sterling</option>
                                    <option value="euro">Euro</option>
                                </select>
                                </div>
                                <div class="mb-3 form-check">
                                    <label class="form-check-label" for="image">Image</label>
                                    <input type="file" class="form-check-input" name="image" id="image">
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

    if request.method == "GET":
        return render_template("fuelForm.html", title='PickAPump Fuel Entry') 

    results.update({"station":request.form["station"]})  
    results.update({"petrol":request.form["petrol"]})  
    results.update({"diesel":request.form["diesel"]})  
    results.update({"kero":request.form["kero"]})  
    results.update({"currency":request.form["currency"]})  

    file = request.files['image']
    file.save("price.jpg")
    date_added = datetime.now()

    fuel_data = {
    'idstationName': results["station"],
    'petrol': results["petrol"],
    'diesel': results["diesel"],
    'kero': results["kero"],
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
                                    database='pickapump')

        #CHECK DATABASE CONNECTION
        if conn.is_connected() == True:
            print("Database Connection Made!")

            #CREATE MAGICAL CURSOR OBJECT
            cursor = conn.cursor()

            #CREATE FUEL INSERT STRING
            add_fuel = ("INSERT INTO fuel "
                        "(idstationname, petrolprice, dieselprice, keroprice, currency, dateadded) "
                        "VALUES (%(idstationName)s, %(petrol)s, %(diesel)s, %(kero)s, %(currency)s, %(date)s,);")
            
            #TELL MYSQL TO USE PICKAPUMP_APP DATABASE
            cursor.execute("USE pickapump")
            cursor.execute(add_fuel, fuel_data)

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

    return redirect("https://pickapump.com")

 
@app.route('/station', methods=['GET', 'POST'])
def station(results={}):
    if request.method == "GET":
        return render_template("index.html", title='PickAPump Fuel Entry')   

    results.update({"stationName":request.form["stationName"]})
    results.update({"address":request.form["address"]})  
    results.update({"postCode":request.form["postCode"]}) 
    results.update({"country":request.form["country"]})  
    results.update({"coords":request.form["coords"]}) 
    results.update({"telephone":request.form["telephone"]}) 

    station_data = {
    'stationName': results["stationName"],
    'address': results["address"],
    'postcode': results["postCode"],
    'country': results["country"],
    'coords': results["coords"],
    'telephone': results["telephone"],
    }
 
    try:
        #CREATE DATABASE CONNECTION
        conn = mysql.connector.connect(user='root', password='97551',
                                    host='localhost',
                                    database='pickapump')

        #CHECK DATABASE CONNECTION
        if conn.is_connected() == True:
            print("Database Connection Made!")
            #CREATE MAGICAL CURSOR OBJECT
            cursor = conn.cursor()
            #CREATE STATION INSERT STRING
            add_station = ("INSERT INTO stationname "
               "(stationName, address, postcode, country, coords, telephone) "
               "VALUES (%(stationName)s, %(address)s, %(postcode)s, %(country)s, %(coords)s, %(telephone)s);")
            #TELL MYSQL TO USE PICKAPUMP_APP DATABASE
            cursor.execute("USE pickapump")
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

    
if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5247)