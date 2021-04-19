from flask import Flask, render_template, request
from utilities.data_collection import get_cities_for_continent
from utilities.data_visualisation import process_cities, find_size, find_clusters, find_timings
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost/weatherapp"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# class Weather(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     lat = db.Column(db.Float)
#     lon = db.Column(db.Float)
#     mean_temp = db.Column(db.Float)
#     min_temp = db.Column(db.Float)
#     min_temp_time = db.Column(db.DateTime)
#     max_temp = db.Column(db.Float)
#     max_temp_time = db.Column(db.DateTime)
#
#     def __init__(self, lat, lon, mean_temp, min_temp, min_temp_time, max_temp, max_temp_time):
#         self.lat = lat
#         self.lon = lon
#         self.mean_temp = mean_temp
#         self.min_temp = min_temp
#         self.min_temp_time = min_temp_time
#         self.max_temp = max_temp
#         self.max_temp_time = max_temp_time
#
#     def __repr__(self):
#         return f"({lat}, {lon}, {mean_temp}, {min_temp}, {min_temp_time}, {max_temp}, {max_temp_time})"
#
# class CityCountryMdata(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     lat = db.Column(db.Float)
#     lon = db.Column(db.Float)
#     citycountry = db.Column(db.Text)
#     continent = db.Column(db.String(5))
#
#     def __init__(self, lat, lon, citycountry, continent):
#         self.lat = lat
#         self.lon = lon
#         self.citycountry = citycountry
#         self.continent = continent
#
#     def __repr__(self):
#         return f"({lat}, {lon}, {citycountry}, {continent})"
#

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':

        af = get_cities_for_continent('AF', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        an = get_cities_for_continent('AN', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        aa = get_cities_for_continent('AS', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        au = get_cities_for_continent('OC', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        eu = get_cities_for_continent('EU', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        na = get_cities_for_continent('NA', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        sa = get_cities_for_continent('SA', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]

        return render_template('index.html', af=af, an=an, aa=aa, au=au, eu=eu, na=na, sa=sa)
    else:

        chosen_cities = []
        continent_count = 0
        af = get_cities_for_continent('AF', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        an = get_cities_for_continent('AN', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        aa = get_cities_for_continent('AS', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        au = get_cities_for_continent('OC', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        eu = get_cities_for_continent('EU', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        na = get_cities_for_continent('NA', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]
        sa = get_cities_for_continent('SA', app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])[:10]


        if 'City' not in request.form.getlist('africa-city'):
            continent_count = continent_count + 1
            chosen_cities.extend([city for city in request.form.getlist('africa-city')])

        if 'City' not in request.form.getlist('antarctica-city'):
            continent_count = continent_count + 1
            chosen_cities.extend([city for city in request.form.getlist('antarctica-city')])

        if 'City' not in request.form.getlist('asia-city'):
            continent_count = continent_count + 1
            chosen_cities.extend([city for city in request.form.getlist('asia-city')])

        if 'City' not in request.form.getlist('australia-city'):
            continent_count = continent_count + 1
            chosen_cities.extend([city for city in request.form.getlist('australia-city')])

        if 'City' not in request.form.getlist('europe-city'):
            continent_count = continent_count + 1
            chosen_cities.extend([city for city in request.form.getlist('europe-city')])

        if 'City' not in request.form.getlist('namerica-city'):
            continent_count = continent_count + 1
            chosen_cities.extend([city for city in request.form.getlist('namerica-city')])

        if 'City' not in request.form.getlist('samerica-city'):
            continent_count = continent_count + 1
            chosen_cities.extend([city for city in request.form.getlist('samerica-city')])

        # sample_input = ["Cairo, Egypt",
        #                 "Kinshasa, Democratic Republic of the Congo",
        #                 "Luanda, Angola",
        #                 "Nairobi, Kenya",
        #                 "McMurdo Station",
        #                 "Karachi, Pakistan",
        #                 "Dhaka, Bangladesh",
        #                 "Delhi, India",
        #                 "Mumbai, India",
        #                 "Sydney, Australia",
        #                 "Melbourne, Australia",
        #                 "Brisbane, Australia",
        #                 "Perth, Australia",
        #                 "Moscow, Russia",
        #                 "Paris, France",
        #                 "London, United Kingdom",
        #                 "Madrid, Spain",
        #                 "Mexico City, Mexico",
        #                 "New York City, United States",
        #                 "Los Angeles, United States",
        #                 "Chicago, United States",
        #                 "Rio de Janeiro, Brazil",
        #                 "Santiago, Brazil",
        #                 "Quito, Ecuador",
        #                 "Cali, Colombia"
        #                 ]
        # continent_count = 7

        resultDict = process_cities(chosen_cities, request.form.get('from'), request.form.get('to'),
                                    app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                    app.config["DB_HOST"])

        resultDictSize = find_size(resultDict, app.config["DB_NAME"], app.config["DB_PASSWORD"], app.config["DB_USER"],
                                   app.config["DB_HOST"])

        resultDictSizeCluster = find_clusters(resultDictSize, continent_count)

        resultDictSizeClusterTime = find_timings(resultDictSizeCluster, app.config["DB_NAME"],
                                                 app.config["DB_PASSWORD"], app.config["DB_USER"],
                                                 app.config["DB_HOST"])

        return render_template('index.html', af=af, an=an, aa=aa, au=au, eu=eu, na=na, sa=sa,
                               result=resultDictSizeClusterTime)

if __name__ == "__main__":
    app.run(host='0.0.0.0')