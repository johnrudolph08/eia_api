
eia_api = '5F4109570C68FDE20F42C25F5152D879'
owm_api = '15469feacecb3b229172bf20a0227e8b'
sid = 'EBA.SCL-ALL.D.H'
location = 'Seattle,US'
city_id = 5809805
start = '2015-09-13 16:46:40+00'
end = '2015-09-13 19:16:40+00'
units = 'imperial'

class GetWeatherForecast(object):
    """
    A class to capture an pyowm weather forecast call
    """

    def __init__(self, api_key, location):
        """
        Create pyowm forecast object and return related attributes
        :param api_key: a valid Open Weath Map Api-Key
        :param location: a valid Open Weather Map Location EX: 'Seattle,US'
        """
        self.api_key = api_key
        self.forecast = self.get_weather(location)
        self.weather_detail = self.get_weather_detail(self.forecast)
        self.time_1hr = self.get_time_1hr(self.weather_detail)
        self.temps = self.interpolate_weather(
            self.weather_detail, self.time_1hr, 'temp')

    def get_weather(self, location):
        """
        Gets weather forecast from openweathermap
        :param location: a valid location provided to owm weather api
        """
        owm = pyowm.OWM(self.api_key)
        fc = owm.three_hours_forecast(location)
        f = fc.get_forecast()
        return f.get_weathers()

    @staticmethod
    def get_weather_detail(weather):
        """
        Returns a nested dictionary where first key is date and second key is temp attrs
        :param weather is a object from get_weather_data
        """
        time_dict = {}
        # first loop through each 3 hr interval in forecast
        for i in weather:
            time = datetime.fromtimestamp(
                i.get_reference_time()).strftime('%Y-%m-%d %H:%M:%S')
            temps_dict = {'temp': None, 'temp_max': None, 'temp_min': None}
            # create nested dict for each temp attribute
            for j in temps_dict:
                temps_dict[j] = i.get_temperature('fahrenheit').get(j)
            time_dict[time] = temps_dict
        return pd.DataFrame.from_dict(time_dict, orient='index')

    @staticmethod
    def interpolate_weather(weather_detail, time, key):
        """
        Interpolates the 3hr forecast to an hourly forecast using cubic interpolation
        :param weather_detail is dataframe weather attributes returned from get_weather_detail
        :param key is weather detail dataframe column (temp, temp_max or temp_min)
        """
        date_len = len(weather_detail.index)
        date_axis = np.linspace(1, date_len, date_len, endpoint=True)
        f_cubic = interp1d(date_axis, weather_detail[key])
        temp_int = f_cubic(np.linspace(
            1, date_len, num=date_len * 3 - 2, endpoint=True))
        return pd.DataFrame(temp_int.tolist(), index=time)

    @staticmethod
    def get_time_1hr(weather_detail):
        """
        Parses temperature and time from weather objects imbedded in forecast object
        :param weather detail is dictionary returned from get_weather_detail
        """
        min_time, max_time = weather_detail.index.min(), weather_detail.index.max()
        return pd.date_range(min_time, max_time, freq='H')