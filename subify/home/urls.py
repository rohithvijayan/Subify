from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path("",views.home,name="home"),
    path("upload",views.vidUpload,name="upload"),
    path("generate/<int:id>/",views.gen_sub,name="generate"),
    path('features',views.features,name='features'),
]