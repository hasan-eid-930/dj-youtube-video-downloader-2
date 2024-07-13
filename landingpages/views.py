from django.shortcuts import redirect, render
from .forms import AccessForm
from .models import LandingPage
# Create your views here.
def maintenance_page(request):
	return render(request, "landingpages/maintenance.html") 

def locked_page(request): 
    form = AccessForm() 
    
    if request.method == "POST":
        form = AccessForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            try:
                access_code = LandingPage.objects.get(name='Staging').access_code
                if password == access_code:
                    # we add session cookie to user browser which will be active for 2 weeks
                    request.session['staging_access'] = True
                    return redirect('youtube')
            except:
                pass
          
    return render(request, 'landingpages/locked.html', {'form': form})