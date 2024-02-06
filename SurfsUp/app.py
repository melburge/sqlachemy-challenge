# Import the dependencies
import numpy as np
import datetime as dt
from datetime import timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Declare a Base using `automap_base()
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with = engine)

# Assign the measurement class to a variable called `Measurement` and
Measurement = Base.classes.measurement

# the station class to a variable called `Station`
Station = Base.classes.station

# Create a session
session = Session(bind = engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################



# Starting at the Home Page for Honolulu Hawaii Climate API and listing all the avaliable routes
@app.route('/')
def home_page():
    return (
        f'Honolulu Hawaii Climate API Home Page<br>'
        f'Available Routes:<br>'
        f'/api/v1.0/precipitation<br>'
        f'/api/v1.0/stations<br>'
        f'/api/v1.0/tobs<br>'
        f'/api/v1.0/<start><br>'
        f'/api/v1.0/<start>/<end><br>'
        )


# Converting the query results from the percipitation data into a dictionary for the last 12 months
# using date as the key and prcp as the value.

# Percipitation link
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    precp_data = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    precp_data = {date: 
                  prcp for date,
                  prcp in precp_data}
    
    return jsonify(precp_data)

# Stations link
# Return JSON list of stations
@app.route('/api/v1.0/stations')
def stations():

    session = Session(engine)
    stations_data = session.query(Station.station).all()
    session.close()

    station_list = [station[0] for station in stations_data]

    return jsonify(station_list)

# Tobs Link
# Query the temperature obs for most active station previous year
@app.route('/api/v1.0/tobs')
def tobs():

    session = Session(engine)

    # Retrieve most active station
    active_station = session.query(Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate date one year from db date
    date_start = session.query(func.max(Measurement.date)).filter(Measurement.station == active_station).scalar()
    date_end = (dt.datetime.strptime(date_start, '%Y-%m-%d') - dt.timedelta(days = 365)).strftime('%Y-%m-%d')

    # Temp obs most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == active_station)\
        .filter(Measurement.date >= date_end).all()

    session.close()

    # Create TOBS Dictionary
    tobs_dict = {date: tobs for date, tobs in tobs_data}

    # Return as JSON
    return jsonify(tobs_dict)

# Start and end dates link
# Return JSON list of the min avg, and max temps
@app.route('/api/v1.0/<start>/<end>')
def temp_dates(start, end):

    session = Session(engine)
    
    # All min, avg and max TOBS between start and end dates
    all_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Create Temp Results Dictionary
    temp_data = {
        'min_temp': all_data[0][0],
        'avg_temp': all_data[0][1],
        'max_temp': all_data[0][2]
    }
    
    # Return JSON temp data
    return jsonify(temp_data)

if __name__ == '__main__':

    app.run(debug=True)























