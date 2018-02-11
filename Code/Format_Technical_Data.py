import pandas as pd 
import numpy as np 
import datetime as dt
import os
import quandl


#Change the working directory to save out data files
#os.chidir("")

#Authenticate the Quandl API with token
quandl.ApiConfig.api_key = 'N1j_H8avpLu-8zwvDdsH'

#TODO: Create a logger for the projects output.
def logger():
	pass

# Initial API call to gain all security prices. 
# All technical ratios will be derived from security data
# Drops any and all non-essential metrics
def getSecurityPrices(security, date_start, date_end):
	date_format = "%Y-%m-%d"
	date_start = dt.datetime.strptime(date_start, date_format)
	date_end = dt.datetime.strptime(date_end, date_format)
	data = quandl.get(("WIKI/" + security), trim_start = date_start, trim_end = date_end)
	data.drop(data.columns[[0,1,2,3,4,5,6]], axis = 1, inplace = True)
	data.columns = ['adj_open','adj_high', 'adj_low', 'adj_close', 'adj_volume']

	return data


# Daily momentum (row label) sub-function
def addDailyMomentum(securityDF):
	securityDF['shifted_close'] = securityDF.adj_close.shift(1)
	securityDF['dly_momentum'] = securityDF.adj_close > securityDF.shifted_close
	securityDF.drop(['shifted_close'], axis = 1, inplace = True)

# 10 Day moving average sub-function
def add10DayMavg(securityDF):
	securityDF['10Dmavg'] = pd.rolling_mean(securityDF.adj_close,10)

# Exponentially weighted 10 day moving average sub-function
def add10DayExpWeightedMavg(securityDF):
	securityDF['10DWmavg'] = pd.ewma(securityDF.adj_close, span = 10)

# 10 day momentum calculation sub-function
def add10DayMomentum(securityDF):
	securityDF['10dshifted_close'] = securityDF.adj_close.shift(10)
	securityDF['10DMomentum'] = (securityDF.adj_close / securityDF['10dshifted_close'])*100
	securityDF.drop(['10dshifted_close'], axis = 1, inplace = True)

# Adds stochastic K-percent figure to dataframe sub-function
def addStochasticKPercent(securityDF):
	roll_min = securityDF.adj_low.rolling(14,min_periods = 14).min()
	roll_max = securityDF.adj_high.rolling(14,min_periods = 14).max()
	securityDF['stoch_Kperc'] = ((securityDF.adj_close - roll_min)/(roll_max - roll_min)) * 100

# Adds stochastic D-percent figure to dataframe (derived from k%) sub-function
def addStochasticDPercent(securityDF):
	securityDF['stoch_Dperc'] = pd.rolling_mean(securityDF.stoch_Kperc,3)

# Relative strength index over a window of 14 days. sub-function
def addRelativeStrengthIndex(securityDF):
	securityDF['shifted_close'] = securityDF.adj_close.shift(1)
	securityDF['gain/loss'] = (securityDF.adj_close - securityDF.shifted_close) / securityDF.shifted_close

	# To get average gain and loss per period
	securityDF['gain'] = np.where(securityDF['gain/loss'] > 0,securityDF['gain/loss'],0)
	# Include a negative one here to reverse the sign of loss values
	securityDF['loss'] = np.where(securityDF['gain/loss'] <= 0,securityDF['gain/loss']*-1,0)

	# average gain and average loss
	avg_gain = pd.rolling_mean(securityDF.gain,14)
	avg_loss = pd.rolling_mean(securityDF.loss,14)

	#Drop unnecessary columns
	securityDF.drop(['gain/loss','gain','loss'], axis = 1, inplace = True)

	securityDF['14dRSI'] = (100 - (100/ (1 + (avg_gain/avg_loss))))


# Adds MACD histogram values, sub-function
def addMACDHistogram(securityDF):
	D12EWMACD = pd.ewma(securityDF.adj_close, span = 12)
	D26EWMACD = pd.ewma(securityDF.adj_close, span = 26)

	# Get 9 day exponential moving average of EWMACDLine
	EWMACDLine = D12EWMACD - D26EWMACD
	Signal_Line = pd.ewma(EWMACDLine, span = 9)

	# For debugging code
	# print(EWMACDLine)
	# print(Signal_Line)

	#Finalize addition to securityDF
	securityDF['EWMACD'] = EWMACDLine - Signal_Line

# 
def addWilliamsRPercent(securityDF):
	roll_min = securityDF.adj_low.rolling(14,min_periods = 14).min()
	roll_max = securityDF.adj_high.rolling(14,min_periods = 14).max()

	securityDF['williams_Rperc'] = ((roll_max - securityDF.adj_close) / (roll_max - roll_min)) * -100

# 7-Day ADL, sub-function
def add7DayAccumulationDistributionLine(securityDF):
	roll_min = securityDF.adj_low.rolling(7,min_periods = 7).min()
	roll_max = securityDF.adj_high.rolling(7,min_periods = 7).max()

	securityDF['7D_ADL'] = ((securityDF.adj_close - roll_min) - (roll_max - securityDF.adj_close)) / (roll_max - roll_min)

def addCommodityChannelIndex(securityDF):
	typical_price = (securityDF.adj_close + securityDF.adj_high + securityDF.adj_low) / 3
	Constant = 0.15

	rolling_mean_TP_20D = pd.rolling_mean(typical_price,20)
	mean_deviation = abs(typical_price - rolling_mean_TP_20D)
	rolling_mean_MD = pd.rolling_mean(mean_deviation,20)

	securityDF['20D_CCI'] = (typical_price - rolling_mean_TP_20D) / (0.15 * rolling_mean_MD)

# Adds technical attributes to an existing dataset
# Each will be labeled appropriately
# This is the orchestration package for all of the
# Sub-functions written below (start with "add")
def addTechnicalAttributes(securityDF):
	add10DayMavg(securityDF)
	add10DayExpWeightedMavg(securityDF)
	add10DayMomentum(securityDF)
	addStochasticKPercent(securityDF)
	addStochasticDPercent(securityDF)
	addRelativeStrengthIndex(securityDF)
	addMACDHistogram(securityDF)
	addWilliamsRPercent(securityDF)
	add7DayAccumulationDistributionLine(securityDF)
	addCommodityChannelIndex(securityDF)
	#Label should always be last
	addDailyMomentum(securityDF)
	securityDF.dropna(inplace = True)


df = getSecurityPrices("aapl","1997-01-01","2018-01-01")
addTechnicalAttributes(df)
print(df.describe())







