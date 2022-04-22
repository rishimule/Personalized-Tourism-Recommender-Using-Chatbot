from django.shortcuts import render
import pandas as pd
import numpy as np
from pprint import pprint as pp

from chatbot.models import Search


# Functions
def SearchHistoryView(request):
    curuser = request.user
    print(curuser)
    search_list = Search.objects.filter(username = curuser.username)
    return render(request, template_name='history/search_history.html', context={"search_list":search_list})



def weighted_rating(v,m,R,C):
    '''
    Calculate the weighted rating
    
    Args:
    v -> average rating for each item (float)
    m -> minimum votes required to be classified as popular (float)
    R -> average rating for the item (pd.Series)
    C -> average rating for the whole dataset (pd.Series)
    
    Returns:
    pd.Series
    '''
    return ( (v / (v + m)) * R) + ( (m / (v + m)) * C )


def assign_popular_based_score(places_df):

    # C is the average rating across the whole dataset
    C = np.mean(places_df['Rating_mean'])

    # m is the minimum votes required to be listed in the popular items(defined by > percentile 80 of total votes)
    m = np.percentile(places_df['Rating_count'], 75)

    # Reducing data
    places_df = places_df[places_df['Rating_count'] >= m]

    # R is the average rating for the item
    R = places_df['Rating_mean']

    # v is the number of votes for the item.
    v = places_df['Rating_count']

    places_df['weighted_rating'] = weighted_rating(v,m,R,C)
    print(places_df)
    return places_df.sort_values('weighted_rating', ascending = False).copy()


# Create your views here.




def PlacesInCityView(request, cityslug):
    # import cities data
    df2 = pd.read_hdf('cities.hdf','df')
    mycity = df2[df2['slug']==cityslug]
    mycity_resluts = mycity.to_dict('records')[0]
    pp(mycity_resluts)
    
    
    df = pd.read_csv('places.csv', index_col=0)
    singlecitydf = df[df['slug'] == cityslug]
    places_df = assign_popular_based_score(singlecitydf).head(10)    
    print(places_df)
    places_results = places_df.head().to_dict('records')
    pp(places_results)
    pp(mycity_resluts)
    
    
    return render(request, template_name='places/city.html', context={'places_results':places_results,
                                                                      'city':mycity_resluts})