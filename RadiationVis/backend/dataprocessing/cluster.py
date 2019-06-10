import sys
import os
import django
import json
from django.db import connection

# 找到项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RadiationVis.settings')
django.setup()

from backend import models

if __name__ == "__main__":
	# begin = '2020-04-06 06:00:00'
	# end = '2020-04-06 06:00:00'
	# all = models.MobileSensorReadings.objects.raw("select longitude, latitude, avg(value) from mobilesensorreadings where timestamp between '2020-04-06 06:00:00'  and '2020-04-06 06:00:00' group by concat(longitude, ',' , latitude) order by count(*) desc")
	# tmp = [str(o) for o in list(all)]
	# print(json.dumps({'data': tmp}))
	
	cursor = connection.cursor()

    # Data retrieval operation - no commit required
	# cursor.execute("select longitude, latitude, avg(value) as value from mobilesensorreadings where timestamp between '2020-04-06 06:00:00'  and '2020-04-06 06:00:00' group by concat(longitude, ',' , latitude) order by count(*) desc")

	cursor.execute("select latitude, longitude, avg(value) as value from staticsensorreadings left join staticsensorlocations on staticsensorreadings.sid = staticsensorlocations.sid where timestamp between '{0}' and '{1}' group by staticsensorreadings.sid;".format('2020-04-06 00:00:00', '2020-04-06 01:00:00'))
	
	desc = cursor.description
	
	data = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
	
	print(json.dumps({'data': data}))