"""
URL configuration for capstone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    # user authentication urls 
    path('signup/', user_signup), #works
    path('signup_page', signup_page, name='signup_page'), # works
    path('users', view_users),
    path('login/', user_login),
    path('login_page', login_page, name= 'login_page'),
    path('api/verify', verify_email), #wrks
    path('users/delete', delete_user),
    path('api/update_user', edit_user),
    

    #meters
    path('meters/', create_product), 
    path('meters', add_meter, name = 'add_meter'),
    path('sensor_data', sensor_data),
    path('datapost', data_post, name='data_post'),
    path('user_page', user_page, name='user_page'),
    path('viewdetails/<int:product_id>/',  sensor_data_, name='sensor_data_'), # this is for admin when they press view details
    path('sensor_data_details/<int:product_id>/', sensor_data_details, name='sensor_data_details'), #this would be for user
    
    path('most_recent_sensor_data/<int:user_id>/', most_recent_sensor_data, name='most_recent_sensor_data'),
    path('products/delete/', delete_product), 
    path('products', get_product), 
    path('admin_dashboard', dashboard,name='dashboard'),
    path('add_meter', add_meter, name='add_meter'),
    path('add_meter_p', add_meter_p, name="add_meter_p"),
    path('check_anomalies/<int:user_id>/', check_anomalies, name='check_anomalies'),
]  
