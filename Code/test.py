from DataCollection import StockCollectionRecord
from Logger import Log


log = Log("Test_Collection_Log", "Test_Results_Log",  #Collection columns names
													  [["Execution_Date",
														"Execution_Time",
														"Execution_Duration_Sec",
														"Stock_Ticker",
														"Scheduled_Start_Date",
														"Scheduled_End_Date",
														"Actual_Start_Date",
														"Actual_End_Date",
														"Row_Count",
														"Column_Count",
														"NaN_Row_Count",
														"Trend_Specific",
														"Status_Message"]],

														#Results column names
														["Results"])

test1 = [StockCollectionRecord("aapl","2000-01-01","2017-07-07"),
		StockCollectionRecord("amzn","2000-01-01","2017-07-07"),
		StockCollectionRecord("gawern9s","2000-01-01","2017-07-07"),
		StockCollectionRecord("tsla","2000-01-01","2017-07-07"),
		StockCollectionRecord("jpm","2000-01-01","2017-07-07"),
		StockCollectionRecord("sbux","2000-01-01","2017-07-07"),
		StockCollectionRecord("nvda","2000-01-01","2017-07-07")]

test2 = [StockCollectionRecord("msft","2000-01-01","2017-07-07",trendSpecific = True),
		StockCollectionRecord("goog","2000-01-01","2017-07-07",trendSpecific = True),
		StockCollectionRecord("wmt","2000-01-01","2017-07-07",trendSpecific = True),
		StockCollectionRecord("luv","2000-01-01","2017-07-07",trendSpecific = True)]

for i in test1:
	log.addCollectionRecord(i)

for j in test2:
	log.addCollectionRecord(j)

#data1 = StockCollectionRecord("amzn","2000-01-01","2017-07-07")
data2 = StockCollectionRecord("gs","2000-01-01","2017-07-07",trendSpecific = True)

#print(data1.securityDF.describe())
print(log.CollectionLog)