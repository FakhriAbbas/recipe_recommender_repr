from django.urls import path

from . import views

urlpatterns = [
    path('<int:variation>', views.index, name='index'),
    path('pre_survey', views.pre_survey, name='pre_survey'),
    path('part_2_instructions', views.part_2_instructions, name='part_2_instructions'),
    path('preference', views.preference, name='preference'),
    path('session_1', views.session_1, name='session_1'),
    path('session_2', views.session_2, name='session_2'),
    path('session_3', views.session_3, name='session_3'),
    path('session_4', views.session_4, name='session_4'),
    path('thank_you', views.thank_you, name='thank_you'),
    path('load_critique', views.load_critique, name='load_critique'),
    path('submit_load_more', views.submit_load_more, name='submit_load_more'),
    path('submit_dislike', views.submit_dislike, name='submit_dislike'),
    path('submit_add_to_meal', views.submit_add_to_meal, name='submit_add_to_meal'),
    path('show_meal_plan', views.show_meal_plan, name='show_meal_plan'),
    path('load_search_result', views.load_search_result, name='load_search_result'),
    path('end_session', views.end_session, name='end_session'),
    path('session_reflection', views.session_reflection, name='session_reflection'),
    path('log_recipe_flavour_nutrition', views.log_recipe_flavour_nutrition, name='log_recipe_flavour_nutrition'),
    path('load_cuisine', views.load_cuisine, name='load_cuisine'),
    path('consent_form', views.consent_form, name='consent_form'),
    path('download_meal_plan', views.download_meal_plan, name='download_meal_plan'),
    path('video_tutorial', views.video_tutorial, name='video_tutorial'),

]