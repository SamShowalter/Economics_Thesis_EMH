import pandas as pd 
import numpy as np 
import datetime as dt
import os
import quandl


#Change the working directory to save out data files
#os.chidir("")

#Authenticate the Quandl API with token
quandl.ApiConfig.api_key = 'N1j_H8avpLu-8zwvDdsH'

#TODO: Create a logger function to connect transaction output for the projects output.
class StockCollectionRecord():

	#Record for Collection
	def __init__(self, securityName, startDate, endDate, trendSpecific = False):
		try:
			self.ExecutionDate = dt.datetime.now().date()
			self.utcDateTimeStart = dt.datetime.utcnow()
			self.ExecutionTimeStart = dt.datetime.now().time()
			self.StockTicker = securityName
			self.ScheduledDateStart = startDate
			self.ScheduledDateEnd = endDate
			self.TrendSpecific = trendSpecific
			self.StatusMessage = "Pending"

			#API pull to get the security price information
			self.getSecurityPrices()

			#Get technical attributes for data
			self.addTechnicalAttributes()

			# Convert to trend specific if necessary
			if trendSpecific:
				self.convertToTrendSpecific()

		except Exception as e:
			print("\nERROR: Data pull failed:\n" + str(e)+"\n")
			self.ActualDateStart = -1
			self.ActualDateEnd = -1
			self.NumRows = -1
			self.NumCols = -1
			self.NumNaNRecords = -1
			self.PullDuration = -1
			self.securityDF = -1
			self.StatusMessage = "FAILURE"
			

		


	# Initial API call to gain all security prices. 
	# All technical ratios will be derived from security data
	# Drops any and all non-essential metrics
	def getSecurityPrices(self):
		date_format = "%Y-%m-%d"
		date_start = dt.datetime.strptime(self.ScheduledDateStart, date_format)
		date_end = dt.datetime.strptime(self.ScheduledDateEnd, date_format)
		data = quandl.get(("WIKI/" + self.StockTicker), trim_start = self.ScheduledDateStart, trim_end = self.ScheduledDateEnd)
		data.drop(data.columns[[0,1,2,3,4,5,6]], axis = 1, inplace = True)
		data.columns = ['adj_open','adj_high', 'adj_low', 'adj_close', 'adj_volume']

		#Final Informationa about data pulling
		self.ActualDateStart = str(data.index[0])[:11]
		self.ActualDateEnd = str(data.index[-1])[:11]
		self.NumRows = len(data.index)
		self.StatusMessage = "Success"

		#Assign Dataframe to variable
		self.securityDF = data
		

	# Daily momentum (row label) sub-function
	def addDailyMomentum(self):
		self.securityDF['shifted_close'] = self.securityDF.adj_close.shift(1)
		self.securityDF['dly_momentum'] = self.securityDF.adj_close > self.securityDF.shifted_close
		self.securityDF.drop(['shifted_close'], axis = 1, inplace = True)

	# 10 Day moving average sub-function
	def add10DayMavg(self):
		self.securityDF['10D_mavg'] = pd.rolling_mean(self.securityDF.adj_close,10)

	# Exponentially weighted 10 day moving average sub-function
	def add10DayExpWeightedMavg(self):
		self.securityDF['10D_Wmavg'] = pd.ewma(self.securityDF.adj_close, span = 10)

	# 10 day momentum calculation sub-function
	def add10DayMomentum(self):
		self.securityDF['10dshifted_close'] = self.securityDF.adj_close.shift(10)
		self.securityDF['10D_Momentum'] = (self.securityDF.adj_close / self.securityDF['10dshifted_close'])*100
		self.securityDF.drop(['10dshifted_close'], axis = 1, inplace = True)

	# Adds stochastic K-percent figure to dataframe sub-function
	def add14DayStochasticKPercent(self):
		roll_min = self.securityDF.adj_low.rolling(14,min_periods = 14).min()
		roll_max = self.securityDF.adj_high.rolling(14,min_periods = 14).max()
		self.securityDF['14D_stoch_Kperc'] = ((self.securityDF.adj_close - roll_min)/(roll_max - roll_min)) * 100

	# Adds stochastic D-percent figure to dataframe (derived from k%) sub-function
	def addStochasticDPercent(self):
		self.securityDF['stoch_Dperc'] = pd.rolling_mean(self.securityDF['14D_stoch_Kperc'],3)

	# Relative strength index over a window of 14 days. sub-function
	def addRelativeStrengthIndex(self):
		self.securityDF['shifted_close'] = self.securityDF.adj_close.shift(1)
		self.securityDF['gain/loss'] = (self.securityDF.adj_close - self.securityDF.shifted_close) / self.securityDF.shifted_close

		# To get average gain and loss per period
		self.securityDF['gain'] = np.where(self.securityDF['gain/loss'] > 0,self.securityDF['gain/loss'],0)
		# Include a negative one here to reverse the sign of loss values
		self.securityDF['loss'] = np.where(self.securityDF['gain/loss'] <= 0,self.securityDF['gain/loss']*-1,0)

		# average gain and average loss
		avg_gain = pd.rolling_mean(self.securityDF.gain,14)
		avg_loss = pd.rolling_mean(self.securityDF.loss,14)

		#Drop unnecessary columns
		self.securityDF.drop(['gain/loss','gain','loss'], axis = 1, inplace = True)

		#Add rsi metric
		self.securityDF['14D_RSI'] = (100 - (100/ (1 + (avg_gain/avg_loss))))


	# Adds MACD histogram values, sub-function
	def addMACDHistogram(self):
		D12EWMACD = pd.ewma(self.securityDF.adj_close, span = 12)
		D26EWMACD = pd.ewma(self.securityDF.adj_close, span = 26)

		# Get 9 day exponential moving average of EWMACDLine
		EWMACDLine = D12EWMACD - D26EWMACD
		Signal_Line = pd.ewma(EWMACDLine, span = 9)

		# For debugging code
		# print(EWMACDLine)
		# print(Signal_Line)

		#Finalize addition to securityDF
		self.securityDF['EWMACD'] = EWMACDLine - Signal_Line

	# 
	def add14DayWilliamsRPercent(self):
		roll_min = self.securityDF.adj_low.rolling(14,min_periods = 14).min()
		roll_max = self.securityDF.adj_high.rolling(14,min_periods = 14).max()

		self.securityDF['14D_stock_Rperc'] = ((roll_max - self.securityDF.adj_close) / (roll_max - roll_min)) * -100

	# 7-Day ADL, sub-function
	def add7DayAccumulationDistributionLine(self):
		roll_min = self.securityDF.adj_low.rolling(7,min_periods = 7).min()
		roll_max = self.securityDF.adj_high.rolling(7,min_periods = 7).max()

		#Rolling volume, divided by 1000
		roll_vol_sum = self.securityDF.adj_volume.rolling(7,min_periods = 7).sum() / 1000

		# Money flow multiplier and money flow volume
		money_flow_mult = ((self.securityDF.adj_close - roll_min) - (roll_max - self.securityDF.adj_close)) / (roll_max - roll_min)
		money_flow_vol = roll_vol_sum * money_flow_mult

		# For debugging purposes
		# print(money_flow_mult.describe())

		# Iterates through to change A/D Line day to day
		for i in range(7,len(money_flow_vol)):
			money_flow_vol.iloc[i] = money_flow_vol.iloc[i-1] + money_flow_vol.iloc[i]

		self.securityDF['7D_ADL'] = money_flow_vol

	def addCommodityChannelIndex(self):
		typical_price = (self.securityDF.adj_close + self.securityDF.adj_high + self.securityDF.adj_low) / 3
		Constant = 0.15

		rolling_mean_TP_20D = pd.rolling_mean(typical_price,20)
		mean_deviation = abs(typical_price - rolling_mean_TP_20D)
		rolling_mean_MD = pd.rolling_mean(mean_deviation,20)

		# 0.015 is apparently the customary constant here, as seen in literature
		self.securityDF['20D_CCI'] = (typical_price - rolling_mean_TP_20D) / (0.015 * rolling_mean_MD)


	# Adds technical attributes to an existing dataset
	# Each will be labeled appropriately
	# This is the orchestration package for all of the
	# Sub-functions written below (start with "add")
	def addTechnicalAttributes(self):
		self.add10DayMavg()
		self.add10DayExpWeightedMavg()
		self.add10DayMomentum()
		self.add14DayStochasticKPercent()
		self.addStochasticDPercent()
		self.addRelativeStrengthIndex()
		self.addMACDHistogram()
		self.add14DayWilliamsRPercent()
		self.add7DayAccumulationDistributionLine()
		self.addCommodityChannelIndex()
		#Label should always be last
		self.addDailyMomentum()
		self.NumCols = len(self.securityDF.columns)
		self.NumNaNRecords = max(self.securityDF.isnull().sum())
		#self.securityDF.dropna(inplace = True)

		# Duration of API pull captured
		API_time_end = dt.datetime.utcnow()
		self.PullDuration = (API_time_end - self.utcDateTimeStart).total_seconds()

	def convertWithTrending(self,dfColumn):
		return np.where(dfColumn > dfColumn.shift(1),1,-1)

	def convertWithBounds(self,dfColumn, lowerBound, upperBound):
		bool_greater_col = (dfColumn > dfColumn.shift(1))

		# Less than lower threshold (oversold) or (yesterday's indicator and less than upperBound), up, otherwise down
		return np.where(((dfColumn < lowerBound) | ((bool_greater_col) & (dfColumn < upperBound))),1,-1)

	# May do this later, once more of the model is built.
	def convertToTrendSpecific(self):
		# Add trend specific for moving averages
		self.securityDF['10D_mavg'] = np.where(self.securityDF['10D_mavg'] < self.securityDF.adj_close, 1, -1)
		self.securityDF['10D_Wmavg'] = np.where(self.securityDF['10D_Wmavg'] < self.securityDF.adj_close, 1, -1)

		# Add trend specific for momentum
		self.securityDF['10D_Momentum'] = np.where(self.securityDF['10D_Momentum'] > 100, 1, -1)

		#Convert remaining columns with helper functions
		self.securityDF['EWMACD'] = self.convertWithTrending(self.securityDF['EWMACD'])
		self.securityDF['7D_ADL'] = self.convertWithTrending(self.securityDF['7D_ADL'])
		self.securityDF['20D_CCI'] = self.convertWithBounds(self.securityDF['20D_CCI'],-200,200)
		self.securityDF['14D_stoch_Kperc'] = self.convertWithBounds(self.securityDF['14D_stoch_Kperc'],20,80)
		self.securityDF['stoch_Dperc'] = self.convertWithBounds(self.securityDF['stoch_Dperc'],20,80)
		self.securityDF['14D_stock_Rperc'] = self.convertWithBounds(self.securityDF['14D_stock_Rperc'],-80,-20)
		self.securityDF['14D_RSI'] = self.convertWithBounds(self.securityDF['14D_RSI'],30,70)

		#Change the time log for variable
		# Duration of API pull captured
		API_time_end = dt.datetime.utcnow()
		self.PullDuration = (API_time_end - self.utcDateTimeStart).total_seconds()
		




	









