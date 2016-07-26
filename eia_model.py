import requests
import json
import datetime


class CallApi:
    """
    Class the returns an eia_api object
    Attributes are set for each json item and can be returned by
    calling CallApi.item_item2 EX: CallApi.series or CallApi.series_data for nested item
    """

    eia_url = 'http://api.eia.gov/series/'

    def __init__(self, api_key, *args):
        """
        Create eia_api object and related attriobutes from json
        :param api_key: an API key that is provided by EIA
        :param *args: The series id (also called source key) is a
                       case-insensitive string consisting of letters, numbers, dashes
                       ("-") and periods (".") that uniquely identifies an EIA series\
                       multiple series can be submitted by comma separation ex: api_key, s1, s2
        """
        self.api_key = api_key
        self.series_id = [";".join(args)]
        self.json = self.get_series()
        self.create_atttributes()

    def get_series(self):
        """
        Calls the EIA API with supplied api_key on init and series_id and return json
        """
        api_parms = (
            ('api_key', self.api_key),
            ('series_id', self.series_id),
        )
        eia_req = requests.get(self.eia_url, params=api_parms)
        return json.loads(eia_req.text)

    def create_atttributes(self):
        """
        Set class attributes for each dict item from returned json
        """
        for key, value in self.json.items():
            # to handle request key of JSON that returns a nested dictionary
            if isinstance(value, dict):
                setattr(self, key, value)
            # to handle series key of JSON that returns a list with nested
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    setattr(self, 'series_{}'.format(i+1), item)


def create_datetime(series):
        """
        Creates a list of datetimes from eia_json
        :param series is an eia series list of attributes
        """
        freq = {'A': '%Y', 'M': '%Y%m', 'W': '%Y%m%d', 'D': '%Y%m%d'}
        date_list = [datetime.datetime.strptime(x[0], freq[series['f']]).strftime(
            '%Y-%m-%d %H:%M:%S') for x in series['data']]
        return date_list


def create_values(series):
        """
        Creates a list of values
        :param series is an eia series list of attributes
        """
        return [x[1] for x in series['data']]
