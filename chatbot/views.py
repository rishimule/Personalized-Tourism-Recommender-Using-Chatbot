from django.http import HttpResponse
from django.shortcuts import render
import time
import datetime as dtt
from datetime import date
from datetime import datetime
from pprint import pprint as pp

# Import Models
from .models import Search

# Get base folder
from django.conf import settings
BASE_DIR = settings.BASE_DIR

# For Data handling
import numpy as np
import pandas as pd

# To get distance between two places
import geopy.distance

# For GeoCoding
from geopy.geocoders import Nominatim
from opencage.geocoder import OpenCageGeocode

# Functions

def get_no_of_days(date1,date2):
    """Get No of days between two dates

    Args:
        date1 (str): Start Date (dd-mm-yyyy)
        date2 (str): End Date (dd-mm-yyyy)

    Returns:
        int: No of days inclusive
    """
    print(date1, date2)
    date_format = "%d-%m-%Y" 
    d0 = datetime.strptime(date1, date_format)
    d1 = datetime.strptime(date2, date_format)
    delta = d1 - d0
    print(delta.days + 1)
    return delta.days+1

def get_loc_data(addr):
    """Get latitude and Longitude of user's location

    Args:
        addr (str): Address of User

    Returns:
        list: [Latitude,Longitude]
    """
    key = 'a2af0c6d20454780ae7e96edfb4e9a3c'
    geocoder = OpenCageGeocode(key)
    query = f'{addr} India'  
    results = geocoder.geocode(query)
    print('Getting User Location data')
    pp(results[0]['geometry'])
    lat = results[0]['geometry']['lat']
    lon = results[0]['geometry']['lng']
    return [lat,lon ]

def get_distance_km(lat1, lon1, lat2, lon2):
    """Get distance between places.

    Args:
        lat1 (int): Latitude of place A
        lon1 (int): Longitude of place A
        lat2 (int): Latitude of place B
        lon2 (int): Longitude of place B

    Returns:
        float: Distance in KM
    """
    return geopy.distance.distance((lat1, lon1), (lat2, lon2)).km + 20

def weighted_rating(v, m, R, C, AQI, c_or_e, no_of_places):
    """Calculate the Weighted Ratings

    Args:
        v (float): average rating for each item
        m (float): minimum votes required to be classified as popular
        R (pd.Series): average rating for the item
        C (float): average rating for the whole dataset
        AQI (pd.Series): AQI for the item  
        c_or_e (boolean): Existence of Child or Elder
        no_of_places (pd.Series): no_of_places for item

    Returns:
        pd.Series: Weighted Rating
    """
    # IMDB like scoring function
    finalresult = ((v / (v + m)) * R) + ((m / (v + m)) * C)

    # 100 points for each place in no_of_places
    finalresult += no_of_places*100

    # Child or elder
    if c_or_e:
        finalresult = finalresult - 0.1*AQI*finalresult
    return finalresult

def assign_popular_based_score(cities_df, c_or_e):
    """Get Weighted Score and Sort the Data

    Args:
        cities_df (pd.DataFrame): Cities DataFrame
        c_or_e (boolean): Existence of child or elder

    Returns:
        pd.DataFrame: Sorted DataFrame based on weighted Score
    """

    # C is the average rating across the whole dataset
    C = np.mean(cities_df['city_score'])

    # m is the minimum votes required to be listed in the popular items(defined by > percentile 80 of total votes)
    m = np.percentile(cities_df['Rating_count'], 70)

    # Reducing data
    cities_df = cities_df[cities_df['Rating_count'] >= m]

    # R is the average rating for the item
    R = cities_df['city_score']

    # v is the number of votes for the item.
    v = cities_df['Rating_count']

    # AQI for the item
    AQI = cities_df['AQI']

    # no_of_places for item
    no_of_places = cities_df['no_of_places']

    cities_df['weighted_rating'] = weighted_rating(
        v, m, R, C, AQI, c_or_e, no_of_places)
    print(cities_df)
    return cities_df.sort_values('weighted_rating', ascending=False).copy()


# Create your views here.
def indexView(request):
    return HttpResponse("This is chatbot index page!")

def FromChatbotView(request):
    # http://127.0.0.1:8000/chatbot/recommend?name=Rishi+Mule&age=4&people=4&child=FALSE&elder=TRUE&startdate=05-06-2022&enddate=10-06-2022&city=Mumbai&state=Maharashtra&radius=350
    
    data = {k: v[0] for k, v in dict(request.GET).items()}
    print(data)
    data['days'] = get_no_of_days(data['startdate'], data['enddate'])

    # data = {'name': 'Rishi Mule',
    #         'age': '19',
    #         'people': '4',
    #         'child': 'FALSE',
    #         'elder': 'TRUE', 
    #         'startdate': '05-06-2022', 
    #         'enddate': '10-06-2022', 
    #         'city': 'Mumbai', 
    #         'state': 'Maharashtra',
    #         'days': '4',
    #         'radius': '400'
    #         }

    user_inputs = {
        'name'        : data['name'],
        'age'         : int(data['age']),
        'city_name'   : data['city'],
        'state_name'  : data['state'],
        'startdate'   : data['startdate'],
        'enddate'     : data['enddate'],
        'radius_km'   : int(data['radius']),
        'days'        : int(data['days']),
        'no_of_people': int(data['people']),
        'is_child'    : data['child'].upper()=='TRUE',
        'is_elder'    : data['elder'].upper()=='TRUE',
        # 'history'     : data['history'].upper()!='TRUE',
    }
    
    if not 'history' in data.keys():
        row_entry = Search(username = request.user.username,
                            name = user_inputs['name'],
                            age = user_inputs['age'],
                            people = user_inputs['no_of_people'],
                            child_in_group = user_inputs['is_child'],
                            elder_in_group = user_inputs['is_elder'],
                            startdate = datetime.strptime(user_inputs['startdate'], '%d-%m-%Y').date(),
                            enddate = datetime.strptime(user_inputs['enddate'], '%d-%m-%Y').date(),
                            state = user_inputs['state_name'],
                            current_city = user_inputs['city_name'],
                            days = user_inputs['days'],
                            radius = user_inputs['radius_km']
                        )
        row_entry.save()

    # import cities data
    df = pd.read_hdf('cities.hdf','df')
    
    # Get User Lat & Lon
    lat2, lon2 = get_loc_data(f'{user_inputs["city_name"]} {user_inputs["state_name"]}')

    # Frind Distance from user
    df['distance'] = df.apply(lambda x: get_distance_km( lat1=x['lat'] , lon1=x['lon'] , lat2=lat2, lon2=lon2), axis=1)
    
    # Reduce the Data  
    smalldf = df[(df['distance'] < user_inputs['radius_km']+50) & df['no_of_places'] > user_inputs['days']]
    new_radius = user_inputs['radius_km']+50
    new_days = user_inputs['days']

    while smalldf.shape[0] < 20:
        new_radius += 50
        new_days -= 0.5
        if new_days <= 1:
            new_days = 1
        smalldf = df[df['distance'] < new_radius]   
        print(f'Now Radius: {new_radius}')    
    
    # Get Weighted Scores    
    cities_df = assign_popular_based_score(smalldf,(user_inputs['is_child'] or user_inputs['is_elder']))
        
    # Printing
    print()
    print(cities_df)
    print()
    print(cities_df.head())
    print(request.user.username)
    city_results = cities_df.head().to_dict('records')
    
    if not 'history' in data.keys():
        row_entry.results = city_results
        row_entry.save()
        
        
    return render(request, 'chatbot/result.html', {'city_results': city_results})
