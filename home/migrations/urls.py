from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('manual-input/', views.manual_input, name='manual_input'),
    path('iot-input/', views.iot_input, name='iot_input'),
    path('iot-data/', views.iot_data, name='iot_data'),
    path('suggestions/', views.suggestions, name='suggestions'),
    path('contact/', views.contact, name='contact'),
    path("manual-predict-wqi/", views.manual_wqi_prediction, name="manual_predict_wqi"),
    path("iot-predict-wqi/", views.iot_wqi_prediction, name="iot_predict_wqi"),
    path("manual_predict_suggest/", views.manual_predict_suggest, name="manual_predict_suggest"),
    path("iot_predict_suggest/", views.iot_predict_suggest, name="iot_predict_suggest"),

]