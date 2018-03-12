import pandas as pd  
import numpy as np 
import os
import datetime as dt 
from MLModeler import Modeler
#import matplotlib.pyplot as plt


########################################################################################################################

# Read in interest rates (already been edited and refined)
#iRates = pd.read_csv("/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar/Economics_Thesis_EMH/Data/Index_Data/Tbill_Rates.csv", parse_dates = [0])

#For remote directory 
os.chdir("/home/LDAPdir/sshowalter18/Economics_Thesis_EMH/Data/Index_Data/")
iRates = pd.read_csv("Tbill_Rates.csv", parse_dates = [0])

#Set index of interest rate information
iRates.set_index("Date", drop = True ,inplace = True)

########################################################################################################################

class Trader():
	
	def __init__(self, modeler = None, 
					   principal = 100000,
					   #Fidelity investments, largest broker, rate for U.S. stocks
					   transCost = 4.95,
					   remoteServer = False):

		#Set server and principal values
		self.TransCost = transCost
		self.RemoteServer = remoteServer
		self.Principal = principal
		
	# Set the modeler (done in the tester)
	def setModeler(self, modeler):
		self.Modeler = modeler

	#Run the orchestration for the trading algorithm
	def runTrader(self):

		#Set trade log filename
		self.TradeLogFilename = (self.Modeler.StockCollector.StockTicker.replace(".csv","") + "-" 
								+ self.Modeler.Classifiers + "-"
								+ self.Modeler.ResLogFileRoot.replace("ResLog.csv","TradeLog.csv"))

		#Set trade data for trader
		self.TradeData = self.Modeler.TradeData

		#Add all trading performance attributes, pre-trade
		self.addPercentChangeAttributes()
		self.addLiquidity()
		self.addBuyHoldSellSignals()
		self.getInterestRates()

		#Run investing algorithm
		self.invest()

		#Get percent change in the portfolio
		self.getPortfolioPercChg()

		#Add the market returns benchmark in real dollars
		self.addMarketBenchmark()

		#Drop NaN values (only the first value)
		self.TradeData.dropna(inplace = True)

		#Print statement for debugging
		#print(self.TradeData.tail())

		#Get trade start and end dates
		self.TradeDateStart = self.TradeData.index[0]
		self.TradeDateEnd = self.TradeData.index[-1]

		#Get total number of transactions
		self.TotalTransactions = len(self.TradeData[self.TradeData.trans_costs == self.TransCost].index)

		#Get number of trading days
		self.TradeDayNum = len(self.TradeData.index)	

		#Get aggregate information about portfolio performance
		self.iRateReturn = ((1 + self.TradeData.iRate_1D.mean())**len(self.TradeData)) - 1

		#Calculate market return
		self.MarketReturn = (self.TradeData.adj_close[-1] / self.TradeData.adj_close[0]) - 1

		#Calculate portfolio return
		self.PortfolioReturn = (self.TradeData.EOD_total_value[-1] / self.Principal) - 1

		#Calculate volatility across the entire trading period (extrapoliated from day)
		self.Volatility = np.sqrt(len(self.TradeData.index)) * self.TradeData.port_perc_chg.std()

		#Calculate other performance ratios
		self.Beta = self.calculateBeta()
		self.Alpha = self.calculateAlpha()
		self.Sharpe = self.PortfolioReturn - self.iRateReturn
		self.Sortino = self.calculateSortino()
		
		#NOTE: volatility and returns are always over the entire timeframe

		#Save trade data
		self.saveTradeData()

		#Print trade data for debugging
		#print(self.TradeData.tail())

		#For visualizing
		#######################################################################
		# plt.plot(self.TradeData.index,self.TradeData.EOD_total_value)
		# plt.plot(self.TradeData.index,self.TradeData.market_benchmark)
		# plt.show()

		#######################################################################

	#Save trade data
	def saveTradeData(self):
		directory = "/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar/Economics_Thesis_EMH/Data/ResLogs/"

		#If there is a remote server, change directory accordingly
		if self.RemoteServer:
			directory = directory.replace("/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar","/home/LDAPdir/sshowalter18")

		#Change directory
		os.chdir(directory + self.Modeler.FolderName.replace("_MasterLog",""))	

		#Save data to csv
		self.TradeData.to_csv(self.TradeLogFilename)

	#Calculate beta of the portfolio
	def calculateBeta(self):

		#Calculate beta
		beta = self.TradeData.port_perc_chg.cov(self.TradeData.perc_chg) / self.TradeData.perc_chg.var()

		#Return beta
		return beta

	#Calculate beta of the portfolio
	def calculateAlpha(self):

		#Calculate alpha
		alpha = self.PortfolioReturn - (self.iRateReturn + (self.MarketReturn - self.iRateReturn)*self.Beta)

		#Return alpha
		return alpha

	#Calculate sortino with MAR = average 1-day risk free return
	def calculateSortino(self, MAR = "iRate"):
		if MAR == "iRate":
			MAR = self.TradeData.iRate_1D.mean()
		else:
			MAR == 0.0

		#Determine downside devs
		port_downside_devs = (self.TradeData.port_perc_chg[self.TradeData.port_perc_chg <= MAR] - MAR)**2

		#take the square root of (the sum of squared deviations from MAR divided by number of obs)
		downside_deviation = np.sqrt(port_downside_devs.sum() / len(port_downside_devs))

		sortino = (self.TradeData.port_perc_chg.mean() - self.TradeData.iRate_1D.mean()) / downside_deviation

		return sortino


	#Add day to day percent change in the sample
	def addPercentChangeAttributes(self):
		lagPrice = self.TradeData.adj_close.shift(1)
		self.TradeData['perc_chg'] = (self.TradeData.adj_close / lagPrice) - 1

	#Add liquidity logic column
	def addLiquidity(self):

		#Start on the first buy signal after the first item
		TradeDataSkipFirst = self.TradeData.iloc[1:,:]

		#When price first increases (jumps)
		firstPriceJump = min(TradeDataSkipFirst[TradeDataSkipFirst.Predictions == True].index)

		#Initialize the number of Trues (e.g. you are liquid)
		self.TradeData.loc[:firstPriceJump,'EOD_liquidity'] = True

		#For each row including and after the first "False"
		for row in range(len(self.TradeData[self.TradeData.EOD_liquidity == True]) - 1,len(self.TradeData)):

			#If it is the first row, initialize it
			if row == len(self.TradeData[self.TradeData.EOD_liquidity == True]) - 1:
				self.TradeData.EOD_liquidity[row] = False

			#Else run the iterative process
			else:
				if self.TradeData.Predictions[row] != self.TradeData.Predictions[row-1]:
					self.TradeData.EOD_liquidity[row] = not self.TradeData.EOD_liquidity[row-1]
				else:
					self.TradeData.EOD_liquidity[row] = self.TradeData.EOD_liquidity[row-1]

	def addBuyHoldSellSignals(self):
		lag_liquidity = self.TradeData.EOD_liquidity.shift(1)
		self.TradeData['trade_action'] = "Hold"

		#Make trade action buy
		self.TradeData.loc[min(self.TradeData[self.TradeData.Predictions == True].index), "trade_action"] = "Buy"

		#Situation where an individual sells 
		self.TradeData.trade_action[(self.TradeData.EOD_liquidity == True) & (lag_liquidity == False)] = "Sell"

		#Situation where individual buys
		self.TradeData.trade_action[(self.TradeData.EOD_liquidity == False) & (lag_liquidity == True)] = "Buy"

	def addMarketBenchmark(self):
		market_benchmark = (self.TradeData.adj_close / self.TradeData.adj_close[0]) * self.Principal

		#Remove the top item because of NaN record in first row
		market_benchmark = market_benchmark.iloc[1:]

		#Set column as market reference
		self.TradeData['market_benchmark'] = market_benchmark

	# Logic for buying stock
	def getBuySharesEquityCash(self,row):
		trans_costs = self.TransCost
		cash = row.EOD_cash - trans_costs
		shares =  (row.EOD_cash // row.adj_close)
		equity = row.adj_close * shares
		cash = row.EOD_cash - equity
		
		return shares, equity, cash, trans_costs

	# Logic for selling stock
	def getSellSharesEquityCash(self,row):
		#Transaction cost of fidelity, world's largest broker
		trans_costs = self.TransCost
		shares =  0
		equity = 0
		cash = row.EOD_cash + row.EOD_equity - trans_costs

		return shares, equity, cash, trans_costs

	# Logic for holding stock
	def getHoldSharesEquityCash(self,row):
		shares =  row.EOD_shares
		equity = row.EOD_equity
		cash = row.EOD_cash
		trans_costs = 0

		return shares, equity, cash, trans_costs

	#Get shares, equity, and cash orchestration
	def getSharesEquityCashOrch(self,row, signal):
		if (signal == "Buy"):
			return self.getBuySharesEquityCash(row)
		elif (signal == "Sell"):
			return self.getSellSharesEquityCash(row)
		else:
			return self.getHoldSharesEquityCash(row)

	#Join interest rates to Trading Dataframe
	def getInterestRates(self):
		self.TradeData = self.TradeData.join(iRates)
		self.TradeData.iRate_1D.fillna(self.TradeData.iRate_1D.mean(), inplace = True)

	def getPortfolioPercChg(self):
		#Get a lag of the portfolio performance to generate percent changes
		lagAlgoPortfolio = self.TradeData.EOD_total_value.shift(1)

		# Get percent changes of the portfolio
		self.TradeData['port_perc_chg'] = (self.TradeData.EOD_total_value / lagAlgoPortfolio) - 1

	#Get principal 
	def invest(self):
		self.TradeData['trans_costs'] = 0.0
		self.TradeData['EOD_shares'] = 0
		self.TradeData["EOD_cash"] = self.Principal + 0.0
		self.TradeData["EOD_equity"] = 0.0

		for row in range(1,len(self.TradeData)):

			#Get start of day shares information for Buy, Sell, Hold
			SOD_shares, SOD_equity, SOD_cash, trans_costs = self.getSharesEquityCashOrch(self.TradeData.iloc[row - 1], self.TradeData.trade_action[row])

			# The same becasue intraday trading not supported
			self.TradeData.EOD_shares[row] = SOD_shares

			#Equity updated for stock price changes
			self.TradeData.EOD_equity[row] = SOD_shares * self.TradeData.adj_close[row]

			#Cash updated based on risk free rate
			self.TradeData.EOD_cash[row] = SOD_cash * (1 + self.TradeData.iRate_1D[row])

			#Set transaction costs
			self.TradeData.trans_costs[row] = trans_costs

		self.TradeData["EOD_total_value"] = self.TradeData.EOD_cash + self.TradeData.EOD_equity










