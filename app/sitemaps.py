from django.contrib.sitemaps import Sitemap
from django.urls import reverse
# from .models import Tag, Post

# this for static urls 
class StaticSitemap(Sitemap):
    # return list of url names
    def items(self):
        return ['youtube']
    
    # return path for each item's url
    def location(self, item):
        return reverse(item)
    
# class CategorySitemap(Sitemap):
#     def items(self):
#         return Tag.objects.all()  
    
    
# class PostpageSitemap(Sitemap):
#     def items(self):
#         return Post.objects.all()[:100] 