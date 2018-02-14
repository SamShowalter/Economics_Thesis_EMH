####################################################################################################
# Econometrics Analysis: EMH Research Paper
# Sam Showalter
# Dr. Jeff Gropp
####################################################################################################

# Clear current data
rm(list = ls())

# Set working directory
#Setwd()

# Install Quandl API and dependencies
install.packages("Quandl")
library(Quandl)

# Install econometric packages
install.packages("plm")
library(plm)

# Install variance ratio test packages
install.packages('vrtest')
library(vrtest)
#library(help="vrtest")

# Install remaining econometric packages and functions
asinstall.packages('tseries')
library(tseries)
#library(help="tseries")

#Authenticate with API Key
Quandl.api_key("N1j_H8avpLu-8zwvDdsH")

ticker = "amzn"
paste("WIKI/",ticker, sep ="")

#Test run
xrx = Quandl(paste("WIKI/",toupper(ticker), sep = ""),
              start_date="2016-01-01", 
              end_date = '2018-01-01')

plot(as.Date(xrx$Date), xrx$`Adj. Close`)

print(amzn$`Adj. High`)
