'''
Created on Nov 14, 2019

@author: sch
'''

import sys
from datetime import date

from bse_bhav.config import get_redis_connection
from bse_bhav.controllers import BhavController

REDIS_CONNECTION = get_redis_connection()
if REDIS_CONNECTION is None:
    sys.exit()
REDIS_CONNECTION.flushdb()
bhav_controller = BhavController(REDIS_CONNECTION) 
bhav_controller.save_bhav_copy_report(date(2019, 11, 14))
data = bhav_controller.get_top_stocks()
print(data.get_json())
data = bhav_controller.get_stocks_by_name("bank")
print(data.get_json())