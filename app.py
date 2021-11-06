# Dependencies
from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")


# Route to render index.html template using data from Mongo
@app.route("/")
def index():
    # Find one record of data from the mongo database
    mars_dict = mongo.db.mars.find_one()
    # Return template and data
    return render_template("index.html", data=mars_dict)


@app.route("/scrape")
def scrape():
    # Scrape new data using scrape_mars.py
    mars_scrape = scrape_mars.scrape()
    print(mars_scrape)
    # Update the Mongo database mars_db with the new scraped data mars_scrape using update and upsert=True
    mongo.db.mars.update({}, mars_scrape, upsert=True)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)