import logging
logger = logging.getLogger(__name__)
from backend.models import StaticSensorLocations

if __name__ == "__main__":
	logger.info('hello world')
	all = StaticSensorLocations.objects.all().values()
	print(all)