from DataCollector import StockCollector
from Logger import Log 
from MLModeler import Modeler
import copy

MasterLog = Log("Test_Collection_Log", "Test_Metadata",  "Test_Results_Log",  #Collection columns names
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

																#Results metadata names (need to fill out)
																["Test Metadata"],

																#Results column names
																["Not Applicable"])

MLLog = Log("Test_Collection_Log", "Test_Metadata",  "Test_Results_Log",  
																#Collection columns names
															  	["Not Applicable"],

																#Results metadata names (need to fill out)
																["Not Applicable"],

																#Results column names
																[["Execution_Date",
																"Execution_Time",
																"Execution_Duration_Sec",
																"Stock_Ticker",
																"Stock_Start_Date",
																"Stock_End_Date",
																"Model_Tag",
																"Trend_Specific",
																"Test_Period_Years",
																"Model_Specific_Info",
																"Accuracy"]])

# test1 = [StockCollector("aapl","2000-01-01","2017-07-07"),
# 		StockCollector("amzn","2000-01-01","2017-07-07"),
# 		StockCollector("gawern9s","2000-01-01","2017-07-07"),
# 		StockCollector("tsla","2000-01-01","2017-07-07"),
# 		StockCollector("jpm","2000-01-01","2017-07-07"),
# 		StockCollector("sbux","2000-01-01","2017-07-07"),
# 		StockCollector("nvda","2000-01-01","2017-07-07")]

# test2 = [StockCollector("msft","2000-01-01","2017-07-07",trendSpecific = True),
# 		StockCollector("goog","2000-01-01","2017-07-07",trendSpecific = True),
# 		StockCollector("wmt","2000-01-01","2017-07-07",trendSpecific = True),
# 		StockCollector("luv","2000-01-01","2017-07-07",trendSpecific = True)]

# for i in test1:
# 	log.addCollectionRecord(i)

# for j in test2:
# 	log.addCollectionRecord(j)

data1 = StockCollector("amzn","2000-01-01","2018-01-01")
#data2 = StockCollector("goog","2000-01-01","2018-01-01",trendSpecific = False)

MasterLog.addCollectionRecord(data1)
#MasterLog.addCollectionRecord(data2)

#print(MasterLog.CollectionLog)

testML1 = Modeler(data1, copy.deepcopy(MLLog), test_period_fold_size = 5)

#testML2 = Modeler(data2, copy.deepcopy(MLLog))
#print(testML1.Log.ResLog)

print(testML1.resultsDF.describe())
#print(testML2.resultsDF.describe())

# print(data1.securityDF.describe())
# print(log.CollectionLog)

