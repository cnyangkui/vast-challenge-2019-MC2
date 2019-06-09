import sys
import os
import django
import json

# 找到项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RadiationVis.settings')
django.setup()

from backend.models import StaticSensorLocations

if __name__ == "__main__":
	all = StaticSensorLocations.objects.raw("select * from staticsensorlocations")
	tmp = [str(o) for o in list(all)]
	print(json.dumps({'data': tmp}))