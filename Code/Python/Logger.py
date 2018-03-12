import datetime as dt 
import pandas as pd 
import os

class Log():

	# Collection Log tracks the information about the datasets 
	# Being collected by API and ensures that all meta-data information 
	# is stored.
	def __init__(self, master_log_name, 
					   res_log_name, 
					   master_col_names, 
					   res_col_names,
					   remoteServer = False):

		#Give names to logs
		self.MasterLogName = str(dt.datetime.now().strftime("%H.%M.%S")) + "-MasterLog.csv"

		#Set server
		self.RemoteServer = remoteServer

		#Two DataFrame logs for performance and data collection
		self.MasterLog = pd.DataFrame(columns = master_col_names)
		self.ResLog = pd.DataFrame(columns = res_col_names)

	# Add a record of an API pull from Quandl to the log
	def addMasterLogRecord(self, test):
		new_record_df = pd.DataFrame(
								      [[
								       ##-----  Data Collection Information  ---##

								       #Data Collection metadata
								       test.RemoteServer,
								       test.DataCollector.CollectionDate,
								       test.DataCollector.CollectionTimeStart,
								       test.DataCollector.CollectionDuration,
								       test.ModelDuration,
								       test.TradeDuration,
								       test.TestDuration,

								       #Stock information -- request
									   test.DataCollector.StockTicker,
									   test.DataCollector.ScheduledDateStart,
									   test.DataCollector.ScheduledDateEnd,
									   
									   #Stock information -- actual
									   test.DataCollector.ActualDateStart,
									   test.DataCollector.ActualDateEnd,
									   test.DataCollector.NumRows,
									   test.DataCollector.NumCols,
									   test.DataCollector.NumNaNRecords,
									   test.DataCollector.TrendSpecific,
									   test.DataCollector.StatusMessage,

									   ##-----  Modeler information  ---##

									   #Information from modeler about parameters
								       test.Modeler.Classifiers,
								       test.Modeler.SVMParams,
								       test.Modeler.RFEstimators,
								       test.Modeler.KNNeighbors,
								       test.Modeler.TestPeriodSize, test.Modeler.TestPeriodNum,
								       test.Modeler.TotalTestYears,


									   #Modeler information about Support vector machine
								       test.Modeler.SVMPerf[0],		#TP
								       test.Modeler.SVMPerf[1],		#FP
								       test.Modeler.SVMPerf[2],		#TN
								       test.Modeler.SVMPerf[3],		#FN
								       test.Modeler.SVMPerf[4],		#Positive precision
								       test.Modeler.SVMPerf[5],		#Negative precision
								       test.Modeler.SVMPerf[6],		#Positive recall
								       test.Modeler.SVMPerf[7],		#Negative recall
								       test.Modeler.SVMPerf[8],		#Precision
								       test.Modeler.SVMPerf[9],		#Recall
								       test.Modeler.SVMPerf[10],	#Accuracy
								       test.Modeler.SVMPerf[11],	#F-measure

								       #Modeler information about Random forest
								       test.Modeler.RFPerf[0],		#TP
								       test.Modeler.RFPerf[1],		#FP
								       test.Modeler.RFPerf[2],		#TN
								       test.Modeler.RFPerf[3],		#FN
								       test.Modeler.RFPerf[4],		#Positive precision
								       test.Modeler.RFPerf[5],		#Negative precision
								       test.Modeler.RFPerf[6],		#Positive recall
								       test.Modeler.RFPerf[7],		#Negative recall
								       test.Modeler.RFPerf[8],		#Precision
								       test.Modeler.RFPerf[9],		#Recall
								       test.Modeler.RFPerf[10],		#Accuracy
								       test.Modeler.RFPerf[11],		#F-measure

								       #Modeler information about Gaussian Naive Bayes
								       test.Modeler.GNBPerf[0],		#TP
								       test.Modeler.GNBPerf[1],		#FP
								       test.Modeler.GNBPerf[2],		#TN
								       test.Modeler.GNBPerf[3],		#FN
								       test.Modeler.GNBPerf[4],		#Positive precision
								       test.Modeler.GNBPerf[5],		#Negative precision
								       test.Modeler.GNBPerf[6],		#Positive recall
								       test.Modeler.GNBPerf[7],		#Negative recall
								       test.Modeler.GNBPerf[8],		#Precision
								       test.Modeler.GNBPerf[9],		#Recall
								       test.Modeler.GNBPerf[10],	#Accuracy
								       test.Modeler.GNBPerf[11],	#F-measure
								       
								       #Modeler information about K-Nearest Neighbors
								       test.Modeler.KNNPerf[0],		#TP
								       test.Modeler.KNNPerf[1],		#FP
								       test.Modeler.KNNPerf[2],		#TN
								       test.Modeler.KNNPerf[3],		#FN
								       test.Modeler.KNNPerf[4],		#Positive precision
								       test.Modeler.KNNPerf[5],		#Negative precision
								       test.Modeler.KNNPerf[6],		#Positive recall
								       test.Modeler.KNNPerf[7],		#Negative recall
								       test.Modeler.KNNPerf[8],		#Precision
								       test.Modeler.KNNPerf[9],		#Recall
								       test.Modeler.KNNPerf[10],	#Accuracy
								       test.Modeler.KNNPerf[11],	#F-measure

								       #Modeler information about Logistic Regression
								       test.Modeler.LOGPerf[0],		#TP
								       test.Modeler.LOGPerf[1],		#FP
								       test.Modeler.LOGPerf[2],		#TN
								       test.Modeler.LOGPerf[3],		#FN
								       test.Modeler.LOGPerf[4],		#Positive precision
								       test.Modeler.LOGPerf[5],		#Negative precision
								       test.Modeler.LOGPerf[6],		#Positive recall
								       test.Modeler.LOGPerf[7],		#Negative recall
								       test.Modeler.LOGPerf[8],		#Precision
								       test.Modeler.LOGPerf[9],		#Recall
								       test.Modeler.LOGPerf[10],	#Accuracy
								       test.Modeler.LOGPerf[11],	#F-measure

								       ##-----  Trader information  ---##

								       #Get introductory information (metadata)
								       test.Trader.Principal,
								       test.Trader.TransCost,
								       test.Trader.TradeDateStart,
								       test.Trader.TradeDateEnd,
								       test.Trader.TradeDayNum,
								       test.Trader.TotalTransactions,

								       #Get returns of different assets
								       test.Trader.iRateReturn,
								       test.Trader.MarketReturn,
								       test.Trader.PortfolioReturn,

								       #Trading volatility across entire period
								       test.Trader.Volatility,

								       #Other performance ratios
								       test.Trader.Beta,
								       test.Trader.Alpha,
								       test.Trader.Sharpe,
								       test.Trader.Sortino,

								       #Results Log filename for the modeler
								       test.Modeler.ResLogFilename,

								       #Trade Log file name for the trader
								       test.Trader.TradeLogFilename]],

									   #Add the Collection Log Column Names
									   columns = self.MasterLog.columns)

		self.MasterLog = pd.concat([self.MasterLog ,new_record_df], axis = 0)
		self.MasterLog.reset_index(drop = True, inplace = True)

	def addResultRecord(self, model):
		new_results_df = pd.DataFrame(
								      [[

								      	#Execution metadata
								      	dt.datetime.now().date(),
								       	dt.datetime.now().time(),
								       	model.ModelDuration,

								       	#Sample information
										model.StockCollector.StockTicker,
										model.StockCollector.ActualDateStart,
										model.StockCollector.ActualDateEnd,
										model.StockCollector.TrendSpecific,
										model.TestPeriodSize,
										model.TestPeriodNum,

										#Model information
										model.ModelName,

										#Model performance
										model.ModelPerf[0],		#TP
								       	model.ModelPerf[1],		#FP
								       	model.ModelPerf[2],		#TN
								       	model.ModelPerf[3],		#FN
								       	model.ModelPerf[4],		#Positive precision
								       	model.ModelPerf[5],		#Negative precision
								       	model.ModelPerf[6],		#Positive recall
								       	model.ModelPerf[7],		#Negative recall
								       	model.ModelPerf[8],		#Precision
								       	model.ModelPerf[9],		#Recall
								       	model.ModelPerf[10],	#Accuracy
								       	model.ModelPerf[11]		#F-measure
										]],

									   #Add the Collection Log Column Names
									   columns = self.ResLog.columns)

		self.ResLog = pd.concat([self.ResLog, new_results_df], axis = 0)
		self.ResLog.reset_index(drop = True, inplace = True)

	# Save the collection log as a csv
	def saveMasterLog(self):

		directory = "/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar/Economics_Thesis_EMH/Data/MasterLogs/"

		#If there is a remote server, change directory accordingly
		if self.RemoteServer:
			directory = directory.replace("/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar","/home/LDAPdir/sshowalter18")

		#Change directory
		os.chdir(directory)

		#Save master log as a csv
		self.MasterLog.to_csv(self.MasterLogName, sep = ",")

	# Save the results log as a csv
	def saveResultsLog(self, resLogName, folderName):
		directory = "/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar/Economics_Thesis_EMH/Data/ResLogs/"

		#If there is a remote server, change directory accordingly
		if self.RemoteServer:
			directory = directory.replace("/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar","/home/LDAPdir/sshowalter18")

		#Change directory
		os.chdir(directory + folderName.replace("-MasterLog",""))

		#Save the log
		self.ResLog.to_csv(resLogName, sep = ",")



