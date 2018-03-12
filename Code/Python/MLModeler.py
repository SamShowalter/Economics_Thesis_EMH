import pandas as pd
import numpy as np
import datetime as dt
import os
import copy
from Logger import Log

# K-Nearest Neighbors
from sklearn.neighbors import KNeighborsClassifier

# Random Forest Classifier
from sklearn.ensemble import RandomForestClassifier

# Support Vector Machine model
from sklearn.svm import SVC

# Logistic Regression
from sklearn.linear_model import LogisticRegression

# Stochastic Gradient Descent Optimizer
from sklearn.linear_model import SGDClassifier

# Gaussian Naive Bayes Optimizer
from sklearn.naive_bayes import GaussianNB


MLLog = Log("Test_Collection_Log",  "Test_Results_Log",  
																#Results metadata names (need to fill out)
																["Not Applicable"],

																#Results column names
																[[
																#Execution metadata
																"Execution_Date",
																"Execution_Time",
																"Execution_Duration_Sec",

																#Sample information
																"Stock_Ticker",
																"Stock_Start_Date",
																"Stock_End_Date",
																"Trend_Specific",
																"Test_Period_Size",
																"Test_Period_Num",

																#Model Name
																"Model_Name",
																
																#Model performance
																"TP", "FP", "TN", "FN",
																"Pos_Precision", "Neg_Precision",
																"Pos_Recall", "Neg_Recall",
																"Precision", "Recall",
																"Accuracy", "F-Measure"]])

############################################################################################################################

class Modeler():

	def __init__(self,  
					    test_period_size = 1,
					    test_period_num = 100,				# Either 1 (day), 5 (week), 20 (month)
						n_neighbors = 5, 					# 1 = 100 day test period
						SVM_params = ('rbf',1,5), 			# 5 = 50 week (250 day) test period
						n_estimators = 80,					# 20 = 25 month (500 day) test period
						specific_model = None,				# Could also use MAX for full backtest
						remoteServer = False):				#Set remote server

		#Set remote server
		self.RemoteServer = remoteServer

		#Initialize self master log
		self.MasterLogName = "MASTER LOG NOT YET ASSIGNED"

		#Set model specifications and trading decision
		self.KNNeighbors = n_neighbors
		self.SVMParams = SVM_params
		self.TestPeriodSize = test_period_size
		self.TestPeriodNum = test_period_num
		self.RFEstimators = n_estimators
		self.SpecificModel = specific_model

		# self.Trading = trading
		self.Predictions = []

		#Creating logger object, map it to a server, and attribute a name
		self.Log = copy.deepcopy(MLLog)
		self.ResLogFileRoot =  str(dt.datetime.now().strftime("%H.%M.%S.%f"))[:10] + "-ResLog.csv"

	#Set the sample for a stock
	def setStockCollector(self,stock_collector):
		self.StockCollector = stock_collector

	#Run the modeler
	def runModeler(self):
		#Set server for Results log
		self.Log.RemoteServer = self.RemoteServer

		#Identify classifiers
		classifiers = [self.RF_train_test_model,
		               self.LOG_train_test_model,
		               self.GNB_train_test_model,
		               self.KNN_train_test_model,
		               self.SVM_train_test_model]

		
		#Informing the log what kind of tests the modeler did
		if self.SpecificModel is None:
			self.Classifiers = "All"
		else:
			self.Classifiers = self.SpecificModel 

		#Update result log filename
		self.ResLogFilename = (self.StockCollector.StockTicker + "-"
							  + self.Classifiers + "-"
							  + self.ResLogFileRoot)

		self.model_engine(classifiers)

	'''
	Make folder for Result Logs
	'''
	def makeFolder(self):
		directory = "/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar/Economics_Thesis_EMH/Data/ResLogs/"

		#If there is a remote server, change directory accordingly
		if self.RemoteServer:
			directory = directory.replace("/Users/Sam/Documents/Depauw/04_Senior_Year/Semester_2/EMH_Seminar","/home/LDAPdir/sshowalter18/")

		#Change directory
		os.chdir(directory)

		#Make new folder with MasterLog name
		self.FolderName = self.MasterLogName.replace("MasterLog.csv","") + "ResLogs"

		#Check to see if folder exists. If not, add it.
		try:
		    os.mkdir(self.FolderName)
		except:
			print("\nFolder already created.\n")
		    

	'''
	This is the sklearn KNN model. By passing in the train and test
	data, we can train the model and then test it. This function
	does exactly that and then returns the accuracy, as found
	with the function iter_accuracy
	'''
	def KNN_train_test_model(self, X_train, X_test, y_train, y_test):
		KNN_clf = KNeighborsClassifier(n_neighbors = self.KNNeighbors)
		KNN_clf.fit(X_train,y_train)
		predicted = KNN_clf.predict(X_test)
		if self.SpecificModel is not None:
			self.Predictions += list(predicted)
		actual = y_test

		return self.evaluatePerformance(actual,predicted)

	'''
	This is the sklearn SVM model. By passing in the train and test
	data, we can train the model and then test it. This function
	does exactly that and then returns the accuracy, as found
	with the function iter_accuracy
	'''
	def SVM_train_test_model(self, X_train, X_test, y_train, y_test):
		SVM_clf = SVC(kernel = self.SVMParams[0], C = self.SVMParams[1], gamma = self.SVMParams[2])
		SVM_clf.fit(X_train,y_train)
		predicted = SVM_clf.predict(X_test)
		if self.SpecificModel is not None:
			self.Predictions += list(predicted)
		actual = y_test

		return self.evaluatePerformance(actual,predicted)

	'''
	This is the sklearn GNB model. By passing in the train and test
	data, we can train the model and then test it. This function
	does exactly that and then returns the accuracy, as found
	with the function iter_accuracy
	'''
	def GNB_train_test_model(self, X_train, X_test, y_train, y_test):
		GNB_clf = GaussianNB()
		GNB_clf.fit(X_train, y_train)
		predicted = GNB_clf.predict(X_test)
		if self.SpecificModel is not None:
			self.Predictions += list(predicted)
		actual = y_test

		return self.evaluatePerformance(actual,predicted)

	'''
	This is the sklearn Random Forest model. By passing 
	in the train and test data, we can train the model and then test it. 
	This function does exactly that and then returns the accuracy, as 
	found with the function iter_accuracy.
	'''
	def RF_train_test_model(self, X_train, X_test, y_train, y_test):
		RF_clf = RandomForestClassifier(n_estimators = self.RFEstimators)
		RF_clf.fit(X_train, y_train)
		predicted = RF_clf.predict(X_test)
		if self.SpecificModel is not None:
			self.Predictions += list(predicted)
		actual = y_test

		return self.evaluatePerformance(actual,predicted)


	'''
	This is the sklearn Logistic Regression model. By passing 
	in the train and test data, we can train the model and then test it. 
	This function does exactly that and then returns the accuracy, as 
	found with the function iter_accuracy.
	'''
	def LOG_train_test_model(self, X_train, X_test, y_train, y_test):
		LOG_clf = LogisticRegression()
		LOG_clf.fit(X_train, y_train)
		predicted = LOG_clf.predict(X_test)
		if self.SpecificModel is not None:
			self.Predictions += list(predicted)
		actual = y_test

		return self.evaluatePerformance(actual,predicted)


	'''
	Train test split for algorithmic trading model. This allows
	the model to run iteratively and re-train the model after each period
	'''
	def train_test_split(self):

		print(self.StockCollector.SecurityDF)

		if (self.TestPeriodNum == "max"):
			
			#Must use a minimum of 10 years (2520 work days) of training data to start
			self.TestPeriodNum = (len(self.StockCollector.SecurityDF) - 2520) // self.TestPeriodSize

		#Get test bounds
		testBounds = self.TestPeriodNum*self.TestPeriodSize

		#Total number of years, kept as a float (can be rounded later)
		#252 is the number of work days in a year, roughly
		self.TotalTestYears = len(self.StockCollector.SecurityDF.iloc[-testBounds:,:]) / 252

		#Training data and testing data for fitting the model
		X_train = self.StockCollector.SecurityDF.iloc[:-testBounds,:-1]
		y_train = self.StockCollector.SecurityDF.iloc[:-testBounds,-1]

		#Test information and the actual answers to determine accuracy
		self.AdjClose = self.StockCollector.AdjClose.iloc[-testBounds:,]
		X_test = self.StockCollector.SecurityDF.iloc[-testBounds:,:-1]
		y_test = self.StockCollector.SecurityDF.iloc[-testBounds:,-1]

		return X_train, X_test, y_train, y_test

	'''
	returns accuracy of the sample
	'''
	def accuracy(self, actual, predicted):
		return (actual == predicted).value_counts().get(True,0) / actual.size


	'''
	Positive precision as a function of True Positive and False Positive
	'''
	def posPrecision(self,TP, FP):
		try:
			return TP / (TP + FP)
		except:
			return 0


	'''
	Negative precision as a function of True Negative and False Negative
	'''
	def negPrecision(self,TN, FP):
		try:
			return TN / (TN + FP)
		except:
			return 0


	'''
	Positive recall as a function of True Positive and False Negative
	'''
	def posRecall(self,TP, FN):
		try:
			return TP / (TP + FN)
		except:
			return 0


	'''
	Precision as a function of positive and negative precision
	'''
	def precision(self,pPrecision, nPrecision):
		return (pPrecision * 0.5) + (nPrecision * 0.5)


	'''
	Recall as a function of positive and negative recall
	'''
	def recall(self,pRecall, nRecall):
		return (pRecall * 0.5) + (nRecall * 0.5)


	'''
	Negative precision as a function of True Negative and False Positive
	'''
	def negRecall(self,TN, FP):
		
		try:
			return TN / (TN + FP)
		except:
			return 0

	'''
	F-measure as a function of precision and recall
	'''
	def fMeasure(self,precision, recall):
		if (precision + recall) == 0:
			return 0

		return (2 * precision * recall) / (precision + recall)

	'''
	Evaluate performance of a test.
	'''
	def evaluatePerformance(self,actual, predicted):

		#Results dataframe
		resultsDF = pd.DataFrame(actual,predicted)

		# Accuracy for the whole test
		accuracy = self.accuracy(actual,predicted)

		# True positive, False positive, True negative, False negative
		TP = ((actual == 1) & (predicted == 1)).value_counts().get(True,0)
		FP = ((actual == 1) & (predicted == 0)).value_counts().get(True,0) 
		TN = ((actual == 0) & (predicted == 0)).value_counts().get(True,0)
		FN = ((actual == 0) & (predicted == 1)).value_counts().get(True,0)

		# Precision and recall metrics (positive and negative)
		posPrecision = self.posPrecision(TP,FP)
		negPrecision = self.negPrecision(TN,FN)
		posRecall = self.posRecall(TP, FN)
		negRecall = self.negRecall(TN, FP)

		# Weighted average total for precision and recall
		precision = self.precision(posPrecision, negPrecision)
		recall = self.recall(posRecall, negRecall)

		# F-measure for the dataset
		fMeasure = self.fMeasure(precision, recall)

		# Return all of these values to the dataset. for DEBUGGING
		#print(TP, FP, TN, FN, posPrecision, negPrecision, posRecall, negRecall, precision, recall, accuracy, fMeasure)

		#Update predicted values


		#Return the performance of the model
		return (TP, FP, TN, FN, posPrecision, negPrecision, posRecall, negRecall, precision, recall, accuracy, fMeasure)

	'''
	Engine of the model that allows for the dataset to
	iteratively be re-training after each fold is tested
	and recorded.

	Test days:
		- 1 day for daily updates
		- 7 days for weekly updates
		- 30 days for monthly updates
	'''
	def kFoldCrossValidationTest(self, classifier, model_tag):
		X_train, X_test, y_train, y_test = self.train_test_split()

		#Master test set for trading
		self.TradeData = X_test
		y_test_master = y_test

		#For debugging purposes
		#print(max(X_train.isnull().sum()),y_train.isnull().sum(),max(X_test.isnull().sum()),y_test.isnull().sum())

		#Metadata and collection incormation for results
		res_list = []

		#Iteratre through every test period and make predictions
		for fold in range(self.TestPeriodSize,self.TestPeriodNum*self.TestPeriodSize + self.TestPeriodSize,self.TestPeriodSize):

			# Time the execution
			timeStart = dt.datetime.utcnow()
			
			#Find records to test
			X_pred = X_test.iloc[:self.TestPeriodSize,]
			y_pred = y_test.iloc[:self.TestPeriodSize,]

			#Get the accuracy of the classifier
			self.ModelPerf = classifier(X_train,X_pred,y_train,y_pred)

			# Change the train samples
			X_train = X_train.append(X_pred)
			y_train = y_train.append(y_pred)

			# Change the test samples
			X_test = X_test.iloc[self.TestPeriodSize:,]
			y_test = y_test.iloc[self.TestPeriodSize:,]

			# Print statement for debugging
			print(len(X_pred),len(y_pred),len(X_train),len(X_test),len(y_train),len(y_test), self.ModelPerf[10])

			# Finish time for execution
			timeEnd = dt.datetime.utcnow()

			#Duration for execution
			self.ModelDuration = (timeEnd - timeStart).total_seconds()

			#Add a record to the logger
			self.Log.addResultRecord(self)

			#Add the accuracy of the model to the list of results
			res_list.append(self.ModelPerf)

		if self.SpecificModel is not None:
			#Creates the final predictions dataframe
			self.Predictions = pd.DataFrame(self.Predictions,columns = ["Predictions"])
			self.Predictions.set_index(self.TradeData.index, inplace = True)

			#Generates all information necessary for trading
			#self.TradeData.adj_close
			self.TradeData = pd.concat([self.AdjClose,self.Predictions,y_test_master], axis = 1)

			print(self.TradeData)

			print(len(self.TradeData[self.TradeData.Predictions == self.TradeData.dly_momentum])/len(self.TradeData))

			#print(self.TradeData)

		return res_list

	'''
	Main engine of the model. For each model specified above, this 
	function will run it and store the accuracy data as a dictionary.
	The keys for this dictionary are the names of the functions above,
	before the first underscore. This function allows you to specify
	the number of samples you would like to collect, the test ratio for
	how much of the dataset you want to predict, and a list of the
	models that you want to provide. For this model we are going to predict
	all five.
	'''
	def model_engine(self,classifiers):
		#Train test split for the dataset
		X_train, X_test, y_train, y_test = self.train_test_split()

		#Initialize the results dictionary
		results_dict = {}

		#Make directory for folder names
		self.makeFolder()

		#Iterate through the models
		for classifier in classifiers:

			#Name of the model plus the 
			model_tag = classifier.__name__.rsplit('_')[0]
			self.ModelName = model_tag

			#Check for specific models
			if self.SpecificModel is not None and self.SpecificModel != model_tag:
				continue

			#Store results from the simulation as a dictionary
			results_dict[model_tag] = self.kFoldCrossValidationTest(classifier,model_tag)

			#Save Results Log
			self.Log.saveResultsLog(self.ResLogFilename, self.FolderName.replace(".csv",""))

		#Format and store the average results
		self.resultsDF = pd.DataFrame.from_dict(results_dict)
		averageResults = self.resultsDF.apply(lambda col: tuple(map(np.mean, zip(*col))),axis = 0).to_dict()

		#Store average results for each model (order does not matter because of keys)
		self.SVMPerf = averageResults.get('SVM',(0,0,0,0,0,0,0,0,0,0,0,0))
		self.RFPerf = averageResults.get('RF',(0,0,0,0,0,0,0,0,0,0,0,0))
		self.GNBPerf = averageResults.get('GNB',(0,0,0,0,0,0,0,0,0,0,0,0))
		self.KNNPerf = averageResults.get('KNN',(0,0,0,0,0,0,0,0,0,0,0,0))
		self.LOGPerf = averageResults.get('LOG',(0,0,0,0,0,0,0,0,0,0,0,0))
