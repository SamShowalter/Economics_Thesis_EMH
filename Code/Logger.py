import os
import datetime as dt 
import pandas as pd 

class Log():

	# Collection Log tracks the information about the datasets 
	# Being collected by API and ensures that all meta-data information 
	# is stored.
	def __init__(self, collectionLogName, resultsLogName, collectionColNames, resColNames):

		#Two DataFrame logs for performance and data collection
		self.CollectionLog = pd.DataFrame(columns = collectionColNames)
		self.ResultsLog = pd.DataFrame(columns = resColNames)

	# Add a record of an API pull from Quandl to the log
	def addCollectionRecord(self, record):
		new_record_df = pd.DataFrame(
								      [[record.ExecutionDate,
								       record.ExecutionTimeStart,
								       record.PullDuration,
									   record.StockTicker,
									   record.ScheduledDateStart,
									   record.ScheduledDateEnd,
									   record.ActualDateStart,
									   record.ActualDateEnd,
									   record.NumRows,
									   record.NumCols,
									   record.NumNaNRecords,
									   record.TrendSpecific,
									   record.StatusMessage]],

									   #Add the Collection Log Column Names
									   columns = self.CollectionLog.columns)

		self.CollectionLog = pd.concat([self.CollectionLog ,new_record_df], axis = 0)
		self.CollectionLog.reset_index(drop = True, inplace = True)

	# Save the collection log as a csv
	def saveCollectionLog(self):
		self.CollectionLog.to_csv(logName + "_" + str(dt.datetime.now()) + "_CollectionLog.csv", sep = ",")

	# Save the results log as a csv
	def saveResultsLog(self):
		self.CollectionLog.to_csv(logName + "_" + str(dt.datetime.now()) + "_CollectionLog.csv", sep = ",")



