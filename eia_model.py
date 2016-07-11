# import pandas as pd
import requests
import json


class SeriesQuery:

    eia_url = 'http://api.eia.gov/series/'

    def __init__(self, api_key, series_id):
        """
        Require and api_key and series_id

        :param api_key: an API key that is provided by EIA
        :param series_id: The series id (also called source key) is a
                       case-insensitive string consisting of letters, numbers, dashes
                       ("-") and periods (".") that uniquely identifies an EIA series
        """
        self.api_parms = (
            ('api_key', api_key),
            ('series_id', series_id),
        )

        self.json = self.get_json()

    def get_json(self):
        """
        Makes a call to the EIA API and returns a dictionary from JSON
        """
        eia_req = requests.get(self.eia_url, params=self.api_parms)
        return json.loads(eia_req.text)

    def get_field(self, field):
        """
        Takes a dict with nested lists and dicts,
        and searches all dicts for a key of the field
        provided.

        :param field: A field to search for in search_dict
        """
        fields_found = []

        for key, value in self.json.items():

            if key == field:
                fields_found.append(value)

            elif isinstance(value, dict):
                results = self.get_field(value, field)
                for result in results:
                    fields_found.append(result)

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self.get_field(item, field)
                        for another_result in more_results:
                            fields_found.append(another_result)

        return fields_found


# def eia_data_series_to_df(eia_series):
#     '''Converts eia api data series to dataframe'''
#     eia_df = pd.DataFrame(eia_series)
#     eia_df.columns = ['date', 'value']
#     return eia_df