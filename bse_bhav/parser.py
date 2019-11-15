'''
This modules contains code to download the BSE Bhavcopy which is published
on everyday once INDIAN market closes.

Created on Nov 6, 2019

@author: sch
'''

import os
import io
import logging
import zipfile
import csv

import requests


BHAV_CODE_INDEX = 0
BHAV_NAME_INDEX = 1
BHAV_OPEN_INDEX = 4
BHAV_HIGH_INDEX = 5
BHAV_LOW_INDEX = 6
BHAV_CLOSE_INDEX = 7
BHAV_LAST_INDEX = 8
BHAV_PREVIOUS_CLOSE_INDEX = 9
SORTED_BHAV_SET_NAME = "bhav_score"
LAST_DATE_INDEXD_KEY = "last_date_indexed"
TOP_STOCKS_COUNT = 10
STOCK_PREFIX = "ticker_"


class Bhav(object):
    """
    A python class to encapsulate the bhav attributes
    """
    key = None
    data = None


    def __init__(self, key, value):
        """Constructor"""
        self.key = key
        self.data = value


    def calculate_percentage_change(self):
        """
        Calculates the percentage change i.e change of data between close and open
        """
        self.data["percentage"] = round(round(((self.data['close'] - self.data['open'])\
                                                 / self.data['open']) * 100, 2), 2)


    def __str__(self):
        return "%s : %s" % (self.key, self.data)


def download_bse_bhav_copy(report_date):
    """
    Downloads the BSE bhav copy for a given date and returns the absolute path of the report

    Parameters:
    report_date (datetime.date): the date for which bhav copy is to be downloaded

    Returns:
    sting: absolute filepath of the report
    """
    bhav_filename = "EQ%s_CSV.ZIP" % report_date.strftime("%d%m%y")
    bhav_url = "https://www.bseindia.com/download/BhavCopy/Equity/" + bhav_filename
    response = requests.get(bhav_url, stream=True)
    if response.status_code != 200:
        logging.warning("Got response code %s when trying to download: %s",
                        response.status_code, bhav_url)
        return None
    logging.info("Successfully got status 200 when trying to download: %s", bhav_url)
    bhav_filepath = os.path.abspath("EQ%s.CSV" % report_date.strftime("%d%m%y"))
    bhav_zip = zipfile.ZipFile(io.BytesIO(response.content))
    bhav_zip.extractall()
    logging.info("Successfully extracted the file as %s", bhav_filepath)
    return bhav_filepath


def read_bse_bhav_report(bhav_filepath):
    """
    Reads the BSE Bhav CSV Report file

    Parameters:
    bhav_filepath (string): absolute filepath of the report

    Returns:
    list: list of rows of Bhav
    """
    bhav_list = []
    if not os.path.exists(bhav_filepath):
        logging.error("Can't find file %s", bhav_filepath)
        return bhav_list
    with open(bhav_filepath, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        csvreader.__next__()
        for row in csvreader:
            key = STOCK_PREFIX + row[BHAV_NAME_INDEX].rstrip().upper()
            data = {"code": row[BHAV_CODE_INDEX],
                    "open": float(row[BHAV_OPEN_INDEX]),
                    "high": float(row[BHAV_HIGH_INDEX]),
                    "low": float(row[BHAV_LOW_INDEX]),
                    "close": float(row[BHAV_CLOSE_INDEX]),
                   }
            bhav = Bhav(key, data)
            bhav.calculate_percentage_change()
            bhav_list.append(bhav)
    os.remove(bhav_filepath)
    return bhav_list


def store_bhav_in_redis(bhav_list, redis_connection):
    """
    Stores the bhav list in the redis and also store the sorted set with maximum perentage
    under SORTED_BHAV_SET_NAME
    """
    # flush the previous data if any
    redis_connection.flushdb()
    for bhav in bhav_list:
        if not redis_connection.hmset(bhav.key, bhav.data):
            logging.warning("Not able to save the entry %s in Database", bhav)
            return False
    logging.info("Successfully saved %s entries in database", len(bhav_list))
    bhav_list.sort(key=lambda bhav: bhav.data['percentage'], reverse=True)
    for index in range(TOP_STOCKS_COUNT):
        score = index + 1
        if redis_connection.zadd(SORTED_BHAV_SET_NAME, {bhav_list[index].key: score}) != 1:
            logging.warning("Not able to save the score of %s in Database", bhav_list[index])
            return False
    logging.info("Successfully saved the score of top %s Bhav under %s",\
                 TOP_STOCKS_COUNT, SORTED_BHAV_SET_NAME)
    return True


def download_and_store_bhav(report_date, redis_connection):
    """
    Downloads the bhav copy and store it in the redis d/b
    Return True if sucess else False
    """
    bhav_filepath = download_bse_bhav_copy(report_date)
    if bhav_filepath is None:
        return False
    bhav_list = read_bse_bhav_report(bhav_filepath)
    if bhav_list == []:
        return False
    if not store_bhav_in_redis(bhav_list, redis_connection):
        # flush DB incase of inconsistent data load
        logging.warning("Flushing the database")
        redis_connection.flushdb()
        return False
    redis_connection.set(LAST_DATE_INDEXD_KEY, report_date.strftime("%d-%m-%y"))
    return True
