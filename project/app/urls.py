from django.urls import  path
from . import views 

urlpatterns = [
    path('',views.youtube,name='youtube' ),
    path('download/',views.download,name='download' ),
    path('adaptive-download/',views.adaptive_download,name='adaptive-download' ),
    # for testing some views
    path('test/',views.test,name='test' ),
    # used for show exception page
    path('exception/<str:exception>/',views.exception,name='exception' ),
]
