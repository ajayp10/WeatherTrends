from weatherbit.api import Api
from datetime import datetime, timedelta
import requests
import psycopg2

import json
import os

import pandas as pd
import re
import pycountry_convert as pc


def store_to_db(lat, lon, start_date, end_date, db_name, db_password, db_user, db_host):
    """
    Queries the weatherbit using API/requests to retrieve information from desired <start_date> to <end_date>
    and stores in weather table.

    :param lat: lattitude coordinate
    :param lon: longtitude coordinate
    :param start_date: date object
    :param end_date: date object
    :return void:
    """
    api_key = os.environ.get('API_KEY')
    api = Api(api_key)

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        conn = psycopg2.connect(dbname=db_name, password=db_password, user=db_user, host=db_host)
        cur = conn.cursor()

        if start_date < end_date:

            for n in range((end_date - start_date).days):
                sdate = start_date + timedelta(n)
                edate = start_date + timedelta(n+1)

                ## Using an API Wrapper
                # api.set_granularity('daily')
                # history = api.get_history(lat=lat, lon=lon, start_date=str(sdate.date()), end_date=str(edate.date()))
                # print(history.get_series(['temp','min_temp','max_temp', 'min_temp_ts', 'max_temp_ts']))


                ## Using the API directly
                response = requests.get("https://api.weatherbit.io/v2.0/history/daily?lat="+str(lat)+"&lon="+str(lon)+"&start_date="+str(sdate.date())+"&end_date="+str(edate.date())+"&key="+api_key)

                if response.status_code == 200:

                    # query = """ INSERT INTO weather (lat, lon, mean_temp, min_temp, min_temp_time, max_temp, max_temp_time) VALUES (%s,%s,%s,%s,%s,%s,%s) """
                    query = """ INSERT INTO test_weather (lat, lon, mean_temp, min_temp, min_temp_time, max_temp, max_temp_time) VALUES (%s,%s,%s,%s,%s,%s,%s) """
                    record = (lat,
                              lon,
                              response.json()["data"][0]["temp"],
                              response.json()["data"][0]["min_temp"],
                              datetime.fromtimestamp(
                                  int(response.json()["data"][0]["min_temp_ts"])
                              ).strftime('%Y-%m-%d %H:%M:%S'),
                              response.json()["data"][0]["max_temp"],
                              datetime.fromtimestamp(
                                  int(response.json()["data"][0]["max_temp_ts"])
                              ).strftime('%Y-%m-%d %H:%M:%S'))
                    cur.execute(query, record)

        conn.commit()
        conn.close()

    except Exception as e:
        print("Exiting store_to_db due to exception: ", e.__class__)

    finally:
        if conn:
            cur.close()
            conn.close()


def collect_data(filename, start_date, end_date):
    """
    For each city in json file <filename>, store_to_db() method is invoked to store history information to database.

    :param filename: cities json object
    :param start_date: date object
    :param end_date: date object
    :return void:
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.realpath( __file__ )))
    filepath = os.path.join(root_dir, "data")

    with open(os.path.join(filepath, filename)) as json_data:
        data = json.load(json_data)

    for continent in data:
        for city in data[continent]:
            store_to_db(city["lat"], city["lon"], start_date, end_date, db_name, db_password, db_user, db_host)


def load_master_data():
    """
    Continent details for each city from weatherbit metadata is pulled using pycountry_convert API and stored in
    city_country_mdata table.

    :return void:
    """
    db_name = "postgres"
    db_password = "postgres"
    db_user = "postgres"
    db_host = "localhost"

    root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    filepath = os.path.join(root_dir, "data")

    data = pd.read_csv(os.path.join(filepath, "cities_all.csv"))
    data["city_country"] = data["city_name"].str.cat(data["country_full"],sep=", ")
    data = data.dropna()

    try:
        conn = psycopg2.connect(dbname=db_name, password=db_password, user=db_user, host=db_host)
        cur = conn.cursor()

        for item in data.itertuples():
            continent_flag = 0
            continent_name = ""

            if re.sub("[^a-zA-Z0-9, ]+", "", item[8]):
                try:
                    country_code = pc.country_name_to_country_alpha2(item[5], cn_name_format="default")
                    continent_name = pc.country_alpha2_to_continent_code(country_code)
                except:
                    continent_flag = 1

                if continent_flag == 0:
                    # query = """ INSERT INTO city_country_mdata (lat, lon, citycountry, continent) VALUES (%s,%s,%s,%s) """
                    record = (item[6], item[7], re.sub("[^a-zA-Z0-9, ]+", "",item[8]), continent_name)
                    cur.execute(query, record)

        conn.commit()
        conn.close()

    except Exception as e:
        print("Exiting load_master_data due to exception: ", e.__class__)

    finally:
        if conn:
            cur.close()
            conn.close()


def get_cities_for_continent(continent, db_name, db_password, db_user, db_host):
    """
    Given the <continent>, its corresponding cities are queried from city_country_mdata table.

    :param continent: string with 2 characters
    :return result: list of cities
    """

    try:
        conn = psycopg2.connect(dbname=db_name, password=db_password, user=db_user, host=db_host)
        cur = conn.cursor()

        query = """ SELECT citycountry from city_country_mdata WHERE continent = %s """
        record = (continent,)
        cur.execute(query, record)
        result = cur.fetchall()

        result = [tup[0] for tup in result]

        conn.commit()
        conn.close()

        return result

    except Exception as e:
        print("Exiting get_cities_for_continent due to exception: ", e.__class__)

    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    # lat = 30.06263
    # lon = 31.24967
    # start_date = '2018-02-01'
    # end_date = '2018-02-02'
    #
    # store_to_db(40.71427, -74.00597, "2020-12-31", "2021-02-01")

    # collect_data("cities.json", "2020-12-01", "2021-02-01")
    print("check dates")

    # load_master_data()

    # print(get_cities_for_continent('AS'))

# CREATE TABLE weather (
# 	id SERIAL PRIMARY KEY,
# 	lat NUMERIC(8,5),
# 	lon NUMERIC(8,5),
#    	mean_temp DECIMAL NOT NULL,
#    	min_temp DECIMAL NOT NULL,
# 	min_temp_time TIMESTAMP,
#    	max_temp DECIMAL NOT NULL,
# 	max_temp_time TIMESTAMP
# );
#
# INSERT INTO weather(lat,lon,mean_temp,min_temp,min_temp_time,max_temp,max_temp_time)
# VALUES(35.7721,-78.63861,7.86,5,to_timestamp(1483272000),10,to_timestamp(1483308000))
#
#
# CREATE TABLE city_country_mdata (
# 	id SERIAL PRIMARY KEY,
# 	lat NUMERIC(8,5),
# 	lon NUMERIC(8,5),
#     citycountry VARCHAR(80),
# 	continent VARCHAR(3)
# );

# INSERT INTO city_country_mdata(lat, lon, citycountry, continent) VALUES (-77.846, 166.676, 'McMurdo Station', 'AN')
# INSERT INTO city_country_mdata(lat, lon, citycountry, continent) VALUES(-4.32758, 15.31357, 'Kinshasa, Democratic Republic of the Congo', 'AF');
# INSERT INTO city_country_mdata(lat, lon, citycountry, continent) VALUES(-8.83682, 13.23432, 'Luanda, Angola', 'AF')