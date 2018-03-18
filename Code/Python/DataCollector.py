import pandas as pd 
import numpy as np 
import datetime as dt
import os
import quandl

#Authenticate the Quandl API with token
#quandl.ApiConfig.api_key = 'N1j_H8avpLu-8zwvDdsH'
quandl.ApiConfig.api_key = 'KNJV-DzCKDdhU2PKfwag'

#TODO: Create a logger function to connect transaction output for the projects output.
class StockCollector():

	#Record for Collection
	def __init__(self, securityName, 
					   startDate, 
					   endDate, 
					   trendSpecific = True,
					   remoteServer = False):

		#Set initial values and variables
		self.RemoteServer = remoteServer
		self.CollectionDate = dt.datetime.now().date()
		self.utcDateTimeStart = dt.datetime.utcnow()
		self.CollectionTimeStart = dt.datetime.now().time()
		self.StockTicker = securityName
		self.ScheduledDateStart = startDate
		self.ScheduledDateEnd = endDate
		self.NumNaNRecords = 0
		self.TrendSpecific = trendSpecific
		self.StatusMessage = "Pending"

	def _defaultDataPullFailure(self, e):
		# Record the error message where the stock ticker would be
		self.StockTicker = str(e)
		self.ActualDateStart = -1
		self.ActualDateEnd = -1
		self.NumRows = -1
		self.NumCols = -1
		self.NumNaNRecords = -1
		self.PullDuration = -1
		self.SecurityDF = -1
		self.StatusMessage = "FAILURE"

	def runDataCollector(self):
		try:
			#If the stock data is from a csv
			if (self.StockTicker[0] == "^"):
				print("\nPULLING FROM CSV FOR INDEX DATA\n")
				self.readCSVData()

			#API pull to get the security price information
			else:
				self.getSecurityPrices()

			#Get technical attributes for data
			self.addTechnicalAttributes()

			# Convert to trend specific if necessary
			if self.TrendSpecific:
				self.convertToTrendSpecific()

			#Drop un-used columns
			self.SecurityDF.drop(['adj_open','adj_high','adj_low'], axis = 1, inplace = True)

			#Shifts adjusted price, volume, and momentum so you are predicting the next day
			#MUST have a trade period of only one day
			self.SecurityDF.index = self.SecurityDF.index.shift(1, freq = "D")
			self.SecurityDF.dly_momentum = self.SecurityDF.dly_momentum.shift(-1)
			self.SecurityDF.adj_close = self.SecurityDF.adj_close.shift(-1)
			self.SecurityDF.adj_volume = self.SecurityDF.adj_close.shift(-1)
			
			#Drop lost record because of shifting and convert label field
			self.SecurityDF.dropna(inplace = True)
			self.SecurityDF.dly_momentum = self.SecurityDF.dly_momentum.astype(bool)

			#Save adjusted close data for later
			self.AdjClose = self.SecurityDF.adj_close

			#Drop un-used columns after shifting has occurred
			self.SecurityDF.drop(['adj_close','adj_volume'], axis = 1, inplace = True)

		except Exception as e:
			print("\nERROR: Data pull failed:\n" + str(e)+"\n")

			# Record the error message where the stock ticker would be
			self._defaultDataPullFailure(e)
			
	def readCSVData(self):
		#Initial directory
		directory = "/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar/Economics_Thesis_EMH/Data/Index_Data/"

		#If there is a remote server, change directory accordingly
		if self.RemoteServer:
			directory = directory.replace("/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar","/home/LDAPdir/sshowalter18")

		#Change directory
		os.chdir(directory)

		#Read csv data, set index, and convert index to a datetime
		self.SecurityDF = pd.read_csv(self.StockTicker)
		self.SecurityDF.set_index("Date", inplace = True)
		self.SecurityDF.index = pd.to_datetime(self.SecurityDF.index)

		#Convert all columns to numbers, and coerce errors to NaN
		for column in self.SecurityDF.columns:
			self.SecurityDF[column] = pd.to_numeric(self.SecurityDF[column], errors = 'coerce')

		#Clear out any null or ill-formatted data
		self.NumNaNRecords += max(self.SecurityDF.isnull().sum())
		self.SecurityDF.dropna(inplace = True)

		#Trim dataframe to appropriate size
		self.SecurityDF = self.SecurityDF[(self.SecurityDF.index >= self.ScheduledDateStart) &
										  (self.SecurityDF.index <= self.ScheduledDateEnd)]


		#Drop the unnecessary columns, and add other attributes
		self.SecurityDF.columns = ['adj_open','adj_high', 'adj_low', 'adj_close', 'adj_volume']
		self.ActualDateStart = str(self.SecurityDF.index[0])[:11]
		self.ActualDateEnd = str(self.SecurityDF.index[-1])[:11]
		self.StatusMessage = "Success"


	# Initial API call to gain all security prices. 
	# All technical ratios will be derived from security data
	# Drops any and all non-essential metrics
	def getSecurityPrices(self):

		#Information about the date format
		date_format = "%Y-%m-%d"
		date_start = dt.datetime.strptime(self.ScheduledDateStart, date_format)
		date_end = dt.datetime.strptime(self.ScheduledDateEnd, date_format)
		data = quandl.get(("WIKI/" + self.StockTicker), trim_start = self.ScheduledDateStart, trim_end = self.ScheduledDateEnd)
		data.drop(data.columns[[0,1,2,3,4,5,6]], axis = 1, inplace = True)
		data.columns = ['adj_open','adj_high', 'adj_low', 'adj_close', 'adj_volume']

		#Final Informationa about data pulling
		self.ActualDateStart = str(data.index[0])[:11]
		self.ActualDateEnd = str(data.index[-1])[:11]
		self.StatusMessage = "Success"

		#Assign Dataframe to variable
		self.SecurityDF = data
		

	# Daily momentum (row label) sub-function
	def addDailyMomentum(self):
		self.SecurityDF['shifted_close'] = self.SecurityDF.adj_close.shift(1)
		self.SecurityDF['dly_momentum'] = self.SecurityDF.adj_close > self.SecurityDF.shifted_close
		self.SecurityDF.drop(['shifted_close'], axis = 1, inplace = True)

	# 10 Day moving average sub-function
	def add10DayMavg(self):
		self.SecurityDF['10D_mavg'] = pd.rolling_mean(self.SecurityDF.adj_close,10)

	# Exponentially weighted 10 day moving average sub-function
	def add10DayExpWeightedMavg(self):
		self.SecurityDF['10D_Wmavg'] = pd.ewma(self.SecurityDF.adj_close, span = 10)

	# 10 day momentum calculation sub-function
	def add10DayMomentum(self):
		self.SecurityDF['10dshifted_close'] = self.SecurityDF.adj_close.shift(10)
		self.SecurityDF['10D_Momentum'] = (self.SecurityDF.adj_close / self.SecurityDF['10dshifted_close'])*100
		self.SecurityDF.drop(['10dshifted_close'], axis = 1, inplace = True)

	# Adds stochastic K-percent figure to dataframe sub-function
	def add14DayStochasticKPercent(self):
		roll_min = self.SecurityDF.adj_low.rolling(14,min_periods = 14).min()
		roll_max = self.SecurityDF.adj_high.rolling(14,min_periods = 14).max()
		self.SecurityDF['14D_stoch_Kperc'] = ((self.SecurityDF.adj_close - roll_min)/(roll_max - roll_min)) * 100

	# Adds stochastic D-percent figure to dataframe (derived from k%) sub-function
	def addStochasticDPercent(self):
		self.SecurityDF['stoch_Dperc'] = pd.rolling_mean(self.SecurityDF['14D_stoch_Kperc'],3)

	# Relative strength index over a window of 14 days. sub-function
	def addRelativeStrengthIndex(self):
		self.SecurityDF['shifted_close'] = self.SecurityDF.adj_close.shift(1)
		self.SecurityDF['gain/loss'] = (self.SecurityDF.adj_close - self.SecurityDF.shifted_close) / self.SecurityDF.shifted_close

		# To get average gain and loss per period
		self.SecurityDF['gain'] = np.where(self.SecurityDF['gain/loss'] > 0,self.SecurityDF['gain/loss'],0)
		# Include a negative one here to reverse the sign of loss values
		self.SecurityDF['loss'] = np.where(self.SecurityDF['gain/loss'] <= 0,self.SecurityDF['gain/loss']*-1,0)

		# average gain and average loss
		avg_gain = pd.rolling_mean(self.SecurityDF.gain,14)
		avg_loss = pd.rolling_mean(self.SecurityDF.loss,14)

		#Drop unnecessary columns
		self.SecurityDF.drop(['gain/loss','gain','loss'], axis = 1, inplace = True)

		#Add rsi metric
		self.SecurityDF['14D_RSI'] = (100 - (100/ (1 + (avg_gain/avg_loss))))


	# Adds MACD histogram values, sub-function
	def addMACDHistogram(self):
		D12EWMACD = pd.ewma(self.SecurityDF.adj_close, span = 12)
		D26EWMACD = pd.ewma(self.SecurityDF.adj_close, span = 26)

		# Get 9 day exponential moving average of EWMACDLine
		EWMACDLine = D12EWMACD - D26EWMACD
		Signal_Line = pd.ewma(EWMACDLine, span = 9)

		# For debugging code
		# print(EWMACDLine)
		# print(Signal_Line)

		#Finalize addition to SecurityDF
		self.SecurityDF['EWMACD'] = EWMACDLine - Signal_Line

	# 
	def add14DayWilliamsRPercent(self):
		roll_min = self.SecurityDF.adj_low.rolling(14,min_periods = 14).min()
		roll_max = self.SecurityDF.adj_high.rolling(14,min_periods = 14).max()

		self.SecurityDF['14D_stock_Rperc'] = ((roll_max - self.SecurityDF.adj_close) / (roll_max - roll_min)) * -100

	# 7-Day ADL, sub-function
	def add7DayAccumulationDistributionLine(self):
		roll_min = self.SecurityDF.adj_low.rolling(7,min_periods = 7).min()
		roll_max = self.SecurityDF.adj_high.rolling(7,min_periods = 7).max()

		#Rolling volume, divided by 1000
		roll_vol_sum = self.SecurityDF.adj_volume.rolling(7,min_periods = 7).sum() / 1000

		# Money flow multiplier and money flow volume
		money_flow_mult = ((self.SecurityDF.adj_close - roll_min) - (roll_max - self.SecurityDF.adj_close)) / (roll_max - roll_min)
		money_flow_vol = roll_vol_sum * money_flow_mult

		# For debugging purposes
		# print(money_flow_mult.describe())

		# Iterates through to change A/D Line day to day
		for i in range(7,len(money_flow_vol)):
			money_flow_vol.iloc[i] = money_flow_vol.iloc[i-1] + money_flow_vol.iloc[i]

		self.SecurityDF['7D_ADL'] = money_flow_vol

	def addCommodityChannelIndex(self):
		typical_price = (self.SecurityDF.adj_close + self.SecurityDF.adj_high + self.SecurityDF.adj_low) / 3
		Constant = 0.015

		rolling_mean_TP_20D = pd.rolling_mean(typical_price,20)
		mean_deviation = abs(typical_price - rolling_mean_TP_20D)
		rolling_mean_MD = pd.rolling_mean(mean_deviation,20)

		# 0.015 is apparently the customary constant here, as seen in literature
		self.SecurityDF['20D_CCI'] = (typical_price - rolling_mean_TP_20D) / (Constant * rolling_mean_MD)


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
		self.NumCols = len(self.SecurityDF.columns)
		self.NumNaNRecords += max(self.SecurityDF.isnull().sum())

		# #Print security DF
		# print(self.SecurityDF.head())

		#Drop all NaN data
		self.SecurityDF.dropna(inplace = True)
		self.NumRows = len(self.SecurityDF.index)

		# Duration of API pull captured
		API_time_end = dt.datetime.utcnow()
		self.CollectionDuration = (API_time_end - self.utcDateTimeStart).total_seconds()

	#Changes technical trends to booleans with trending
	def convertWithTrending(self,dfColumn):
		return np.where(dfColumn > dfColumn.shift(1),1,-1)

	# Converts technical trends to booleans with certain bounds AND trending
	def convertWithBounds(self,dfColumn, lowerBound, upperBound):
		bool_greater_col = (dfColumn > dfColumn.shift(1))

		# Less than lower threshold (oversold) or (yesterday's indicator and less than upperBound), up, otherwise down
		return np.where(((dfColumn < lowerBound) | ((bool_greater_col) & (dfColumn < upperBound))),1,-1)

	# May do this later, once more of the model is built.
	def convertToTrendSpecific(self):

		# Add trend specific for moving averages
		self.SecurityDF['10D_mavg'] = np.where(self.SecurityDF['10D_mavg'] < self.SecurityDF.adj_close, 1, -1)
		self.SecurityDF['10D_Wmavg'] = np.where(self.SecurityDF['10D_Wmavg'] < self.SecurityDF.adj_close, 1, -1)

		# Add trend specific for momentum
		self.SecurityDF['10D_Momentum'] = np.where(self.SecurityDF['10D_Momentum'] > 100, 1, -1)

		#Convert remaining columns with helper functions
		self.SecurityDF['EWMACD'] = self.convertWithTrending(self.SecurityDF['EWMACD'])
		self.SecurityDF['7D_ADL'] = self.convertWithTrending(self.SecurityDF['7D_ADL'])
		self.SecurityDF['20D_CCI'] = self.convertWithBounds(self.SecurityDF['20D_CCI'],-200,200)
		self.SecurityDF['14D_stoch_Kperc'] = self.convertWithBounds(self.SecurityDF['14D_stoch_Kperc'],20,80)
		self.SecurityDF['stoch_Dperc'] = self.convertWithBounds(self.SecurityDF['stoch_Dperc'],20,80)
		self.SecurityDF['14D_stock_Rperc'] = self.convertWithBounds(self.SecurityDF['14D_stock_Rperc'],-80,-20)
		self.SecurityDF['14D_RSI'] = self.convertWithBounds(self.SecurityDF['14D_RSI'],30,70)

		#Change the time log for variable
		# Duration of API pull captured
		API_time_end = dt.datetime.utcnow()
		self.CollectionDuration = (API_time_end - self.utcDateTimeStart).total_seconds()

		




	









