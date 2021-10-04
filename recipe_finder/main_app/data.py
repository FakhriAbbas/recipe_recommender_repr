import pickle
from django.core.files.storage import default_storage
from .services import *

ingr_mlb = pickle.load( default_storage.open('./data/pickles/ingr_mlb.pkl', mode='rb') )
# recommender_df = pickle.load( default_storage.open( './data/pickles/recommender_df.pkl', mode='rb' ) )
cuisine_dict = {}
search_space = None

def load_cuisine_data_to_dict(cuisine):
    if cuisine not in cuisine_dict:
        tmp_df = pickle.load(default_storage.open('./data/pickles/cuisine_country_df/recommender_df_' + str(cuisine) + '.pkl' , mode='rb'))
        cuisine_dict[cuisine] = tmp_df
    print(tmp_df.columns)

def get_cuisine_df(cuisine):
    load_cuisine_data_to_dict(cuisine)
    return cuisine_dict[cuisine]

def get_search_space():
    return search_space

def load_cuisine_object_data():
    list = pickle.load(default_storage.open('./data/pickles/cuisine_list.pkl', mode='rb'))
    newlist = sorted(list, key=lambda k: k['label'])
    return newlist

display_name_dict ={
    'piquant_n' : 'Spicy',
    'sour_n' : 'Sour',
    'salty_n' : 'Salty',
    'sweet_n' : 'Sweet',
    'bitter_n' : 'Bitter',
    'meaty_n' : 'Meaty',
    'saturatedFatContent_n' : 'Saturated fat',
    'fatContent_n' : 'Fat',
    'carbohydrateContent_n' : 'Carbohydrate',
    'sugarContent_n' : 'Sugar',
    'calories_n' : 'Calories',
    'fiberContent_n' : 'Fiber',
    'cholesterolContent_n' : 'Cholesterol',
    'transFatContent_n' : 'Trans fat',
    'sodiumContent_n' : 'Sodium',
    'proteinContent_n' : 'Protein'
}