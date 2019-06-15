from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from backend.models import StaticSensorLocations, StaticSensorReadings, MobileSensorReadings
import json
import logging
from backend.utils.dateencoder import DateEncoder
from backend.dataprocessing.correlation import calCorrlelation

logger = logging.getLogger(__name__)

# Create your views here.
def testdb(request):
	all = StaticSensorLocations.objects.all().values()
	# logger.info(type(all))
	return HttpResponse(json.dumps({'data': list(all)}), content_type='application/json')

def findSrBySid(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		# 首先检查是静态传感器还是动态传感器
		category = params['category']
		if category == 'mobile':
			responseData = MobileSensorReadings.objects.filter(sid=params['sid']).values()
		elif category == 'static':
			responseData =StaticSensorReadings.objects.filter(sid=params['sid']).values()
		return HttpResponse(json.dumps(list(responseData), cls=DateEncoder), content_type='application/json')

def findAggMrrByTimeRange(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		cursor = connection.cursor()
		
		# Data retrieval operation - no commit required
		cursor.execute("select longitude, latitude, avg(value) as value from mobilesensorreadings where timestamp between '{0}'  and '{1}' group by concat(longitude, ',' , latitude) order by avg(value) desc".format(params['begintime'], params['endtime']))
		desc = cursor.description
		alldata = cursor.fetchall()
		data = [dict(zip([col[0] for col in desc], row)) for row in alldata]
		return HttpResponse(json.dumps(data), content_type='application/json')

def findAggSrrByTimeRange(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		cursor = connection.cursor()
		
		# Data retrieval operation - no commit required
		cursor.execute("select latitude, longitude, avg(value) as value from staticsensorreadings left join staticsensorlocations on staticsensorreadings.sid = staticsensorlocations.sid where timestamp between '{0}' and '{1}' group by staticsensorreadings.sid order by avg(value) desc;".format(params['begintime'], params['endtime']))
		desc = cursor.description
		alldata = cursor.fetchall()
		data = [dict(zip([col[0] for col in desc], row)) for row in alldata]
		return HttpResponse(json.dumps(data), content_type='application/json')

def calSensorSimilarity(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		data = calCorrlelation(params['begintime'], params['endtime'])
	return HttpResponse(json.dumps(data), content_type='application/json')
	



