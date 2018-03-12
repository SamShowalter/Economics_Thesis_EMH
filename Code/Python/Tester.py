########################################
# A test has a:
# - Modeler
# - Trader (potentially)
# - Logger (to store everything)
#
########################################

import pandas as pd 
import numpy as np 
from Logger import Log
from AutoTrader import Trader
import datetime as dt
import copy

class Test():

	def __init__(self, log,
					   data_collector,
					   modeler, 
					   trader = None, 
					   remoteServer = False):

		#Set Server for test
		self.RemoteServer = remoteServer

		#Time metadata
		self.ExecutionDateStart = dt.datetime.now().date()
		self.ExecutionTimeStart = dt.datetime.now().time()
		utc_exec_start = dt.datetime.utcnow()

		#Initialize and set server for log
		self.Log = log
		self.Log.RemoteServer = self.RemoteServer

		#Initialize and set server for Stock Collector
		self.DataCollector = data_collector
		self.DataCollector.RemoteServer = self.RemoteServer

		#Run Stock Collector
		self.DataCollector.runDataCollector()

		# Get data collection duration information done in data collection
		# Some weird compilation order makes times funky otherwise

		#Time the modeler
		utc_model_start = dt.datetime.utcnow()
		
		#Initialize modeler
		self.Modeler = modeler

		#Add sample to modeler and run model
		self.Modeler.setStockCollector(self.DataCollector)
		#print(self.Modeler.StockCollector)
		self.Modeler.RemoteServer = self.RemoteServer
		self.Modeler.MasterLogName = self.Log.MasterLogName
		self.Modeler.runModeler()

		#Mode duration metadata
		self.ModelDuration = (dt.datetime.utcnow() - utc_model_start).total_seconds()

		#If trader is not none, then trade with the algorithm
		if trader is not None:
			self.Trader = trader
			self.Trader.RemoteServer = self.RemoteServer
			self.Trader.setModeler(self.Modeler)
			self.Trader.runTrader()

		#If no trading is to occur, default trader for logging purposes
		else:
			self._defaultTrader()

		#Get trade duration metadata (subtract Model duration to get trade duration)
		self.TradeDuration = ((dt.datetime.utcnow() - utc_model_start).total_seconds() - self.ModelDuration)

		#Total test duration metadata
		self.TestDuration = (dt.datetime.utcnow() - utc_exec_start).total_seconds()
		
		#Add masterlog record
		self.Log.addMasterLogRecord(self)

	#Default trading information if no trading is to occur
	def _defaultTrader(self):
		#Default all trader values to nothing if none exists
		self.Trader = Trader()

		#Default metadata information
		self.Trader.Principal = 0
		self.Trader.TradeDateStart = 0
		self.Trader.TradeDateEnd = 0
		self.Trader.TradeDayNum = 0
		self.Trader.TotalTransactions = 0

		#Default returns from assets information
		self.Trader.iRateReturn = 0
		self.Trader.MarketReturn = 0
		self.Trader.PortfolioReturn = 0

		#Default volatility to zero
		self.Trader.Volatility = 0

		#Default other performance metrics to zero
		self.Trader.Beta = 0
		self.Trader.Alpha = 0
		self.Trader.Sharpe = 0
		self.Trader.Sortino = 0

		#Default message for trade log
		self.Trader.TradeLogFilename = "NO TRADING RUN"



		