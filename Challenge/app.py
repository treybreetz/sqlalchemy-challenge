# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 19:16:47 2023

@author: baseb
"""

# Set up the Flask Weather App
# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database engine for Flask app
# Create function allows access to SQLite database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = scoped_session(sessionmaker(bind=engine))
# Create Flask app, all routes go after this code
app = Flask(__name__)

# Define welcome route
@app.route("/")

def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/temp/<start><br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/temp/<start>/<end><br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"

    )


# Precipitation Route
@app.route("/api/v1.0/precipitation")

def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)
# check website changes, (http://127.0.0.1:5000/), should be block of dates

# Stations Route
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())
# check website changes, (http://localhost:5000/), stations with USC0051xxxx codes

#Monthly Temperature Route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    
    # Create a list of dictionaries with date and temperature
    temps = [{"date": date, "tobs": tobs} for date, tobs in results]
    
    return jsonify(temps)
#do flask run, (http://localhost:5000/), block of temps (F)

# Statistic Route
@app.route("/api/v1.0/temp/<start>")
def stats_start(start):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    try:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(minavgmax=temps)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/v1.0/temp/<start>/<end>")
def stats_start_end(start, end):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    try:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(minavgmax=temps)
    except Exception as e:
        return jsonify({"error": str(e)})

# from tech help
if __name__ == "__main__":
    app.run(debug=False)
