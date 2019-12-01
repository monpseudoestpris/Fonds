from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt


stock_name='EADSY'
ts = TimeSeries(key='XCQ64AA4PCFYKBYH', output_format='pandas')
data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
data['4. close'].plot()
plt.title('Intraday Times Series for the '+stock_name+' KEY stock (1 min)')
plt.show()
