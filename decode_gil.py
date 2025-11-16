# Author: Gil Pinheiro
# Read AIS messages, get ship code, name, coordinates and save to a csv file

from pyais.stream import TCPConnection
import csv

host = 'localhost'
port = 10110

ship_list =  []
msg_type =  [21]

# Empty file navios.csv
file_path = "navios.csv"
file_object = open(file_path, 'w')
file_object.close()


for msg in TCPConnection(host, port=port):
    decoded_msg = msg.decode()
    ais_content = decoded_msg
    if ais_content.msg_type in msg_type:

        mmsi = ais_content.mmsi

        # Check if ship is already in the ship_list
        if mmsi not in ship_list:
            name = ais_content.name
            lat = ais_content.lat
            lon = ais_content.lon
            str = "%d" % mmsi + ", " + name + ", " + "%6.4f" % lat + ", " + "%6.4f" % lon
            
            # Insert the new ship
            ship_list.append(mmsi)

            # Include a new ship to the navios.csv file 
            with open('navios.csv', 'a') as file:
                writer = csv.writer(file, lineterminator='\n')
                writer.writerow((mmsi, name, lat, lon))

            print(ship_list)
            print(str)

    #print(ais_content)
