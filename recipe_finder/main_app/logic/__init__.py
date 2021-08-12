import random, string
from ..services import *
from django.urls import reverse
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from django.shortcuts import render
import math
from ..constants import *
from scipy.sparse import csr_matrix
import itertools
import scipy
import operator
import datetime

def save_pre_survey_process(request):
    response = {}
    try:
        # read responses
        q1 = request.POST.get("q1", "")
        q2 = request.POST.getlist("q2[]")
        q2_text = request.POST.get("q2_text", "")
        q3 = request.POST.get("q3", "")
        q4 = request.POST.getlist("q4[]")
        q4_text = request.POST.get("q4_text", "")
        q5 = request.POST.get("q5", "")
        q6 = request.POST.get("q6", "")
        q7 = request.POST.get("q7", "")
        q8 = request.POST.get("q8", "")
        q9 = request.POST.get("q9", "")

        # prepare data
        data = {}
        data['q1'] = q1
        data['q2'] = q2
        data['q2_text'] = q2_text
        data['q3'] = q3
        data['q4'] = q4
        data['q4_text'] = q4_text
        data['q5'] = q5
        data['q6'] = q6
        data['q7'] = q7
        data['q8'] = q8
        data['q9'] = q9

        # save data
        save_data_to_storage(request.session.get('USER_ID'), page_name='pre_survey' , data = data)

        # prepare success response
        response['status'] = 1
        response['redirect-url'] = reverse('part_2_instructions')
        return response
    except Exception as e:
        # prepare failure response
        return get_failure_response(exception_msg = e.strerror)

def save_preference_process(request):
    response = {}
    try:
        # read responses
        q1 = request.POST.getlist("q1[]")
        q3 = request.POST.getlist("q3[]")

        # prepare data
        data = {}
        data['q1'] = q1
        data['q3'] = q3

        # save data
        save_data_to_storage(request.session.get('USER_ID') , page_name='preference', data = data)

        # prepare success response
        response['status'] = 1
        response['redirect-url'] = reverse('session_1')
        return response
    except Exception as e:
        # prepare failure response
        return get_failure_response(exception_msg = e.strerror)

def save_reflection_process(request):
    response = {}
    try:
        # read responses
        q1 = request.POST.get("q1", "")
        q2 = request.POST.get("q2", "")
        q3 = request.POST.get("q3", "")
        q4 = request.POST.get("q4", "")
        q5 = request.POST.get("q5", "")
        q6 = request.POST.get("q6", "")
        q7 = request.POST.get("q7", "")

        # prepare data
        data = {}
        data['q1'] = q1
        data['q2'] = q2
        data['q3'] = q3
        data['q4'] = q4
        data['q5'] = q5
        data['q6'] = q6
        data['q7'] = q7
        current_session = get_study_settings_value(get_user_id(request),'current_session')

        # save data
        save_data_to_storage(request.session.get('USER_ID') + '/' + current_session , page_name='reflection', data = data)

        # prepare success response
        response['status'] = 1
        if current_session == 'session_1':
            response['redirect-url'] = reverse('session_2')
        elif current_session == 'session_2':
            response['redirect-url'] = reverse('session_3')
        elif current_session == 'session_3':
            response['redirect-url'] = reverse('session_4')
        else:
            response['redirect-url'] = reverse('thank_you')
        return response
    except Exception as e:
        # prepare failure response
        return get_failure_response(exception_msg = e.strerror)

def init_recommendation(request, current_session, current_type):
    context = {}
    add_to_study_settings(get_user_id(request), 'current_session' , current_session)
    add_to_study_settings(get_user_id(request), 'session_counter' , 1)
    add_to_study_settings(get_user_id(request), 'current_counter' , 1)
    if request.is_ajax():
        pass
    else:
        result_json, result_df, search_space_df = init_critique_recommender(request,current_type)
        distance_tree = get_distance_tree(request,current_type,current_session)
        result_json = generate_critique_diverstiy(result_df, search_space_df, current_type, distance_tree)

        session_counter = get_study_settings_value(get_user_id(request), 'session_counter')
        current_session = get_study_settings_value(get_user_id(request), 'current_session')
        save_data_to_storage(get_user_id(request),
                             current_session  + '/' + str(session_counter),
                             result_json )
        save_user_exploration_history(get_user_id(request),'','','')

        context['items'] = result_json
        context['session_progress'] = get_exploration_progress_service(session_counter)
        context['meal_plan_progress'] = get_meal_plan_progress(get_user_id(request))
        context['search_items'] = load_search_history_summary(get_user_id(request))
        context['is_end_session'] = is_end_session_condition_has_met(request)
        context['session_number'] = current_session[-1]

        return render(request, 'main_app/critique_recommender_parent.html', context = context)

def init_critique_recommender(request,current_type):
    user_id = request.session.get('USER_ID')
    # load preference
    cuisine_list , course_list , _ = get_preference(request.session.get('USER_ID'))
    # generate recommendation
    recommended_recipes, search_space_df = generate_recommendation(cuisine_list, course_list, user_id, current_type, N = 10)
    save_search_space(user_id, search_space_df)
    json_result = json.loads(recommended_recipes.to_json(orient='records'))
    return json_result, recommended_recipes, search_space_df

def generate_recommendation(cuisine_list, course_list, user_id, current_type, N = 10):
    subset_df = load_cuisine_df(cuisine_list,user_id)
    repr_col = get_current_type_columns(current_type)
    centroid = subset_df[repr_col].mean()
    distance_ = cdist([centroid], subset_df[repr_col], metric='euclidean')[0]
    distance_ = (distance_ - min(distance_)) / (max(distance_) - min(distance_))
    subset_df['dist_'] = distance_ / 2
    if len(course_list) != 0:
        subset_df['course_score'] = (np.sum(subset_df[course_list].values, axis=1) / len(course_list)) / 2
    else:
        subset_df['course_score'] = 0
    subset_df['score'] = subset_df['dist_'] + subset_df['course_score']
    top_n_recipe = subset_df.sort_values(by='score', ascending=False)[0:N*10][get_relevant_columns()]
    top_n_recipe.drop_duplicates(subset=['id'], inplace=True)

    # add dislike and meal values
    top_n_recipe = top_n_recipe[0:N]
    top_n_recipe['dislike'] = [1 if v in load_dislike_recipe_list(user_id) else 0 for v in top_n_recipe.id.values]
    top_n_recipe['meal_plan'] = [1 if v in load_meal_plan_recipe_list(user_id) else 0 for v in top_n_recipe.id.values]
    return top_n_recipe, subset_df

def get_cat(cal, average):
    if cal is None:
        return None
    if cal < average:
        return 0
    elif cal >= average:
        return 1

def similarity(i_index, j_index, metric_, matrix_):
    return scipy.spatial.distance.cdist( matrix_[i_index].todense() , matrix_[j_index].todense() , metric = metric_)

def intra_list_similarity(ids , metric_, matrix_, opposite = False):
    list_ = itertools.combinations(ids,2)
    dist_sum = 0
    i = 0
    for pairs in list_:
        dist = similarity(pairs[0], pairs[1], metric_, matrix_)
        if opposite == False:
            dist = 1 - dist
        if math.isnan(dist):
            continue
        dist_sum = dist + dist_sum
        i = i + 1
    length = len(ids)
    factor = length*(length - 1)/2
    return dist_sum/i

def transform_to_categorical(df,critique_columns):
    for col in critique_columns:
        values = df[col].values
        avg = pd.Series(values).mean(skipna=True)
        tmp_list = list()
        for v in values:
            tmp_list.append( get_cat(v, average=avg) )
        df.loc[ : , 'c_' + col] = tmp_list
    return df

def get_diverse_recipes(data_df, distance_tree, s_index, repr_columns):
    length = data_df.shape[0]
    recipe_list = list()
    recipe_list.append(s_index)
    for i in range(0, 10):
        print(data_df[data_df.index == s_index][repr_columns])
        dist, idx = distance_tree.query(data_df[data_df.index == s_index][repr_columns],k=length)
        ordered_list = idx[0]
        for s_i in range(1, len(ordered_list)):
            s_index = ordered_list[s_i * -1]
            if s_index not in recipe_list:
                recipe_list.append(s_index)
                break
    return recipe_list

def transform_recipe_to_categorical(target_recipe_df, farthest_recipes_df, categorical_col):
    for categorical in categorical_col:
        v = farthest_recipes_df[categorical].values
        avg = pd.Series(v).mean(skipna=True)
        target_recipe_df[categorical] = get_cat(target_recipe_df[categorical] , avg)
    return target_recipe_df

def generate_critique_diverstiy(result_df, search_space_df, current_type, distance_tree):
    flavor_col =  get_flavour_col()
    nutrition_col = get_nutrition_col()

    critique_columns = flavor_col + nutrition_col
    result_df['critique'] = None
    result_df['critique'].astype('object')

    # result = {}
    top_n_recipe = transform_to_categorical(result_df, critique_columns)
    categorical_col = [('c_' + str(col)) for col in critique_columns]
    representation_columns = get_current_type_columns(current_type)
    data_df = search_space_df[representation_columns]
    for index, row in top_n_recipe.iterrows():
        print('index ==========>', index)
        df_critique = pd.DataFrame(columns=['column_name', 'display_name', 'direction'])
        farthest_recipes_idx_list = get_diverse_recipes(data_df, distance_tree, index, representation_columns)
        diverse_df = search_space_df[search_space_df.index.isin(farthest_recipes_idx_list)]
        diverse_df = transform_to_categorical(diverse_df, critique_columns)
        target_recipe_df = row
        col_counter = [0] * len(critique_columns)
        for f_index, f_row in diverse_df.iterrows():
            for col_idx, col in enumerate(categorical_col):
                if f_row[col] == 1:
                    col_counter[col_idx] = col_counter[col_idx] + 1
        # percentage
        col_counter_one = [ round(x/diverse_df.shape[0],2) for x in col_counter]
        col_counter_zero = [ round(1 - x,2) for x in col_counter_one]
        transformed_recipe = transform_recipe_to_categorical(target_recipe_df, diverse_df, categorical_col)
        r_vector = transformed_recipe[categorical_col]
        r_inv_vector = [ round(1 - x,2) if x is not None else None for x in r_vector]
        top_feature_n = 5

        # result[target_recipe_df['recipeName']] = {}
        # result[target_recipe_df['recipeName']]['id'] = row['id']
        for v_index, value in enumerate(r_inv_vector):
            has_more = 0
            has_less = 0
            if value == 0:
                if v_index in np.argsort(col_counter_zero)[0:top_feature_n]:
                    # result[target_recipe_df['recipeName']][critique_columns[v_index]] = 'low'
                    has_less = 1
            elif value == 1:
                if v_index in np.argsort(col_counter_one)[0:top_feature_n]:
                    # result[target_recipe_df['recipeName']][critique_columns[v_index]] = 'High'
                    has_more = 1
            elif (has_less == 0) and (has_more == 0):
                continue
            new_row = {'column_name': critique_columns[v_index], 'display_name': get_display_name(critique_columns[v_index]),
                       'More': has_more, 'Less': has_less}
            df_critique = df_critique.append(new_row, ignore_index=True)

        result_df.at[index, 'critique'] = json.loads(df_critique.to_json(orient='records'))
    json_result = json.loads(result_df.to_json(orient='records'))
    return json_result

def generate_critique_diverstiy_random(result_df, search_space_df, current_type):

    flavor_col =  get_flavour_col()
    nutrition_col = get_nutrition_col()

    columns = flavor_col + nutrition_col
    result_df['critique'] = None
    result_df['critique'].astype('object')

    result = {}
    subset_size = search_space_df.shape[0]
    data = search_space_df[columns]
    # convert data to 0/1 based on average
    for col in columns:
        average = data[col].mean()
        values = data[col].values
        data.loc[ values > average , col ] = 1
        data.loc[ values <= average, col] = 0

    div_data = search_space_df[ get_current_type_columns(current_type) ]

    for t in range(0,10):
        # create the random list
        randomlist = []
        for i in range(0, int(10) ):
            n = random.randint(0,subset_size - 1)
            randomlist.append( n )
        ils = intra_list_similarity( randomlist, 'jaccard' , csr_matrix(div_data) , opposite=False)
        result[t] = (ils, randomlist)
    col_counter = [0] * len(columns)

    # get the index of the highest ils score
    idx = max(result.items(), key=operator.itemgetter(1))[0]
    for row in result[idx][1]:
        for col_idx, col in enumerate(data.iloc[row]):
            if col == 1:
                col_counter[col_idx] = col_counter[col_idx] + 1
    col_counter_one = [ round(x/len(result[1][1]),2) for x in col_counter]
    col_counter_zero = [ round(1 - x,2) for x in col_counter_one]

    critique_result = {}
    for index, row in result_df.iterrows():
        df_critique = pd.DataFrame(columns=['column_name', 'display_name', 'direction'])
        r_vector = data[data.index == index].values[0]
        r_inv_vector = [round(1 - x, 2) for x in r_vector]

        top_feature_n = 8
        critique_result[row['recipeName']] = {}
        critique_result[row['recipeName']]['id'] = row['id']
        for v_index, value in enumerate(r_inv_vector):
            has_more = 0
            has_less = 0
            if value == 0:
                if v_index in np.argsort(col_counter_zero)[0:top_feature_n]:
                    critique_result[row['recipeName']][columns[v_index]] = 'low'
                    has_less = 1
            elif value == 1:
                if v_index in np.argsort(col_counter_one)[0:top_feature_n]:
                    critique_result[row['recipeName']][columns[v_index]] = 'High'
                    has_more = 1

            if (has_more == 0) and (has_less == 0):
                continue

            new_row = {'column_name': columns[v_index], 'display_name': get_display_name(columns[v_index]), 'More': has_more, 'Less': has_less}
            df_critique = df_critique.append(new_row, ignore_index=True)
        result_df.at[index, 'critique'] = json.loads(df_critique.to_json(orient='records'))
    json_result = json.loads(result_df.to_json(orient='records'))
    return json_result

def get_critique_for_recipe(request):
    results_json = load_current_results(request)
    recipe_id = request.POST.get('recipe_id')
    for recipe in results_json:
        if recipe['id'] == recipe_id:
            return recipe_id, recipe['recipeName'], recipe['critique']
    return None, None, None

def load_current_results(request):
    user_id = get_user_id(request)
    session_name = get_study_settings_value(user_id, 'current_session')
    session_counter = get_study_settings_value(user_id, 'current_counter')

    results_json = json.loads(load_data_from_storage(user_id, str(session_name) + '/' + str(session_counter)))

    dislike_result = load_dislike_recipe_list(user_id)
    meal_plan_result = load_meal_plan_recipe_list(user_id)
    for recipe in results_json:
        if recipe['id'] in dislike_result:
            recipe['dislike'] = 1
        else:
            recipe['dislike'] = 0
        if recipe['id'] in meal_plan_result:
            recipe['meal_plan'] = 1
        else:
            recipe['meal_plan'] = 0

    return results_json

def load_more_critique_recommender(request):
    direction, column_name, recipe_name, recipe_id = extract_critique_data(request)
    current_type = get_study_settings_value(get_user_id(request), 'current_type')
    user_id = request.session.get('USER_ID')
    # load preference
    cuisine_list , course_list , _ = get_preference(request.session.get('USER_ID'))
    # generate recommendation
    recommended_recipes = load_more_recipes(cuisine_list, course_list, direction, column_name, recipe_name, recipe_id, current_type, user_id, N = 10)
    json_result = json.loads(recommended_recipes.to_json(orient='records'))
    return json_result, recommended_recipes

def load_more_recipes(cuisine_list, course_list, direction, column_name, recipe_name, recipe_id, current_type, user_id, N = 10):
    search_space_df = load_search_space(user_id)
    dis_like_list = load_dislike_recipe_list(user_id)
    threshold = search_space_df[search_space_df['id'] == recipe_id][column_name].values[0]
    search_space_df = search_space_df[~search_space_df['id'].isin(dis_like_list)] # takes time
    if direction == 'More':
        tmp_df = search_space_df[ search_space_df[column_name] > threshold ]
    elif direction == 'Less':
        tmp_df = search_space_df[search_space_df[column_name] < threshold]
    current_type_col = get_current_type_columns(current_type)
    centroid = tmp_df[ tmp_df['id'] == recipe_id ][current_type_col].mean()
    distance_ = cdist([centroid], tmp_df[current_type_col], metric='euclidean')[0] # takes time
    distance_ = (distance_ - min(distance_)) / (max(distance_) - min(distance_))
    tmp_df.loc[:, 'dist_'] = distance_ / 2
    if len(course_list) != 0:
        tmp_df.loc[ : , 'course_score'] = (np.sum(tmp_df[course_list].values, axis=1) / len(course_list)) / 2
    else:
        tmp_df.loc[ : , 'course_score'] = 0.0
    tmp_df.loc[ : , 'score'] = tmp_df['dist_'] + tmp_df['course_score']

    top_n_recipe = tmp_df.sort_values(by='score', ascending=False)[0:N*10][get_relevant_columns()]

    top_n_recipe.drop_duplicates(subset=['id'], inplace=True)
    top_n_recipe = top_n_recipe[0:N]

    # add dislike and meal values
    top_n_recipe['dislike'] = [1 if v in load_dislike_recipe_list(user_id) else 0 for v in top_n_recipe.id.values]
    top_n_recipe['meal_plan'] = [1 if v in load_meal_plan_recipe_list(user_id) else 0 for v in top_n_recipe.id.values]
    return top_n_recipe

def get_exploration_progress(counter):
    return get_exploration_progress_service(counter)

def is_end_session_condition_has_met(request):
    user_id = get_user_id(request)
    counter = get_study_settings_value(user_id, 'session_counter')
    expl_progress = get_exploration_progress(counter)
    meal_plan_progress = get_meal_plan_progress(user_id)

    if expl_progress > 99 and meal_plan_progress > 99:
        return 1
    else:
        return 0

def remove_dislike_recipe(recipe_name, user_id):
    recipe_list = load_dislike_recipe_list(user_id)
    session_name = get_study_settings_value(user_id, 'current_session')
    if recipe_name in recipe_list:
        recipe_list.remove(recipe_name)
        log_dislike_transaction(recipe_name, user_id, 'remove', session_name)
        save_dislike_recipe_list(recipe_list, user_id)

def add_dislike_recipe(recipe_name, user_id):
    recipe_list = load_dislike_recipe_list(user_id)
    session_name = get_study_settings_value(user_id, 'current_session')
    if recipe_name not in recipe_list:
        recipe_list.append(recipe_name)
        log_dislike_transaction(recipe_name,user_id,'add',session_name)
        save_dislike_recipe_list(recipe_list, user_id)

def remove_recipe_add_to_meal_plan(recipe_name,user_id):
    recipe_list = load_meal_plan_recipe_list(user_id)
    session_name = get_study_settings_value(user_id, 'current_session')
    if recipe_name in recipe_list:
        recipe_list.remove(recipe_name)
        log_meal_plan_transaction(recipe_name, user_id, 'remove', session_name)
        save_meal_plan_recipe_list(recipe_list, user_id)
    return len(recipe_list)

def add_recipe_add_to_meal_plan(recipe_name,user_id):
    recipe_list = load_meal_plan_recipe_list(user_id)
    session_name = get_study_settings_value(user_id, 'current_session')
    if recipe_name not in recipe_list:
        recipe_list.append(recipe_name)
        log_meal_plan_transaction(recipe_name, user_id, 'add',session_name)
        save_meal_plan_recipe_list(recipe_list, user_id)
    return len(recipe_list)

def get_meal_plan_progress(user_id):
    recipe_list = load_meal_plan_recipe_list(user_id)
    return get_meal_plan_progress_service(len(recipe_list))

def get_meal_plan_recipes(request):
    user_id = get_user_id(request)
    recipe_list = load_meal_plan_recipe_list(user_id)
    search_space_df = load_search_space(user_id)
    result_df = search_space_df.loc[search_space_df['id'].isin(recipe_list)][get_relevant_columns()]
    return json.loads(result_df.to_json(orient='records'))

def save_user_exploration_history(user_id, recipe_name, column_name, direction):
    session_name = get_study_settings_value(user_id, 'current_session')
    dict_ = load_user_exploration_history_service(session_name, user_id)
    session_counter = get_study_settings_value(user_id, 'session_counter')
    dict_[session_counter] = dict()
    dict_[session_counter]['user_id'] = user_id
    dict_[session_counter]['active'] = 0
    dict_[session_counter]['timestampe'] = datetime.datetime.now().timestamp()
    dict_[session_counter]['session_type'] = get_study_settings_value(user_id, 'current_type')
    if recipe_name:
        dict_[session_counter]['recipe_name'] = recipe_name
        dict_[session_counter]['column_name'] = column_name
        dict_[session_counter]['column_name_display'] = get_display_name(column_name)
        dict_[session_counter]['direction'] = direction
    else:
        dict_[session_counter]['recipe_name'] = 'Nothing selected'
        dict_[session_counter]['column_name'] = 'Nothing selected'
        dict_[session_counter]['direction'] = ''
        dict_[session_counter]['column_name_display'] = 'Nothing selected'
    dict_[session_counter]['session_name'] = session_name
    save_user_exploration_history_service(session_name, dict_, user_id)

def load_search_history_summary(user_id):
    session_name = get_study_settings_value(user_id, 'current_session')
    current_counter = get_study_settings_value(user_id,'current_counter')
    items = load_user_exploration_history_service(session_name, user_id)
    items[str(current_counter)]['active'] = 1
    return items

# load specific list from the history
def load_search_history(request):
    user_id = get_user_id(request)
    search_number = request.POST.get('search_key')
    add_to_study_settings(user_id,'current_counter', int(search_number))
    current_session = get_study_settings_value(user_id, 'current_session')
    results = json.loads(load_data_from_storage(user_id, current_session + '/' + str(search_number)))

    dislike_result = load_dislike_recipe_list(user_id)
    meal_plan_result = load_meal_plan_recipe_list(user_id)
    for recipe in results:
        if recipe['id'] in dislike_result:
            recipe['dislike'] = 1
        else:
            recipe['dislike'] = 0
        if recipe['id'] in meal_plan_result:
            recipe['meal_plan'] = 1
        else:
            recipe['meal_plan'] = 0

    log_loading_search_result(user_id, search_number, current_session)

    return results

def log_recipe_flavour_nutrition_logic(request):
    is_expanded = request.POST.get("is_expanded", "")
    type = request.POST.get("type", "")
    recipe_id = request.POST.get("recipe_id", "")

    user_id = get_user_id(request)
    current_session = get_study_settings_value(user_id, 'current_session')
    log_recipe_flavour_nutrition_service(type, recipe_id, is_expanded, user_id, current_session)

def log_load_critique_logic(request, critique_list):
    user_id = get_user_id(request)
    recipe_id = request.POST.get('recipe_id')
    current_session = get_study_settings_value(user_id, 'current_session')
    log_load_critique_service(user_id, recipe_id, current_session,critique_list)

def log_session_start_logic(request, current_session):
    user_id = get_user_id(request)
    log_session_start_service(user_id,current_session)

def log_session_end_logic(request):
    user_id = get_user_id(request)
    current_session = get_study_settings_value(user_id, 'current_session')
    log_session_end_service(user_id,current_session)
