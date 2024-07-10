from django.contrib import admin
from django.urls import include, path

urlpatterns = [
     # fake admin page
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    # admin page
    path('theboss/', admin.site.urls),
    path('', include('app.urls'))

]
