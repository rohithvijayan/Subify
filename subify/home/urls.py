from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path("",views.home,name="home"),
    path("upload",views.vidUpload,name="upload"),
    path("generate/<int:id>/",views.gen_sub,name="generate"),
    path('features',views.features,name='features'),
    path('about',views.about,name='about'),
    path("https://github.com/rohithvijayan/Subify",views.github,name="github"),
    path("https://www.linkedin.com/in/rohith-vijayan-081b34227/",views.linkedin,name='linkedin'),
]