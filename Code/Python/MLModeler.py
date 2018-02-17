import pandas as pd 
import numpy as np 
import datetime as dt
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


class Modeler():

	def __init__(self,  stockCollector,
						log,
					    test_period_fold_size = 1,			# Either 1 (day), 5 (week), 20 (month)
						n_neighbors = 5, 					# 1 = 100 day test period
						SVMparams = ('rbf',1,5), 			# 5 = 50 week (250 day) test period
						n_estimators = 80,					# 20 = 25 month (500 day) test period
						specificModel = None):

		self.StockCollector = stockCollector
		self.KNNeighbors = n_neighbors
		self.SVMParams = SVMparams
		self.TestPeriodFoldSize = test_period_fold_size
		self.RFEstimators = n_estimators
		self.SpecificModel = specificModel
		self.Log = log

		#Dictionary to keep track of appropriate sample size
		self.KFoldDict = {1:101,5:255,20:520}

		classifiers = [self.RF_train_test_model,
		               self.LOG_train_test_model,
		               self.GNB_train_test_model,
		               self.KNN_train_test_model,
		               self.SVM_train_test_model]

		self.model_engine(classifiers)



	'''
	This is the sklearn KNN model. By passing in the train and test
	data, we can train the model and then test it. This function
	does exactly that and then returns the accuracy, as found
	with the function iter_accuracy
	'''
	def KNN_train_test_model(self, X_train, X_test, y_train, y_test):
		KNN_clf = KNeighborsClassifier(n_neighbors = self.KNNeighbors)
		KNN_clf.fit(X_train,y_train)
		predicted = list(KNN_clf.predict(X_test))
		actual = list(y_test)

		accuracy = self.iter_accuracy(actual,predicted)

		return accuracy

	'''
	This is the sklearn SVM model. By passing in the train and test
	data, we can train the model and then test it. This function
	does exactly that and then returns the accuracy, as found
	with the function iter_accuracy
	'''
	def SVM_train_test_model(self, X_train, X_test, y_train, y_test):
		SVM_clf = SVC(kernel = self.SVMParams[0], C = self.SVMParams[1], gamma = self.SVMParams[2])
		SVM_clf.fit(X_train,y_train)
		predicted = list(SVM_clf.predict(X_test))
		actual = list(y_test)

		accuracy = self.iter_accuracy(actual,predicted)

		return accuracy

	'''
	This is the sklearn GNB model. By passing in the train and test
	data, we can train the model and then test it. This function
	does exactly that and then returns the accuracy, as found
	with the function iter_accuracy
	'''
	def GNB_train_test_model(self, X_train, X_test, y_train, y_test):
		GNB_clf = GaussianNB()
		GNB_clf.fit(X_train, y_train)
		predicted = list(GNB_clf.predict(X_test))
		actual = list(y_test)

		accuracy = self.iter_accuracy(actual,predicted)

		return accuracy

	'''
	This is the sklearn Random Forest model. By passing 
	in the train and test data, we can train the model and then test it. 
	This function does exactly that and then returns the accuracy, as 
	found with the function iter_accuracy.
	'''
	def RF_train_test_model(self, X_train, X_test, y_train, y_test):
		RF_clf = RandomForestClassifier(n_estimators = self.RFEstimators)
		RF_clf.fit(X_train, y_train)
		predicted = list(RF_clf.predict(X_test))
		actual = list(y_test)

		accuracy = self.iter_accuracy(actual,predicted)

		return accuracy


	'''
	This is the sklearn Logistic Regression model. By passing 
	in the train and test data, we can train the model and then test it. 
	This function does exactly that and then returns the accuracy, as 
	found with the function iter_accuracy.
	'''
	def LOG_train_test_model(self, X_train, X_test, y_train, y_test):
		LOG_clf = LogisticRegression()
		LOG_clf.fit(X_train, y_train)
		predicted = list(LOG_clf.predict(X_test))
		actual = list(y_test)

		accuracy = self.iter_accuracy(actual,predicted)

		return accuracy


	'''
	Train test split for algorithmic trading model. This allows
	the model to 
	'''
	def train_test_split(self,dataset):
		testBounds = self.KFoldDict[self.TestPeriodFoldSize]

		#Training data and testing data for fitting the model
		X_train = dataset.iloc[:-testBounds,:-1]
		y_train = dataset.iloc[:-testBounds,-1]

		#Test information and the actual answers to determine accuracy
		X_test = dataset.iloc[-testBounds:,:-1]
		y_test = dataset.iloc[-testBounds:,-1]

		return X_train, X_test, y_train, y_test


	'''
	This model iteratively returns a single value,
	the accuracy of the model as found by 
	num_correct/tot_num_samples. This is the function
	that will be called iteratively when the sampling
	engine runs for all sklearn models. Inputs are 
	actual labels, and predicted labels.
	'''
	def iter_accuracy(self,actual, predicted):
		correct_count = 0
		for i in range(len(actual)):
			if actual[i] == predicted[i]:
				correct_count += 1
		accuracy = correct_count/len(actual)
		return accuracy

	'''
	Engine of the model that allows for the dataset to
	iteratively be re-training after each fold is tested
	and recorded.

	Test days:
		- 1 day for daily updates
		- 7 days for weekly updates
		- 30 days for monthly updates
	'''
	def kFoldCrossValidationTest(self, classifier, modelTag):
		X_train, X_test, y_train, y_test = self.train_test_split(self.StockCollector.securityDF)

		#print(max(X_train.isnull().sum()),y_train.isnull().sum(),max(X_test.isnull().sum()),y_test.isnull().sum())

		#Metadata and collection incormation
		accuracy_list = []
		modelTag = classifier.__name__.rsplit('_')[0]

		for fold in range(self.TestPeriodFoldSize,self.KFoldDict[self.TestPeriodFoldSize],self.TestPeriodFoldSize):

			# Time the execution
			timeStart = dt.datetime.utcnow()
			
			#Find records to test
			X_pred = X_test.iloc[:self.TestPeriodFoldSize,]
			y_pred = y_test.iloc[:self.TestPeriodFoldSize,]

			#Get the accuracy of the classifier
			accuracy = classifier(X_train,X_pred,y_train,y_pred)

			# Change the train samples
			X_train = X_train.append(X_pred)
			y_train = y_train.append(y_pred)

			# Change the test samples
			X_test = X_test.iloc[self.TestPeriodFoldSize:,]
			y_test = y_test.iloc[self.TestPeriodFoldSize:,]

			# Print statement for debugging
			print(len(X_pred),len(y_pred),len(X_train),len(X_test),len(y_train),len(y_test), accuracy)

			# Finish time for execution
			timeEnd = dt.datetime.utcnow()

			#Duration for execution
			modelDuration = (timeEnd - timeStart).total_seconds()

			#Add a record to the logger
			self.Log.addResultRecord(self,
								     modelDuration,
								     modelTag,
								     accuracy)

			accuracy_list.append(accuracy)

		return accuracy_list






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
		X_train, X_test, y_train, y_test = self.train_test_split(self.StockCollector.securityDF)
		results_dict = {}
		for classifier in classifiers:
			modelTag = classifier.__name__.rsplit('_')[0] + "_" + str(self.TestPeriodFoldSize) + "days"
			results_dict[modelTag] = self.kFoldCrossValidationTest(classifier,modelTag)

		results_df = pd.DataFrame.from_dict(results_dict)

		self.resultsDF = results_df

	def saveResultsDF(self, resultsName):
		self.resultsDF.to_csv(logName + "_" + str(dt.datetime.now()) + "_ResultsDF.csv", sep = ",")