from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

# Sitemaps
from django.contrib.sitemaps.views import sitemap
from app.sitemaps import *

sitemaps = {
    'static' : StaticSitemap,
    # 'categories' : CategorySitemap,
    # 'postpages' : PostpageSitemap
}

urlpatterns = [
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt/', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    # fake admin page
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    # admin page
    path('theboss/', admin.site.urls),
    path('', include('app.urls')),
    # for landing pages 
    path('land/', include('landingpages.urls')),

]
# used to serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
