from django.shortcuts import render

from django.http import HttpResponse
from backend.models import StaticSensorLocations

# Create your views here.
def testdb(request):
	all = StaticSensorLocations.objects.all()
	return HttpResponse(all)
