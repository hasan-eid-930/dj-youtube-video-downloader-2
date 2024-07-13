from django.urls import  path
from . import views 

urlpatterns = [
    path('maintenance',views.maintenance_page,name='maintenance' ),
    path('locked/', views.locked_page, name="locked"),
]

