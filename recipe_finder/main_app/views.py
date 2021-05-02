from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from .logic import *
from .constants import *
import json

def index(request,variation):
    if 'USER_ID' not in request.session:
        request.session['USER_ID'] = get_random_string(20)

    variations = [
        [NUT_CRI, FLA_CRI, NUT_FLA_CRI, ING_CRI],
        [NUT_CRI, FLA_CRI, ING_CRI, NUT_FLA_CRI],
        [NUT_CRI, NUT_FLA_CRI, FLA_CRI, ING_CRI],
        [NUT_CRI, NUT_FLA_CRI, ING_CRI, FLA_CRI],
        [NUT_CRI, ING_CRI, FLA_CRI, NUT_FLA_CRI],
        [NUT_CRI, ING_CRI, NUT_FLA_CRI, FLA_CRI],
        [FLA_CRI, NUT_CRI, NUT_FLA_CRI, ING_CRI],
        [FLA_CRI, NUT_CRI, ING_CRI, NUT_FLA_CRI],
        [FLA_CRI, NUT_FLA_CRI, NUT_CRI, ING_CRI],
        [FLA_CRI, NUT_FLA_CRI, ING_CRI, NUT_CRI],
        [FLA_CRI, ING_CRI, NUT_CRI, NUT_FLA_CRI],
        [FLA_CRI, ING_CRI, ING_CRI, NUT_CRI],
        [NUT_FLA_CRI, NUT_CRI, FLA_CRI, ING_CRI],
        [NUT_FLA_CRI, NUT_CRI, ING_CRI, FLA_CRI],
        [NUT_FLA_CRI, FLA_CRI, ING_CRI, NUT_CRI],
        [NUT_FLA_CRI, FLA_CRI, ING_CRI, NUT_CRI],
        [NUT_FLA_CRI, ING_CRI, NUT_CRI, FLA_CRI],
        [NUT_FLA_CRI, NUT_CRI, FLA_CRI, NUT_CRI],
        [ING_CRI, NUT_CRI, FLA_CRI, NUT_FLA_CRI],
        [ING_CRI, NUT_CRI, NUT_FLA_CRI, FLA_CRI],
        [ING_CRI, FLA_CRI, NUT_CRI, NUT_FLA_CRI],
        [ING_CRI, FLA_CRI, NUT_FLA_CRI, NUT_CRI],
        [ING_CRI, NUT_FLA_CRI, NUT_CRI, FLA_CRI],
        [ING_CRI, NUT_FLA_CRI, FLA_CRI, NUT_CRI]
    ]

    save_study_variables(get_user_id(request))
    add_to_study_settings( get_user_id(request), 'seq', variations[15])
    return render(request, 'main_app/index.html')

def pre_survey(request):
    if(request.is_ajax()):
        response = save_pre_survey_process(request)
        return HttpResponse(json.dumps(response), content_type="application/json")
    return render(request, 'main_app/pre_survey.html', context={})

def part_2_instructions(request):
    return render(request, 'main_app/part_2_instructions.html')

def preference(request):
    if(request.is_ajax()):
        response = save_preference_process(request)
        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        context = {
            'cuisine_list' : get_cuisine_list(),
            'course_list' : get_course_list()
        }
        return render(request, 'main_app/preference.html', context = context)

def session_1(request):
    variations = get_study_settings_value(get_user_id(request), 'seq')
    add_to_study_settings(get_user_id(request), 'current_type', variations[0])
    log_session_start_logic(request,'session_1')
    return init_recommendation(request, current_session='session_1', current_type=variations[0])

def session_2(request):
    variations = get_study_settings_value(get_user_id(request), 'seq')
    add_to_study_settings(get_user_id(request), 'current_type', variations[1])
    log_session_start_logic(request,'session_2')
    return init_recommendation(request, current_session='session_2', current_type=variations[1])

def session_3(request):
    variations = get_study_settings_value(get_user_id(request), 'seq')
    add_to_study_settings(get_user_id(request), 'current_type', variations[2])
    log_session_start_logic(request,'session_3')
    return init_recommendation(request, current_session='session_3', current_type=variations[2])

def session_4(request):
    variations = get_study_settings_value(get_user_id(request), 'seq')
    add_to_study_settings(get_user_id(request), 'current_type', variations[3])
    log_session_start_logic(request,'session_4')
    return init_recommendation(request, current_session='session_4', current_type=variations[3])

def load_critique(request):
    if request.is_ajax():
        response = {}
        recipe_id, recipe_name, critique_list = get_critique_for_recipe( request )
        template = get_template("main_app/includes/critique_list.html")
        response['critique-content'] = template.render({"critiques" : critique_list , 'recipe_id' : recipe_id, 'recipe_name' : recipe_name }, request)
        response['status'] = 1
        log_load_critique_logic(request,critique_list)
        return HttpResponse(json.dumps(response), content_type="application/json")

def submit_load_more(request):
    if request.is_ajax():
        response = {}
        json_result, result_df  = load_more_critique_recommender(request)
        search_space = load_search_space(get_user_id(request))
        current_type = get_study_settings_value(get_user_id(request),'current_type')
        result_json = generate_critique_diverstiy(result_df, search_space,current_type)
        template = get_template("main_app/includes/recipe_list_critique.html")
        response['list-content'] = template.render({'items': result_json }, request)
        template = get_template("main_app/includes/critique_header.html")
        context = {}
        session_counter = get_study_settings_value(get_user_id(request), 'session_counter')
        context['session_progress'] = get_exploration_progress_service(session_counter)
        context['meal_plan_progress'] = get_meal_plan_progress(get_user_id(request))
        context['is_end_session'] = is_end_session_condition_has_met(request)
        response['direction-content'] = template.render(context,request)
        template = get_template("main_app/includes/empty.html") # TODO based on progress
        response['button-content'] = template.render({},request)

        current_session = get_study_settings_value(get_user_id(request), 'current_session')

        session_counter = get_study_settings_value(get_user_id(request), 'session_counter')
        add_to_study_settings(get_user_id(request), 'session_counter' , session_counter + 1)
        add_to_study_settings(get_user_id(request), 'current_counter', session_counter + 1)
        session_counter = get_study_settings_value(get_user_id(request), 'session_counter')

        direction, column_name, recipe_name, recipe_id = extract_critique_data(request)
        save_user_exploration_history(get_user_id(request),recipe_name,column_name,direction)
        save_data_to_storage(get_user_id(request),
                         current_session  + '/' + str(session_counter),
                         result_json )

        template = get_template("main_app/includes/search_history.html")
        search_items = load_search_history_summary(get_user_id(request))
        response['search-history-content'] = template.render({'search_items' : search_items},request)
        response['is_end_session'] = is_end_session_condition_has_met(request)
        response['status'] = 1

        return HttpResponse(json.dumps(response), content_type="application/json")

def submit_dislike(request):
    response = {}
    recipe_name = request.POST.get("recipe_name", "")
    user_id = get_user_id(request)
    if request.POST.get("value", "") == '0':
        print('maybe')
        remove_dislike_recipe(recipe_name,user_id)
    elif request.POST.get("value", "") == '1':
        add_dislike_recipe(recipe_name,user_id)
    response['status'] = 1
    return HttpResponse(json.dumps(response), content_type="application/json")

def submit_add_to_meal(request):
    response = {}
    recipe_name = request.POST.get("recipe_name", "")
    user_id = get_user_id(request)
    counter = 0
    if request.POST.get("value", "") == '0':
        counter = remove_recipe_add_to_meal_plan(recipe_name,user_id)
    elif request.POST.get("value", "") == '1':
        counter = add_recipe_add_to_meal_plan(recipe_name,user_id)
    response['status'] = 1
    response['meal_plan_progress'] = get_meal_plan_progress(get_user_id(request))
    response['is_end_session'] = is_end_session_condition_has_met(request)
    return HttpResponse(json.dumps(response), content_type="application/json")

def show_meal_plan(request):
    if request.is_ajax():
        response = {}
        template = get_template("main_app/includes/meal_plan_modal.html")
        items = get_meal_plan_recipes(request)
        response['model_template'] = template.render({
                                                    'items': items
                                                    },
                                                    request)
        response['status'] = 1
        return HttpResponse(json.dumps(response), content_type="application/json")

def load_search_result(request):
    if request.is_ajax():
        response = {}
        items = load_search_history(request)
        study_type = get_study_settings_value(get_user_id(request), 'current_type')
        template = get_template("main_app/includes/recipe_list_critique.html")
        response['list-content'] = template.render({'items': items }, request)
        response['status'] = 1
        return HttpResponse(json.dumps(response), content_type="application/json")

def end_session(request):
    current_session = get_study_settings_value(get_user_id(request),'current_session')
    log_session_end_logic(request)
    if current_session == 'session_1':
        context = {}
        context['session_number'] = 1
        return render(request, 'main_app/critique_reflection.html', context = context)
    if current_session == 'session_2':
        context = {}
        context['session_number'] = 2
        return render(request, 'main_app/critique_reflection.html', context = context)
    if current_session == 'session_3':
        context = {}
        context['session_number'] = 3
        return render(request, 'main_app/critique_reflection.html', context = context)
    if current_session == 'session_4':
        context = {}
        context['session_number'] = 4
        return render(request, 'main_app/critique_reflection.html', context = context)

def session_reflection(request):
    if(request.is_ajax()):
        response = save_reflection_process(request)
        return HttpResponse(json.dumps(response), content_type="application/json")

def thank_you(request):
    return render(request, 'main_app/thank_you.html')

def log_recipe_flavour_nutrition(request):
    log_recipe_flavour_nutrition_logic(request)
    response = {}
    response['status'] = 1
    return HttpResponse(json.dumps(response), content_type="application/json")

def load_cuisine(request):
    if request.is_ajax():
        response = {}
        response['status'] = 1
        response['data'] = load_cuisine_object()
        return HttpResponse(json.dumps(response), content_type="application/json")