'''
The Server module for BSE Bhav Viewer App in CherryPy Framework

Created on Nov 9, 2019

@author: sch
'''

import os
import sys
import logging

import cherrypy
from jinja2 import Environment, FileSystemLoader

from bse_bhav.config import get_redis_connection
from bse_bhav.controllers import ResponseObject, BhavController
from bse_bhav.parser import TOP_STOCKS_COUNT


ENV = Environment(loader=FileSystemLoader('templates'))


class BseBhavApp(object):
    """BSE Bhav Implementation in CherryPy Framework"""

    bhav_controller = None

    @cherrypy.expose
    def index(self):
        """index page"""
        tmpl = ENV.get_template('index.html')
        last_date_indexed = self.bhav_controller.get_last_date_indexed()
        return tmpl.render(last_date_indexed=last_date_indexed, top_stocks_number=TOP_STOCKS_COUNT)

    @cherrypy.expose
    def get_top_stocks(self):
        """
        API end point to get top stocks
        """
        response_object = self.bhav_controller.get_top_stocks()
        return response_object.get_json()

    @cherrypy.expose
    def get_stocks_by_name(self, stock_name=None):
        """
        API end point to get stocks by name
        """
        if stock_name is None or stock_name == "":
            return ResponseObject(False, "Please provide a valid stock name", None).get_json()
        response_object = self.bhav_controller.get_stocks_by_name(stock_name)
        return response_object.get_json()

    @cherrypy.expose
    def save_latest_bhav_report(self):
        """
        Save the latest bhav report on D/B.
        """
        return self.bhav_controller.save_latest_bhav_report().get_json()


CONFIG = {'global': {
    'server.socket_host': '0.0.0.0',
    'server.socket_port':  int(os.environ.get('PORT', '5000'))
    },
          '/favicon.ico': {
              'tools.staticfile.on': True,
              'tools.staticfile.filename': os.path.join(os.path.abspath(os.getcwd()), "static",
                                                        "favicon.ico")
          },
          '/static': {
              'tools.staticdir.on' : True,
              'tools.staticdir.dir' : os.path.join(os.path.abspath(os.getcwd()), "static")
              }
         }

os.path.join(os.path.abspath(os.getcwd()), "static")

if __name__ == "__main__":
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.basicConfig(filename="bse_bhav_app.log",
                        filemode='a',
                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S",
                        level=logging.DEBUG)
    REDIS_CONNECTION = get_redis_connection()
    if REDIS_CONNECTION is None:
        sys.exit(1)
    BHAV_CONTROLLER = BhavController(REDIS_CONNECTION)
    BHAV_CONTROLLER.save_latest_bhav_report()
    BseBhavApp.bhav_controller = BHAV_CONTROLLER
    cherrypy.quickstart(BseBhavApp(), '/', config=CONFIG)
