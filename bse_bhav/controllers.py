'''
Created on Nov 9, 2019

@author: sch
'''

from datetime import date, timedelta
import logging
import json

import requests

from bse_bhav.parser import download_and_store_bhav, STOCK_PREFIX, TOP_STOCKS_COUNT, \
    SORTED_BHAV_SET_NAME, LAST_DATE_INDEXD_KEY, BSE_BASE_URL


class ResponseObject(object):
    """
    Generic response object
    """

    success = None
    msg = None
    data = None

    def __init__(self, success, msg, data):
        """Constructor"""
        self.success = success
        self.msg = msg
        self.data = data

    def get_json(self):
        """Returns the Json format of the ResponseObject"""
        stocks_data = []
        if self.data is not None:
            for stock in self.data:
                stock[1]['name'] = stock[0]
                stocks_data.append(stock[1])
        return json.dumps({"success": self.success, "msg": self.msg, "data": stocks_data})

    def __str__(self):
        """Overidden"""
        return "success=%s; msg=%s; data=%s" % (self.success, self.msg, self.data)


class BhavController(object):
    """
    BSE Bhav controller which interact with the database
    """

    redis_connection = None

    def __init__(self, redis_connection):
        """Constructor"""
        self.redis_connection = redis_connection


    def save_bhav_copy_report(self, report_date=date.today()):
        """
        Downloads, read and saves the bhav copy in Database
        """
        saved = download_and_store_bhav(report_date, self.redis_connection)
        if saved:
            return ResponseObject(True, "Sucessfully saved the data for %s" %
                                  (report_date.strftime("%d-%m-%y")), None)
        return ResponseObject(False, "Issue in saving bhav report", None)


    def save_latest_bhav_report(self):
        """
        Saves the lastest report by trying to download report for today, today - 1 date and so on
        """
        bse_ping = requests.get(BSE_BASE_URL)
        if bse_ping.status_code != 200:
            return ResponseObject(False, "%s is giving %s" % (BSE_BASE_URL, bse_ping), None)
        days_to_subtract = 0
        while True:
            if days_to_subtract > 10:
                return ResponseObject(False, "Tried to index for 10 days but failed", None)
            report_date = date.today() - timedelta(days=days_to_subtract)
            resp = self.save_bhav_copy_report(report_date)
            if resp.success:
                return resp
            days_to_subtract += 1


    def get_top_stocks(self):
        """
        Gets the top 10 stocks from the DB
        """
        try:
            top_stocks_keys = self.redis_connection.zrange(SORTED_BHAV_SET_NAME, 0, -1)
            data = []
            for key in top_stocks_keys:
                stock_name = key.lstrip(STOCK_PREFIX)
                data.append((stock_name, self.redis_connection.hgetall(key)))
            return ResponseObject(True, "Got top %s stocks" % TOP_STOCKS_COUNT, data)
        except Exception as execption:
            logging.exception(execption)
            return ResponseObject(False, str(execption), None)


    def get_stocks_by_name(self, stock_name):
        """
        Scans the database against a stock_name and returns the result
        """
        try:
            stock_name = stock_name.rstrip().lstrip()
            data = []
            scan_name = STOCK_PREFIX + "*" + stock_name.upper() + "*"
            for key in self.redis_connection.scan_iter(scan_name):
                stock_key = key.lstrip(STOCK_PREFIX)
                data.append((stock_key, self.redis_connection.hgetall(key)))
            if len(data) == 0:
                return ResponseObject(False, "Got 0 matches for %s" % stock_name, data)
            return ResponseObject(True, "Got a total of %s matches for %s"\
                                  % (len(data), stock_name), data)
        except Exception as execption:
            logging.exception(execption)
            return ResponseObject(False, str(execption), None)


    def get_last_date_indexed(self):
        """
        Gets last indexed date
        """
        last_date_indexed = self.redis_connection.get(LAST_DATE_INDEXD_KEY)
        return last_date_indexed
