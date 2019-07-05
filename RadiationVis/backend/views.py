from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from backend.models import StaticSensorLocations, StaticSensorReadings, MobileSensorReadings
import json
import logging
from backend.utils.dateencoder import DateEncoder
from backend.dataprocessing.correlation import calCorrlelation
# from backend.dataprocessing.cluster import calCluster
from backend.dataprocessing.cluster_dtw import TestDTW
import time, datetime
from backend.dataprocessing.gridmap import add_grid_info, idw, getLastPointsInGrid

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

def findMrrByTimeRange(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		cursor = connection.cursor()
		
		# Data retrieval operation - no commit required
		cursor.execute("select longitude, latitude, value from mobilesensorreadings where timestamp > '{0}'  and timestamp < '{1}'".format(params['begintime'], params['endtime']))
		desc = cursor.description
		alldata = cursor.fetchall()
		data = [dict(zip([col[0] for col in desc], row)) for row in alldata]
		return HttpResponse(json.dumps(data), content_type='application/json')

def findMrrByTimeRangeAndSid(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		cursor = connection.cursor()
		
		# Data retrieval operation - no commit required
		cursor.execute("select longitude, latitude, value from mobilesensorreadings where timestamp > '{0}'  and timestamp < '{1}' and sid = {2}".format(params['begintime'], params['endtime'], params['sid']))
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

def findSrrByTimeRange(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		cursor = connection.cursor()
		
		# Data retrieval operation - no commit required
		cursor.execute("select latitude, longitude, value from staticsensorreadings left join staticsensorlocations on staticsensorreadings.sid = staticsensorlocations.sid where timestamp between '{0}' and '{1}'".format(params['begintime'], params['endtime']))
		desc = cursor.description
		alldata = cursor.fetchall()
		data = [dict(zip([col[0] for col in desc], row)) for row in alldata]
		return HttpResponse(json.dumps(data), content_type='application/json')

def calSensorSimilarity(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		data = calCorrlelation(params['begintime'], params['endtime'])
	return HttpResponse(json.dumps(data), content_type='application/json')

# def calSensorClusters(request):
# 	if request.method == 'POST':
# 		params = json.loads(request.body)
# 		data = calCluster(params['begintime'], params['endtime'])
# 	return HttpResponse(json.dumps(data), content_type='application/json')

def calSensorClusters(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		data = TestDTW.test_cluster_effect_agg2(params['begintime'], params['endtime'])
	return HttpResponse(json.dumps(data), content_type='application/json')

def calTimeSeries(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		begintime_str = params['begintime']
		endtime_str = params['endtime']
		begin_date = datetime.datetime.strptime(begintime_str, '%Y-%m-%d %H:%M:%S')
		end_date = datetime.datetime.strptime(endtime_str, '%Y-%m-%d %H:%M:%S')
		begin_timestamp = time.mktime(begin_date.timetuple())
		end_timestamp = time.mktime(end_date.timetuple())
		
		static_data = None
		mobile_data = None
		cursor = connection.cursor()

		# 如果时间间隔超过三小时，按小时聚合，否则按分钟聚合
		if (end_timestamp - begin_timestamp) > 12 * 3600:
			# 查询动态数据
			cursor.execute("select concat(DATE_FORMAT(timestamp, '%Y-%m-%d %H'),':00:00') as time, avg(value) as avg, std(value)/sqrt(count(*)) as standarderror from mobilesensorreadings where timestamp >= '{0}' and timestamp < '{1}' group by DATE_FORMAT(timestamp, '%Y-%m-%d %H')".format(begintime_str, endtime_str))
			
			desc = cursor.description
			alldata = cursor.fetchall()
			mobile_data = [dict(zip([col[0] for col in desc], row)) for row in alldata]

			# 查询静态数据
			cursor.execute("select concat(DATE_FORMAT(timestamp, '%Y-%m-%d %H'),':00:00') as time, avg(value) as avg, std(value)/sqrt(count(*)) as standarderror from staticsensorreadings where timestamp >= '{0}' and timestamp < '{1}' group by DATE_FORMAT(timestamp, '%Y-%m-%d %H')".format(begintime_str, endtime_str))
			
			desc = cursor.description
			alldata = cursor.fetchall()
			static_data = [dict(zip([col[0] for col in desc], row)) for row in alldata]
		else:
			# 查询动态数据
			cursor.execute("select concat(DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i'),':00') as time, avg(value) as avg, std(value)/sqrt(count(*)) as standarderror from mobilesensorreadings where timestamp >= '{0}' and timestamp < '{1}' group by DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i')".format(begintime_str, endtime_str))
			desc = cursor.description
			alldata = cursor.fetchall()
			mobile_data = [dict(zip([col[0] for col in desc], row)) for row in alldata]

			# 查询静态数据
			cursor.execute("select concat(DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i'),':00') as time, avg(value) as avg, std(value)/sqrt(count(*)) as standarderror from staticsensorreadings where timestamp >= '{0}' and timestamp < '{1}' group by DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i')".format(begintime_str, endtime_str))
			desc = cursor.description
			alldata = cursor.fetchall()
			static_data = [dict(zip([col[0] for col in desc], row)) for row in alldata]

		data = {'mobile': mobile_data, 'static': static_data}

		return HttpResponse(json.dumps(data), content_type='application/json')

def calTimeSeriesBySid(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		category = params['category']
		sid = params['sid']
		begintime_str = params['begintime']
		endtime_str = params['endtime']
		begin_date = datetime.datetime.strptime(begintime_str, '%Y-%m-%d %H:%M:%S')
		end_date = datetime.datetime.strptime(endtime_str, '%Y-%m-%d %H:%M:%S')
		begin_timestamp = time.mktime(begin_date.timetuple())
		end_timestamp = time.mktime(end_date.timetuple())
		
		data = None
		cursor = connection.cursor()

		# 如果时间间隔超过三小时，按小时聚合，否则按分钟聚合
		if (end_timestamp - begin_timestamp) > 12 * 3600:
			if category == 'mobile':
				# 查询动态数据
				cursor.execute("select concat(DATE_FORMAT(timestamp, '%Y-%m-%d %H'),':00:00') as time, avg(value) as avg, avg(value) - 1.96*(std(value)/sqrt(count(*))) as lower95, avg(value) + 1.96 * (std(value)/ sqrt(count(value))) as upper95 from mobilesensorreadings where timestamp >= '{0}' and timestamp < '{1}' and sid = {2} group by DATE_FORMAT(timestamp, '%Y-%m-%d %H')".format(begintime_str, endtime_str, sid))
				
				desc = cursor.description
				alldata = cursor.fetchall()
				data = [dict(zip([col[0] for col in desc], row)) for row in alldata]

			else:

				# 查询静态数据
				cursor.execute("select concat(DATE_FORMAT(timestamp, '%Y-%m-%d %H'),':00:00') as time, avg(value) as avg, avg(value) - 1.96*(std(value)/sqrt(count(*))) as lower95, avg(value) + 1.96 * (std(value)/ sqrt(count(value))) as upper95 from staticsensorreadings where timestamp >= '{0}' and timestamp < '{1}' and sid = {2} group by DATE_FORMAT(timestamp, '%Y-%m-%d %H')".format(begintime_str, endtime_str, sid))
				
				desc = cursor.description
				alldata = cursor.fetchall()
				data = [dict(zip([col[0] for col in desc], row)) for row in alldata]

		else:
			if category == 'mobile':
				# 查询动态数据
				cursor.execute("select concat(DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i'),':00') as time, avg(value) as avg, avg(value) - 1.96*(std(value)/sqrt(count(*))) as lower95, avg(value) + 1.96 * (std(value)/ sqrt(count(value))) as upper95 from mobilesensorreadings where timestamp >= '{0}' and timestamp < '{1}' and sid = {2} group by DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i')".format(begintime_str, endtime_str, sid))
				desc = cursor.description
				alldata = cursor.fetchall()
				data = [dict(zip([col[0] for col in desc], row)) for row in alldata]
			
			else:
				# 查询静态数据
				cursor.execute("select concat(DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i'),':00') as time, avg(value) as avg, avg(value) - 1.96*(std(value)/sqrt(count(*))) as lower95, avg(value) + 1.96 * (std(value)/ sqrt(count(value))) as upper95 from staticsensorreadings where timestamp >= '{0}' and timestamp < '{1}' and sid = {2} group by DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i')".format(begintime_str, endtime_str, sid))
				desc = cursor.description
				alldata = cursor.fetchall()
				data = [dict(zip([col[0] for col in desc], row)) for row in alldata]

		return HttpResponse(json.dumps(data), content_type='application/json')

def findSensorByTimeRangeAndCoords(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		cursor = connection.cursor()
		
		cursor.execute("select distinct sid from mobilesensorreadings where timestamp > '{0}'  and timestamp < '{1}' and longitude >= {2} and longitude <= {3} and latitude >= {4} and latitude <= {5}".format(params['begintime'], params['endtime'], params['coords'][0], params['coords'][2], params['coords'][1], params['coords'][3]))
		desc = cursor.description
		alldata = cursor.fetchall()
		mobile_data = [row[0] for row in alldata]
	
		cursor.execute("select distinct staticsensorreadings.sid as sid from staticsensorreadings left join staticsensorlocations on staticsensorreadings.sid = staticsensorlocations.sid where timestamp > '{0}'  and timestamp < '{1}' and longitude >= {2} and longitude <= {3} and latitude >= {4} and latitude <= {5}".format(params['begintime'], params['endtime'], params['coords'][0], params['coords'][2], params['coords'][1], params['coords'][3]))

		desc = cursor.description
		alldata = cursor.fetchall()
		static_data = [row[0] for row in alldata]

		data = {'mobile': mobile_data, 'static': static_data}
		
		return HttpResponse(json.dumps(data), content_type='application/json')

def getMobileIdwDataByTimeRange(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		cursor = connection.cursor()
		cursor.execute("select longitude, latitude, value from mobilesensorreadings where timestamp > '{0}'  and timestamp < '{1}'".format(params['begintime'], params['endtime']))
		desc = cursor.description
		alldata = cursor.fetchall()
		data = [dict(zip([col[0] for col in desc], row)) for row in alldata]
		griddata = add_grid_info(data)
		idwdata = idw(griddata)
		return HttpResponse(json.dumps(idwdata), content_type='application/json')

def getStaticIdwDataByTimeRange(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		cursor = connection.cursor()
		cursor.execute("select longitude, latitude, value from staticsensorreadings left join staticsensorlocations on staticsensorreadings.sid = staticsensorlocations.sid where timestamp > '{0}'  and timestamp < '{1}'".format(params['begintime'], params['endtime']))
		desc = cursor.description
		alldata = cursor.fetchall()
		data = [dict(zip([col[0] for col in desc], row)) for row in alldata]
		griddata = add_grid_info(data)
		idwdata = idw(griddata)
		return HttpResponse(json.dumps(idwdata), content_type='application/json')

def getLastCoordsByTimeRange(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		cursor = connection.cursor()
		cursor.execute("select longitude, latitude, sid from mobilesensorreadings where timestamp > '{0}'  and timestamp < '{1}'".format(params['begintime'], params['endtime']))
		desc = cursor.description
		alldata = cursor.fetchall()
		origin_data = [dict(zip([col[0] for col in desc], row)) for row in alldata]
		data = getLastPointsInGrid(origin_data)
		return HttpResponse(json.dumps(data), content_type='application/json')

def getLastCoordByTimeRange(request):
	if request.method == 'POST':
		params = json.loads(request.body)
		cursor = connection.cursor()
		cursor.execute("select longitude, latitude, sid from mobilesensorreadings where timestamp > '{0}'  and timestamp < '{1}'".format(params['begintime'], params['endtime']))
		desc = cursor.description
		alldata = cursor.fetchall()
		origin_data = [dict(zip([col[0] for col in desc], row)) for row in alldata]
		dic = {}
		data = []
		for d in origin_data:
			dic[d['sid']] = [d['longitude'], d['latitude']]
		for k, v in dic.items():
			data.append({'sid': k, 'lnglat': v})
		return HttpResponse(json.dumps(data), content_type='application/json')