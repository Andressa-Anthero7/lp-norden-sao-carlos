from django.shortcuts import render
from .models import Leads, Config_WhatsApp

# Create your views here.
def index(request):
	return render(request,'site/index.html')

def dashboard(request,user):
    leads = Leads.objects.all().order_by('-data_recebimento')
    return render(request, 'site/dashboard.html', {'leads': leads})