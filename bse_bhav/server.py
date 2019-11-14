'''
The Server module for BSE Bhav Viewer App in CherryPy Framework

Created on Nov 9, 2019

@author: sch
'''

import os
import sys
import cherrypy

from bse_bhav.config import get_redis_connection
from bse_bhav.controllers import ResponseObject, BhavController


class BseBhavApp(object):
    """BSE Bhav Implementation in CherryPy Framework"""

    bhav_controller = None

    @cherrypy.expose
    def index(self):
        """index page"""
        return open(os.path.join("views", "index.html"))

    @cherrypy.expose
    def get_top_stocks(self):
        """
        API end point to get top stocks
        """
        response_object = self.bhav_controller.get_top_stocks()
        return response_object.get_json()


    @cherrypy.expose
    def get_stocks_by_name(self, stock_name=None, **pars):
        """
        API end point to get stocks by name
        """
        if stock_name is None or stock_name == "":
            return ResponseObject(False, "Please provide a valid stock name", None).get_json()
        response_object = self.bhav_controller.get_stocks_by_name(stock_name)
        return response_object.get_json()


if __name__ == "__main__":
    redis_connection = get_redis_connection()
    if redis_connection is None:
        sys.exit(1)
    BseBhavApp.bhav_controller = BhavController(redis_connection)
    cherrypy.config.update({'server.socket_port': 8081})
    cherrypy.quickstart(BseBhavApp())
