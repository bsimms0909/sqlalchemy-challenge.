# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask,jsonify
import pandas as pd
import datetime as dt

#################################################
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#################################################


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return the precipitation data for the last year."""
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp)\
                     .filter(Measurement.date >= one_year_ago.strftime("%Y-%m-%d")).all()
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    """Return a JSON list of stations."""
    results = session.query(Station.station, Station.name).all()
    stations_list = [{'station': station, 'name': name} for station, name in results]
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    """Return the temperature observations for the last year of the most active station."""
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station = session.query(Measurement.station)\
                                .group_by(Measurement.station)\
                                .order_by(func.count(Measurement.id).desc())\
                                .first()
    results = session.query(Measurement.date, Measurement.tobs)\
                     .filter(Measurement.station == most_active_station[0])\
                     .filter(Measurement.date >= one_year_ago.strftime("%Y-%m-%d")).all()
    tobs_list = [{'date': date, 'temperature': tobs} for date, tobs in results]
    return jsonify(tobs_list)


@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temp_range(start, end=None):
    """Return TMIN, TAVG, TMAX for a specified start or start-end range."""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if end:
        results = session.query(*sel)\
                         .filter(Measurement.date >= start)\
                         .filter(Measurement.date <= end).all()
    else:
        results = session.query(*sel)\
                         .filter(Measurement.date >= start).all()
    temp_stats = [{'TMIN': result[0], 'TAVG': result[1], 'TMAX': result[2]} for result in results]
    return jsonify(temp_stats)

@app.route('/')
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

if __name__ == '__main__':
    app.run(debug=True)

session.close()