from django.shortcuts import render
from django.http import HttpResponse
from backend.models import StaticSensorLocations, StaticSensorReadings, MobileSensorReadings
import json
import logging
from backend.utils.dateencoder import DateEncoder

logger = logging.getLogger(__name__)

# Create your views here.
def testdb(request):
	all = StaticSensorLocations.objects.all().values()
	# logger.info(type(all))
	return HttpResponse(json.dumps({'data': list(all)}), content_type='application/json')

def findSensorReadingsBySid(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		logger.info(params['sid'])
		# 首先检查是静态传感器还是动态传感器
		category = params['category']
		if category == 'mobile':
			responseData = MobileSensorReadings.objects.filter(sid=params['sid']).values()
		elif category == 'static':
			responseData =StaticSensorReadings.objects.filter(sid=params['sid']).values()
		return HttpResponse(json.dumps(list(responseData), cls=DateEncoder), content_type='application/json')



