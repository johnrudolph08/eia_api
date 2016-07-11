import eia_model as em
# import plotly
# import plotly.plotly as py
# from plotly.graph_objs import *

api_key_inp = '5F4109570C68FDE20F42C25F5152D879'
series_id_inp = 'NG.NW2_EPG0_SWO_R48_BCF.W'
series_id_inp2 = 'ELEC.GEN.ALL-AL-99.A'

# plotly.tools.set_credentials_file(username='johnrudolph08', api_key='tc8c5nyic2')

# trace0 = Scatter(
#     x=[1, 2, 3, 4],
#     y=[10, 15, 13, 17]
# )
# trace1 = Scatter(
#     x=[1, 2, 3, 4],
#     y=[16, 5, 11, 9]
# )
# data = Data([trace0, trace1])

# py.plot(data, filename='basic-line')

eia_test = em.SeriesQuery(api_key_inp, series_id_inp)
print(eia_test.get('data'))
