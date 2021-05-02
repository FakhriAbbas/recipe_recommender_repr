import random, string, json, pickle
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from ..data import *
import pandas as pd
import datetime
from ..constants import *

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    result_str = result_str.upper()
    return result_str

def save_data_to_storage(user_id, page_name ,data):
    default_storage.save('./data/results/' + str(user_id) + '/' + page_name , ContentFile(json.dumps(data)))

def delete_file(user_id, page_name):
    default_storage.delete('./data/results/' + str(user_id) + '/' + page_name)

def load_data_from_storage(user_id, page_name):
    content = default_storage.open('./data/results/' + str(user_id)  + '/' + page_name , mode = 'r').readline()
    return content

def get_failure_response(exception_msg):
    response = {}
    response['statue'] = 0
    response['error-msg'] = 'Something went wrong:' + exception_msg
    return response

def get_cuisine_list():
    cuisine_list = [
        'Asian',
        'African',
        'Mediterranean',
        'Middle Eastern',
        'European',
        'North American',
        'South American',
        'Central American',
    ]
    return cuisine_list

def get_course_list():
    course_list = [
        'Afternoon Tea',
        'Appetizers',
        'Beverages',
        'Breads',
        'Breakfast and Brunch',
        'Cocktails',
        'Condiments and Sauces',
        'Desserts',
        'Lunch',
        'Main Dishes',
        'Salads',
        'Side Dishes',
        'Snacks',
        'Soups'
    ]
    return course_list

def get_preference(user_id):
    cuisine_list = get_cuisine_preference(user_id)
    course_list = get_course_preference(user_id)
    exclude_list = list()
    return cuisine_list, course_list, exclude_list

def get_cuisine_preference(user_id):
    preference_json = json.loads(default_storage.open('./data/results/' + str(user_id) + '/preference' , mode = 'r').readline())
    return preference_json['q1']

def get_course_preference(user_id):
    preference_json = json.loads(default_storage.open('./data/results/' + str(user_id) + '/preference' , mode = 'r').readline())
    return preference_json['q3']

def load_cuisine_df(cuisine_list, user_id):
    if check_if_file_exists(user_id,'search_space.pkl'):
        print('loaded')
        return load_search_space(user_id)
    subset_df = pd.DataFrame()
    for c in cuisine_list:
        tmp_df = get_cuisine_df(c)
        subset_df = pd.concat([subset_df, tmp_df])
    return subset_df

def load_ingr_mlb():
    return ingr_mlb

def load_nutrition_mlb():
    return nutrition_mlb

def save_search_space(user_id, search_space_df):
    if check_if_file_exists(user_id, 'search_space.pkl'):
        pass
    else:
        search_space_df.to_pickle(str(default_storage.location) + '/data/results/' + str(user_id) + '/search_space.pkl')

def load_search_space(user_id):
    search_space = get_search_space()
    if search_space == None:
        search_space = pd.read_pickle(str(default_storage.location) + '/data/results/' + str(user_id) + '/search_space.pkl')
    return search_space

def save_study_variables(user_id, dict_ = {}):
    save_data_to_storage(user_id, 'study_settings' ,  dict_ )

def add_to_study_settings(user_id, key, value):
    content = load_data_from_storage(user_id,'study_settings')
    dict = json.loads(content)
    delete_file(user_id, 'study_settings')
    dict[key] = value
    save_study_variables(user_id, dict)

def get_study_settings_value(user_id, value):
    content = load_data_from_storage(user_id, 'study_settings')
    dict = json.loads(content)
    if value in dict:
        return dict[value]
    else:
        return None

def get_user_id(request):
    return request.session.get('USER_ID')

def get_display_name(column_name):
    return display_name_dict[column_name]

def get_relevant_columns():
    return ['id','recipeName','totalTimeInMinutes', 'smallImageUrl','ingredients','course','cuisine', 'url',
                                                                               'piquant_n', 'sour_n', 'salty_n', 'sweet_n', 'bitter_n', 'meaty_n',
                                                                               'saturatedFatContent_n', 'fatContent_n',
                                                                               'carbohydrateContent_n',
                                                                               'sugarContent_n', 'calories_n',
                                                                               'fiberContent_n', 'cholesterolContent_n',
                                                                               'transFatContent_n', 'sodiumContent_n',
                                                                               'proteinContent_n'
                                                                               ]

def get_exploration_progress_service(counter):
    # return 100
    return 100*((counter)/6)

def get_meal_plan_progress_service(counter):
    # return 100
    return 100*((counter)/6)

def check_if_file_exists(user_id, page_name):
    return default_storage.exists('./data/results/' + str(user_id) + '/' + page_name)

def save_dislike_recipe_list(recipe_list, user_id):
    page_name = 'dislike_recipe_list'
    current_session = get_study_settings_value(user_id, 'current_session')
    if check_if_file_exists(user_id, current_session + '/' + page_name):
        delete_file(user_id, current_session + '/' + page_name)
    save_data_to_storage(user_id, current_session + '/' + page_name, recipe_list)

def load_dislike_recipe_list(user_id):
    page_name = 'dislike_recipe_list'
    current_session = get_study_settings_value(user_id, 'current_session')
    if not check_if_file_exists(user_id, current_session + '/' + page_name):
        return []
    return json.loads(load_data_from_storage(user_id, current_session + '/' + page_name))

def load_meal_plan_recipe_list(user_id):
    page_name = 'meal_plan_recipe_list'
    current_session = get_study_settings_value(user_id, 'current_session')
    if not check_if_file_exists(user_id, current_session + '/' + page_name):
        return []
    return json.loads(load_data_from_storage(user_id, current_session + '/' + page_name))

def save_meal_plan_recipe_list(recipe_list, user_id):
    page_name = 'meal_plan_recipe_list'
    current_session = get_study_settings_value(user_id, 'current_session')
    if check_if_file_exists(user_id, current_session + '/' + page_name):
        delete_file(user_id, current_session + '/' + page_name)
    save_data_to_storage(user_id, current_session + '/' + page_name, recipe_list)

def load_user_exploration_history_service(session_name, user_id):
    page_name = str(session_name) + '/' + 'exploration_history'
    if not check_if_file_exists(user_id, page_name):
        return {}
    return json.loads(load_data_from_storage(user_id, page_name))

def save_user_exploration_history_service(session_name, data_dictionary, user_id):
    page_name = session_name + '/' + 'exploration_history'
    if check_if_file_exists(user_id, page_name):
        delete_file(user_id,page_name)
    save_data_to_storage(user_id, page_name, data_dictionary)

def extract_critique_data(request):
    direction = request.POST.get("direction", "")
    column_name = request.POST.get("critique_name", "")
    recipe_name = request.POST.get("recipe_name", "")
    recipe_id = request.POST.get("recipe_id", "")
    return direction, column_name, recipe_name, recipe_id

def log_meal_plan_transaction(recipe_name, user_id, action, session_name):
    name = session_name + '/' + 'meal_plan_logs'
    list_ = [recipe_name, user_id, action, datetime.datetime.now().timestamp()]
    tmp = list([])
    if check_if_file_exists(user_id,name):
        tmp = json.loads(load_data_from_storage(user_id,name))
        delete_file(user_id,name)
    tmp.append(list_)
    print(tmp)
    save_data_to_storage(user_id,name,tmp)

def log_dislike_transaction(recipe_name, user_id, action, session_name):
    name = session_name + '/' + 'dislike_logs'
    list_ = [recipe_name, user_id, action, datetime.datetime.now().timestamp()]
    tmp = list([])
    if check_if_file_exists(user_id,name):
        tmp = json.loads(load_data_from_storage(user_id,name))
        delete_file(user_id,name)
    tmp.append(list_)
    print(tmp)
    save_data_to_storage(user_id,name,tmp)

def log_loading_search_result(user_id, search_number, session_name):
    name = session_name + '/' + 'search_result_logs'
    list_ = [user_id, search_number, datetime.datetime.now().timestamp()]
    tmp = list([])
    if check_if_file_exists(user_id,name):
        tmp = json.loads(load_data_from_storage(user_id,name))
        delete_file(user_id,name)
    tmp.append(list_)
    save_data_to_storage(user_id,name,tmp)

def log_recipe_flavour_nutrition_service(type, recipe_id, is_expanded, user_id, session_name):
    name = session_name + '/' + 'nutrition_flavour_logs'
    list_ = [type, recipe_id, is_expanded, datetime.datetime.now().timestamp()]
    tmp = list([])
    if check_if_file_exists(user_id,name):
        tmp = json.loads(load_data_from_storage(user_id,name))
        delete_file(user_id,name)
    tmp.append(list_)
    save_data_to_storage(user_id,name,tmp)

def log_load_critique_service(user_id, recipe_id, session_name, critique_list):
    name = session_name + '/' + 'explore_more_logs'
    list_ = [user_id, recipe_id , session_name, critique_list , datetime.datetime.now().timestamp()]
    tmp = list([])
    if check_if_file_exists(user_id,name):
        tmp = json.loads(load_data_from_storage(user_id,name))
        delete_file(user_id,name)
    tmp.append(list_)
    save_data_to_storage(user_id,name,tmp)

def log_session_start_service(user_id, session_name):
    name = session_name + '/' + 'start_time'
    list_ = [datetime.datetime.now().timestamp()]
    tmp = list([])
    tmp.append(list_)
    save_data_to_storage(user_id,name,tmp)

def log_session_end_service(user_id, session_name):
    name = session_name + '/' + 'end_time'
    list_ = [datetime.datetime.now().timestamp()]
    tmp = list([])
    tmp.append(list_)
    save_data_to_storage(user_id,name,tmp)

def get_nutrition_col():
    return [ 'fatContent_n', 'carbohydrateContent_n', 'sugarContent_n', 'calories_n', 'fiberContent_n', 'cholesterolContent_n', 'sodiumContent_n', 'proteinContent_n']

def get_flavour_col():
    return ['piquant_n', 'sour_n', 'salty_n', 'sweet_n', 'bitter_n', 'meaty_n']

def get_current_type_columns(current_type):
    if current_type == NUT_CRI:
        return get_nutrition_col()
    if current_type == FLA_CRI:
        return get_flavour_col()
    if current_type == NUT_FLA_CRI:
        return get_nutrition_col() + get_flavour_col()
    if current_type == ING_CRI:
        return load_ingr_mlb().classes_

def load_cuisine_object():
    return load_cuisine_object_data()