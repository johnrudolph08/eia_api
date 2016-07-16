# import pandas as pd
import requests
import json

class CallApi:
    """
    Class the returns an eia_api object
    Attributes are set for each json item and can be returned by
    calling CallApi.item_item2 EX: CallApi.series or CallApi.series_data for nested item
    """

    eia_url = 'http://api.eia.gov/series/'

    def __init__(self, api_key, series_id):
        """
        Create eia_api object and related attriobutes from json
        :param api_key: an API key that is provided by EIA
        :param series_id: The series id (also called source key) is a
                       case-insensitive string consisting of letters, numbers, dashes
                       ("-") and periods (".") that uniquely identifies an EIA series
        """
        self.api_key = api_key
        self.series_id = series_id
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
                for key2, value2 in value.items():
                    setattr(self, key + "_" + key2, value2)
            # to handle series key of JSON that returns a list with nested dictionary
            elif isinstance(value, list):
                #get nested dictionary from first item in list
                setattr(self, key, value[0])
                for key2, value2 in value[0].items():
                    setattr(self, key + "_" + key2, value2)
