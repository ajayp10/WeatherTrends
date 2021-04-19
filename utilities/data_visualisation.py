import psycopg2
from .data_collection import store_to_db
import numpy as np
import math
from sklearn.cluster import KMeans

def process_cities(cities, from_date, to_date, db_name, db_password, db_user, db_host):
    """
    For each city, its corresponding lattitude and longtitude values are queried from city_country_mdata table and
    stored as key-value pair and returned.

    :param cities: list of cities
    :param from_date: date object
    :param to_date: date object
    :param db_name: database name
    :param db_password: database password
    :param db_user: database username
    :param db_host: database host
    :return: result: dictionary with cities as key and sub dictionary as values which contains values for
    "lat" and "lon"
    """
    result = {}

    try:

        conn = psycopg2.connect(dbname=db_name, password=db_password, user=db_user, host=db_host)
        cur = conn.cursor()

        for city in cities:
            query = """ SELECT lat,lon from city_country_mdata WHERE citycountry = %s """
            record = (city,)
            cur.execute(query, record)

            resultSet = cur.fetchone()

            lat, lon = float(resultSet[0]), float(resultSet[1])

            result[city] = {}
            result[city]["lat"] = lat
            result[city]["lon"] = lon

            store_to_db(lat, lon, from_date, to_date, db_name, db_password, db_user, db_host)

        conn.commit()
        conn.close()

        return result

    except Exception as e:
        print("Exiting process_cities due to exception: ", e.__class__)

    finally:
        if conn:
            cur.close()
            conn.close()


def find_size(resultDict, db_name, db_password, db_user, db_host):
    """
    For each city, depending on the average temperature, the size of pointer is decided and stored in key "size".

    :param resultDict: dictionary with cities as key and sub dictionary as values
    :param db_name: database name
    :param db_password: database password
    :param db_user: database username
    :param db_host: database host
    :return: result: dictionary with cities as key and sub dictionary as values which contains values for
    "size"
    """
    result = []

    try:
        conn = psycopg2.connect(dbname=db_name, password=db_password, user=db_user, host=db_host)
        cur = conn.cursor()

        for city in resultDict:
            # query = """ SELECT AVG (mean_temp)::NUMERIC(8,5) FROM weather WHERE lat = %s and lon = %s """
            query = """ SELECT AVG (mean_temp)::NUMERIC(8,5) FROM test_weather WHERE lat = %s and lon = %s """
            record = (resultDict[city]["lat"], resultDict[city]["lon"])
            cur.execute(query, record)

            result.append(float(cur.fetchone()[0]))

        result = normalise_values(result)

        for index, city in enumerate(resultDict):
            resultDict[city]["size"] = result[index] * 10000

        conn.commit()
        conn.close()

        return resultDict

    except Exception as e:
        print("Exiting find_size due to exception: ", e.__class__)

    finally:
        if conn:
            cur.close()
            conn.close()


def find_clusters(resultDictSize, nclusters):
    """
    For each city, find the cluster it belongs to. Depending on the cluster, a unique color code is added to key
    "color".

    :param resultDictSize: dictionary with cities as key and sub dictionary as values
    :return: resultDictSize: dictionary with cities as key and sub dictionary as values for "color"
    """
    color_mapping = ["red", "orange", "blue", "green", "brown", "gray", "violet"]
    temp_lat = []
    temp_lon = []

    for city in resultDictSize:
        temp_lat.append(resultDictSize[city]["lat"])
        temp_lon.append(resultDictSize[city]["lon"])

    arr = np.array(list(zip(temp_lat, temp_lon)))

    kmeans = KMeans(nclusters).fit(arr)
    clusters = kmeans.labels_

    for index, city in enumerate(resultDictSize):
        resultDictSize[city]["color"] = color_mapping[clusters[index]]

    return resultDictSize


def find_timings(resultDictSizeCluster, db_name, db_password, db_user, db_host):
    """
    For each city, query the lowest and highest temperature and its timings. Store them under appropriate keys.

    :param resultDictSizeCluster: dictionary with cities as key and sub dictionary as values
    :param db_name: database name
    :param db_password: database password
    :param db_user: database username
    :param db_host: database host
    :return: resultDictSizeCluster: dictionary with cities as key and sub dictionary as values which contains values for
    "min_temp", "lmin_temp", "hmin_temp", "max_temp", "lmax_temp" and "hmax_temp"
    """
    try:
        conn = psycopg2.connect(dbname=db_name, password=db_password, user=db_user, host=db_host)
        cur = conn.cursor()

        for city in resultDictSizeCluster:
            # query = """ SELECT min_temp, min_temp_time FROM weather WHERE lat = %s AND lon = %s AND min_temp IN (SELECT MIN(min_temp) FROM weather WHERE lat = %s AND lon = %s) """
            query = """ SELECT min_temp, min_temp_time FROM test_weather WHERE lat = %s AND lon = %s AND min_temp IN (SELECT MIN(min_temp) FROM test_weather WHERE lat = %s AND lon = %s) """
            record = (resultDictSizeCluster[city]["lat"], resultDictSizeCluster[city]["lon"], resultDictSizeCluster[city]["lat"], resultDictSizeCluster[city]["lon"])
            cur.execute(query, record)

            result = cur.fetchall()

            temp_time = []

            for item in result:
                temp = float(item[0])
                temp_time.append(int(str(item[1].time())[:2]))

            temp_time = np.array(temp_time)

            resultDictSizeCluster[city]["min_temp"] = temp
            resultDictSizeCluster[city]["lmin_temp"] = temp_time.min()
            resultDictSizeCluster[city]["hmin_temp"] = temp_time.max()

        for city in resultDictSizeCluster:
            # query = """ SELECT max_temp, max_temp_time FROM weather WHERE lat = %s AND lon = %s AND max_temp IN (SELECT MAX(max_temp) FROM weather WHERE lat = %s AND lon = %s) """
            query = """ SELECT max_temp, max_temp_time FROM test_weather WHERE lat = %s AND lon = %s AND max_temp IN (SELECT MAX(max_temp) FROM test_weather WHERE lat = %s AND lon = %s) """
            record = (resultDictSizeCluster[city]["lat"], resultDictSizeCluster[city]["lon"], resultDictSizeCluster[city]["lat"], resultDictSizeCluster[city]["lon"])
            cur.execute(query, record)

            result = cur.fetchall()

            temp_time = []

            for item in result:
                temp = float(item[0])
                temp_time.append(int(str(item[1].time())[:2]))

            temp_time = np.array(temp_time)

            resultDictSizeCluster[city]["max_temp"] = temp
            resultDictSizeCluster[city]["lmax_temp"] = temp_time.min()
            resultDictSizeCluster[city]["hmax_temp"] = temp_time.max()

        conn.commit()
        conn.close()

        return resultDictSizeCluster

    except Exception as e:
        print("Exiting find_timings due to exception: ", e.__class__)

    finally:
        if conn:
            cur.close()
            conn.close()


def normalise_values(items):
    """
    Normalise values in <items> to a scale of 10.

    :param items: list of input values
    :return: result: normalised values
    """
    start = 1
    end = 10
    width = end - start
    items_array = np.array(items)
    if (items_array.max() - items_array.min()) > 0:
        res = (items_array - items_array.min()) / (items_array.max() - items_array.min()) * width + start
    else:
        res = items_array / items_array

    result = [math.floor(value) for value in res]

    return result


if __name__ == "__main__":
    sample_input = ["Cairo, Egypt",
                    "Kinshasa, Democratic Republic of the Congo",
                    "Luanda, Angola",
                    "Nairobi, Kenya",
                    "McMurdo Station",
                    "Karachi, Pakistan",
                    "Dhaka, Bangladesh",
                    "Delhi, India",
                    "Mumbai, India",
                    "Sydney, Australia",
                    "Melbourne, Australia",
                    "Brisbane, Australia",
                    "Perth, Australia",
                    "Moscow, Russia",
                    "Paris, France",
                    "London, United Kingdom",
                    "Madrid, Spain",
                    "Mexico City, Mexico",
                    "New York City, United States",
                    "Los Angeles, United States",
                    "Chicago, United States",
                    "Rio de Janeiro, Brazil",
                    "Santiago, Brazil",
                    "Quito, Ecuador",
                    "Cali, Colombia"
                    ]

    find_size(process_cities(sample_input, '', ''))