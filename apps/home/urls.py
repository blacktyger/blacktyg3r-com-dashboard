# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('funding', views.funding, name='funding'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
