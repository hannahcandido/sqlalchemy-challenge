# Import the dependencies.
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Reesources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
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

@app.route("/")
def welcome():
    """Welcome page with available API routes."""
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYY.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year from last date in database
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= previous_year).all()

    # Close session after the query
    session.close()

    # Return a dictionary with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Query all stations and return a list
    results = session.query(Station.station).all()

    # Close session after the query
    session.close()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for the previous year."""
    # Calculate the date 1 year ago from the last date in the database
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all temperature observations (tobs) from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Close session after the query
    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results as JSON
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX based on the given date range."""
    # Select statement to fetch minimum, average, and maximum temperature
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Process the 'start' date and 'end' date (if provided)
    start = dt.datetime.strptime(start, "%m%d%Y")  # Convert start date to datetime
    if end:
        end = dt.datetime.strptime(end, "%m%d%Y")  # Convert end date to datetime

    # Query for temperature stats based on the provided date range
    query = session.query(*sel).filter(Measurement.date >= start)
    if end:
        query = query.filter(Measurement.date <= end)  

    # Execute the query and fetch the result
    results = query.all()

    # Close session after the query
    session.close()

    # Unravel results into a 1D array and return as a JSON response
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()
