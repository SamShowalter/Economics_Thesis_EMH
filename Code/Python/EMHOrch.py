from DataCollector import StockCollector
from AutoTrader import Trader
from Logger import Log 
from MLModeler import Modeler
import smtplib
from Tester import Test
import pandas as pd 
import os
import copy

###############################################################################################################################

# Send emails about progress
def sendProgressEmail(subject, message):
	#Establish server
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()

	#Log in to my email account
	server.login("dpudatascience@gmail.com", "Data4good!")

	#Send the final message
	final_message = 'Subject: {}\n\n{}'.format(subject, message)
	server.sendmail("dpudatascience@gmail.com", "samuelrshowalter@gmail.com", final_message)
	#server.sendmail("dpudatascience@gmail.com", "jgropp@depauw.edu", final_message)

	#Quit the server
	server.quit()

def generateProgressInformation(Test, ProgressInfo):
	pass
	


###############################################################################################################################




MasterLog = Log("Master_Log", "Results_Log",  
															  [[
															    #Data collection metadata
															    "Remote_Server",			#If execution run on remote server
															    "Execution_Date",			#Known to the collector as collection date
																"Execution_Time",			#Also known as collection time
																"Collection_Duration",
																"Modeler_Duration",
																"Trader_Duration",
																"Test_Duration",

																#Stock information -- request
																"Stock_Ticker",
																"Scheduled_Start_Date",
																"Scheduled_End_Date",

																#Stock information -- actual
																"Actual_Start_Date",
																"Actual_End_Date",
																"Row_Count",
																"Column_Count",
																"NaN_Row_Count",
																"Trend_Specific",
																"Status_Message",

																##-----  Modeler information  ---##

																#Modeler Meta-parameters
																"Models_Used",
																"SVM_Params",
																"RF_Estimators",
																"KNN_Neighbors",
																"Test_Period_Size", "Num_Test_Periods",
																"Total_Test_Years",

																#Modeler SVM Performance
																"SVM_TP", "SVM_FP", "SVM_TN", "SVM_FN",
																"SVM_Pos_Precision", "SVM_Neg_Precision",
																"SVM_Pos_Recall", "SVM_Neg_Recall",
																"SVM_Precision", "SVM_Recall",
																"SVM_Accuracy", "SVM_F_Measure",
																#12

																#Model Random Forest Performance   
																"RF_TP", "RF_FP", "RF_TN", "RF_FN",
																"RF_Pos_Precision", "RF_Neg_Precision",
																"RF_Pos_Recall", "RF_Neg_Recall",
																"RF_Precision", "RF_Recall",
																"RF_Accuracy", "RF_F_Measure", 
																#12

																#Model Gaussian Naive Bayes performance
																"GNB_TP", "GNB_FP", "GNB_TN", "GNB_FN",
																"GNB_Pos_Precision", "GNB_Neg_Precision",
																"GNB_Pos_Recall", "GNB_Neg_Recall",
																"GNB_Precision", "GNB_Recall",
																"GNB_Accuracy", "GNB_F_Measure",
																#12 

																#Model KNN performance
																"KNN_TP", "KNN_FP", "KNN_TN", "KNN_FN",
																"KNN_Pos_Precision", "KNN_Neg_Precision",
																"KNN_Pos_Recall", "KNN_Neg_Recall",
																"KNN_Precision", "KNN_Recall",
																"KNN_Accuracy", "KNN_F_Measure",
																#12

																#Model Logistic performance 
																"LOG_TP", "LOG_FP", "LOG_TN", "LOG_FN",
																"LOG_Pos_Precision", "LOG_Neg_Precision",
																"LOG_Pos_Recall", "LOG_Neg_Recall",
																"LOG_Precision", "LOG_Recall",
																"LOG_Accuracy", "LOG_F_Measure",

																##-----  Trader information  ---##

																#General trading metadata
																"Principal",
																"Transaction_Cost",
																"Trade_Start_Date",
																"Trade_End_Date",
																"Trade_Day_Num",
																"Total_Transactions",

																#Trading returns from difference assets
																"Risk_Free_Return",
																"Market_Return",
																"Portfolio_Return",

																#Volatility of Portfolio
																"Volatility",

																#Other performance attributes
																"Beta",
																"Alpha",
																"Sharpe",
																"Sortino",

																##-----  Filestore information  ---##

																#Results log filename
																"Res_Log_Filename",

																#Trade log filename
																"Trade_Log_Filename"]],

																#Results column names
																["Not Applicable"])

MLLog = Log("Master_Log",  "Results_Log",  
																#Collection columns names
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



###############################################################################################################################

#Get information about what stock tickers I can pull

# os.chdir("/Users/Sam/Documents/Depauw/04 Senior Year/Semester 2/EMH_Seminar/Economics_Thesis_EMH/Data/Index_Data")

# sp500 = pd.read_csv("SP500_Companies.csv")

# final_list = []
# for company in range(len(sp500)):
# 	print(company)
# 	try:
# 		print(quandl.get(("WIKI/" + sp500.iloc[company,0]), trim_start = "2017-03-02", trim_end = "2017-03-04"))
# 		final_list.append(sp500.iloc[company,0])
# 	except Exception as e:
# 		print(e)

# print(len(final_list),final_list)

###############################################################################################################################

#Index list
index_list = ['^IXIC.csv','^GSPC.csv','^RUT.csv','^DJI.csv']


#503 items
sp500list = ['MMM', 'ABT', 'ABBV', 'ACN', 'ATVI', 'AYI', 'ADBE', 'AAP', 'AES', 'AET', 'AMG', 'AFL', 
				'A', 'APD', 'AKAM', 'ALK', 'ALB', 'ALXN', 'ALLE', 'AGN', 'ADS', 'LNT', 'ALL', 'GOOGL', 
				'GOOG', 'MO', 'AMZN', 'AEE', 'AAL', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'ABC', 'AME', 
				'AMGN', 'APH', 'APC', 'ADI', 'ANTM', 'AON', 'APA', 'AIV', 'AAPL', 'AMAT', 'ADM', 'ARNC', 
				'AJG', 'AIZ', 'T', 'ADSK', 'ADP', 'AN', 'AZO', 'AVB', 'AVY', 'BHI', 'BLL', 'BAC', 'BCR', 
				'BAX', 'BBT', 'BDX', 'BBBY', 'BBY', 'BIIB', 'BLK', 'HRB', 'BA', 'BWA', 'BXP', 'BSX', 'BMY', 
				'AVGO', 'CHRW', 'CA', 'COG', 'CPB', 'COF', 'CAH', 'KMX', 'CCL', 'CAT', 'CBOE', 'CBG', 'CBS', 
				'CELG', 'CNC', 'CNP', 'CTL', 'CERN', 'CF', 'SCHW', 'CHTR', 'CHK', 'CVX', 'CMG', 'CB', 'CHD', 
				'CI', 'XEC', 'CINF', 'CTAS', 'CSCO', 'C', 'CFG', 'CTXS', 'CME', 'CMS', 'COH', 'KO', 'CTSH', 
				'CL', 'CMCSA', 'CMA', 'CAG', 'CXO', 'COP', 'ED', 'STZ', 'GLW', 'COST', 'COTY', 'CCI', 'CSRA', 
				'CSX', 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA', 'DE', 'DLPH', 'DAL', 'XRAY', 'DVN', 'DLR', 'DFS', 
				'DISCA', 'DISCK', 'DG', 'DLTR', 'D', 'DOV', 'DOW', 'DPS', 'DTE', 'DD', 'DUK', 'DNB', 'ETFC', 'EMN', 
				'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'EMR', 'ETR', 'EVHC', 'EOG', 'EQT', 'EFX', 'EQIX', 'EQR', 
				'ESS', 'EL', 'ES', 'EXC', 'EXPE', 'EXPD', 'ESRX', 'EXR', 'XOM', 'FFIV', 'FB', 'FAST', 'FRT', 'FDX', 
				'FIS', 'FITB', 'FSLR', 'FE', 'FISV', 'FLIR', 'FLS', 'FLR', 'FMC', 'FTI', 'FL', 'F', 'FTV', 'FBHS', 
				'BEN', 'FCX', 'FTR', 'GPS', 'GRMN', 'GD', 'GE', 'GGP', 'GIS', 'GM', 'GPC', 'GILD', 'GPN', 'GS', 'GT', 
				'GWW', 'HAL', 'HBI', 'HOG', 'HAR', 'HRS', 'HIG', 'HAS', 'HCA', 'HCP', 'HP', 'HSIC', 'HES', 'HPE', 'HOLX', 
				'HD', 'HON', 'HRL', 'HST', 'HPQ', 'HUM', 'HBAN', 'IDXX', 'ITW', 'ILMN', 'INCY', 'IR', 'INTC', 'ICE', 'IBM', 
				'IP', 'IPG', 'IFF', 'INTU', 'ISRG', 'IVZ', 'IRM', 'JBHT', 'JEC', 'SJM', 'JNJ', 'JCI', 'JPM', 'JNPR', 'KSU', 'K', 
				'KEY', 'KMB', 'KIM', 'KMI', 'KLAC', 'KSS', 'KHC', 'KR', 'LB', 'LLL', 'LH', 'LRCX', 'LEG', 'LEN', 'LUK', 'LVLT', 
				'LLY', 'LNC', 'LLTC', 'LKQ', 'LMT', 'L', 'LOW', 'LYB', 'MTB', 'MAC', 'M', 'MNK', 'MRO', 'MPC', 'MAR', 'MMC', 'MLM', 
				'MAS', 'MA', 'MAT', 'MKC', 'MCD', 'MCK', 'MJN', 'MDT', 'MRK', 'MET', 'MTD', 'KORS', 'MCHP', 'MU', 'MSFT', 'MAA', 
				'MHK', 'TAP', 'MDLZ', 'MON', 'MNST', 'MCO', 'MS', 'MSI', 'MUR', 'MYL', 'NDAQ', 'NOV', 'NAVI', 'NTAP', 'NFLX', 'NWL', 
				'NFX', 'NEM', 'NWSA', 'NWS', 'NEE', 'NLSN', 'NKE', 'NI', 'NBL', 'JWN', 'NSC', 'NTRS', 'NOC', 'NRG', 'NUE', 'NVDA', 
				'ORLY', 'OXY', 'OMC', 'OKE', 'ORCL', 'PCAR', 'PH', 'PDCO', 'PAYX', 'PYPL', 'PNR', 'PBCT', 'PEP', 'PKI', 'PRGO', 'PFE', 
				'PCG', 'PM', 'PSX', 'PNW', 'PXD', 'PNC', 'RL', 'PPG', 'PPL', 'PX', 'PCLN', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PSA', 
				'PHM', 'PVH', 'QRVO', 'QCOM', 'PWR', 'DGX', 'RRC', 'RTN', 'O', 'RHT', 'REG', 'REGN', 'RF', 'RSG', 'RAI', 'RHI', 'ROK', 
				'COL', 'ROP', 'ROST', 'RCL', 'R', 'SPGI', 'CRM', 'SCG', 'SLB', 'SNI', 'STX', 'SEE', 'SRE', 'SHW', 'SIG', 'SPG', 'SWKS', 'SLG', 
				'SNA', 'SO', 'LUV', 'SWN', 'SWK', 'SPLS', 'SBUX', 'STT', 'SRCL', 'SYK', 'STI', 'SYMC', 'SYF', 'SYY', 'TROW', 'TGT', 'TEL', 
				'TGNA', 'TDC', 'TSO', 'TXN', 'TXT', 'BK', 'CLX', 'COO', 'HSY', 'MOS', 'TRV', 'DIS', 'TMO', 'TIF', 'TWX', 'TJX', 'TMK', 'TSS', 
				'TSCO', 'TDG', 'RIG', 'TRIP', 'FOXA', 'FOX', 'TSN', 'USB', 'UDR', 'ULTA', 'UA', 'UAA', 'UNP', 'UAL', 'UNH', 'UPS', 'URI', 
				'UTX', 'UHS', 'UNM', 'URBN', 'VFC', 'VLO', 'VAR', 'VTR', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VIAB', 'V', 'VNO', 'VMC', 'WMT', 
				'WBA', 'WM', 'WAT', 'WEC', 'WFC', 'HCN', 'WDC', 'WU', 'WRK', 'WY', 'WHR', 'WFM', 'WMB', 'WLTW', 'WYN', 'WYNN', 'XEL', 'XRX', 
				'XLNX', 'XL', 'XYL', 'YHOO', 'YUM', 'ZBH', 'ZION', 'ZTS']


###############################################################################################################################
#TO CONVERT TO REMOTE DIRECTORY#
#  - Set remoteServer = True
#  - Change T_bill directory info in AutoTrader
#  - Make sure matplotlib is commented out and that there are no references to it
###############################################################################################################################

#data1 = StockCollector("^RUT.csv", "1988-01-01", "2018-01-01", trendSpecific = True)

for index in index_list:

	for i in range(1,8):
		try:

			t1 = Test(MasterLog,
				  StockCollector(index, "1988-01-01", "2018-01-01", trendSpecific = True),
				  Modeler(
				  		  test_period_size = 1,
				  		  specific_model = "RF",
				  		  n_estimators = i*20, 
				  		  n_neighbors = 20,
				  		  SVM_params = ('rbf',1,'auto'),
				  		  test_period_num = 2520),		#ten years
				  trader = Trader(50000),
				  remoteServer = True)


			sendProgressEmail("Index " + index.replace(".csv","") + " Full Run", "The script ran successfully and has stored " + index.replace(".csv","") + " stock data!\n" +
		  					  "This ran Random Forest specifically for " + str(i*20) + " trees over a period of 10 years.\n" +
		  					  "This data was also traded on to see if any returns were better than the market and used trending\n" +
		  					  "The program took " + str(t1.TestDuration) + " seconds to finish.")

		except Exception as e:
			sendProgressEmail("Data Failure", "The script has failed for " + index.replace(".csv","") + " stock data.\n")


MasterLog.saveMasterLog()









