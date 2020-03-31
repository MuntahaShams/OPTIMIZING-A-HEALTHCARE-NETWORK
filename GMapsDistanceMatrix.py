import requests, json 
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize 
import json
import time

# extract distances between source and destination areas from response json
def distance_matrix(response_json, source, dest, mode):
    dist_matrix = []
    for i in range(0, len(source)):
        for j in range(0, len(dest)):
            matrix_row = {}
            if(response_json['rows'][i]['elements'][j]['status']=='OK'):
                dist_value = response_json['rows'][i]['elements'][j]['distance']['value']
                dur_value = response_json['rows'][i]['elements'][j]['duration']['value']
            else:
                dist_value = -1
                dur_value = -1
            
            matrix_row['mode'] = mode
            matrix_row['origin'] = source[i]
            matrix_row['destination'] = dest[j]
            matrix_row['distance'] = int(dist_value) 
            matrix_row['duration'] = int(dur_value)
            
            dist_matrix.append(matrix_row)
    
    return dist_matrix

# genrate final url from the parameters
def request_url(url, source, dest, mode, api_key, transit_mode, units = None):
    final_url = url + '&origins=' + source + '&destinations=' + dest
    if mode is not None:
        final_url += '&mode=' + mode
    if transit_mode is not None:
        final_url += '&transit_mode=' + transit_mode
    if units is not None:
        final_url += '&units=' + units
    final_url += '&key=' + api_key

    try:
        response = requests.get(final_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else",err)
    return response.json()

def main():
    # google maps distance matrix api key
    api_key = '' # insert your apikey here

    # loading facility data
    facility_data = pd.read_csv("facilities.csv")
    # loading area zipcodes
    area_zipcodes = facility_data['Facility Area-Zipcode'].astype(str).tolist()

    source = area_zipcodes
    dest = area_zipcodes

    # assigning different modes of transit
    modes = ['driving', 'walking', 'bicycling', 'transit']
    transit_modes = ['bus', 'rail']
    # units = ['metric', 'imperial']

    url ='https://maps.googleapis.com/maps/api/distancematrix/json?'

    matrix = []
    # requesting distance matrix responses for different transit modes
    for mode in modes:
        transit = None
        # units = None
        response = {}
        print("Mode: " + mode)
        if(mode == "transit"):
            for transit in transit_modes:
                print("Transit: " + transit)
                response = request_url(url, "|".join(source), "|".join(dest), mode, api_key, transit)
                mode_matrix = distance_matrix(response, source, dest, transit)
                matrix.extend(mode_matrix)
        else:
            response = request_url(url, "|".join(source), "|".join(dest), mode, api_key, transit)
            mode_matrix = distance_matrix(response, source, dest, mode)
            matrix.extend(mode_matrix)
        time.sleep(5)

    # converting matrix to pandas dataframe
    df = pd.DataFrame(matrix)
    print(df.shape)

    # saving dataframe to csv
    df.to_csv("distance_matrix.csv")
    # print(df)

if __name__ == '__main__':
    main()

