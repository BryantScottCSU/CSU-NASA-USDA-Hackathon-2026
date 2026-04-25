from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/options/", views.api_options, name="api_options"),
    path("api/summary/", views.api_summary, name="api_summary"),
    path("api/countries/", views.api_countries, name="api_countries"),
    path("api/timeseries/", views.api_timeseries, name="api_timeseries"),
    path("api/hotspots/", views.api_hotspots, name="api_hotspots"),
]
