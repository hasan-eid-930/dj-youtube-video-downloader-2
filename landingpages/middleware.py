from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from .models import LandingPage

def landingpage_middleware(get_response):
    def middleware(request):
        if page_is_enabled('Maintenance'):
            print('maintenance')
            # this condition for protect against infinite loop 
            if request.path != reverse('maintenance'):
                # this for prevent redirect to maintenance when visit admin
                if '/theboss' not in request.path:
                    # prevent it from appear in staging enviromrnt
                    if settings.STAGING != 'True':
                        return redirect('maintenance')
                    
        if page_is_enabled('Staging'):
            print('staging')
            if request.path != reverse('locked'):
                if '/theboss' not in request.path:
                    # it only work in staging phase
                    if settings.STAGING == 'True':
                        if 'staging_access' not in request.session:
                            return redirect('locked')
        
        response = get_response(request)
        return response
    
    return middleware


def page_is_enabled(page_name):
    page = LandingPage.objects.filter(name=page_name).first()
    if page:
        return page.is_enabled
    else:
        return False