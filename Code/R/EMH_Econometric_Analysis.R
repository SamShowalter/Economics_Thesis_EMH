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


##############################################################################################################################################
# Valid stock tickers to query
sp500list = c('MMM', 'ABT', 'ABBV', 'ACN', 'ATVI', 'AYI', 'ADBE', 'AAP', 'AES', 'AET', 'AMG', 'AFL', 
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
             'XLNX', 'XL', 'XYL', 'YHOO', 'YUM', 'ZBH', 'ZION', 'ZTS')

#Valid list of stock indices
index_list = c('^IXIC.csv','^GSPC.csv','^RUT.csv','^DJI.csv')

##############################################################################################################################################

#Subsample of stock data
test = c("LLY")
print(test)

#cbind the functions


ADF_automate = function(securityList,dateStart, dateEnd)
{
  resultsDF = data.frame()
  
  for (stock in securityList)
  {
    stock_data = Quandl(paste("WIKI/",toupper(stock), sep = ""),
                        start_date=dateStart, 
                        end_date = dateEnd)
    
    #print(stock)
    
    #resultsDF = cbind(resultsDF,stock_data$`Adj. Close`)
    #
    first_diff = c(diff(stock_data$`Adj. Close`,lag = 1, differences = 1))
    #par(mar=c(-1,1))
    #hist(first_diff,breaks = 150, xlim = c(-2,2))
    test_results = adf.test(first_diff, alternative = "stationary")
    #boot_tests = Boot.test(stock_data$`Adj. Close`[c(1:100)],c(1,5,10),nboot = 10, wild = 'Normal')
    #print(boot_tests)
    
    
    if (nrow(resultsDF) == 0)
    {
      resultsDF = data.frame(t(unlist(test_results)))
      resultsDF$numDays = length(stock_data$`Adj. Close`)
      resultsDF$pp.p.value = pp.test(first_diff,alternative = "stationary")$p.value
      names(resultsDF) = c("ADF.tstat","Lag.order","alternative","adf.p.value","method","data.name","NumDays","pp.p.value")
    }
    else
    {
      newRow = data.frame(t(unlist(test_results)))
      newRow$numDays = length(stock_data$`Adj. Close`)
      resultsDF$pp.p.value = pp.test(first_diff,alternative = "stationary")$p.value
      names(newRow) = c("ADF.tstat","adf.Lag.order","adf.alternative","adf.p.value","adf.method","adf.data.name","NumDays",
                        "pp.tstat","pp.Lag.order", "pp.alterative", "pp.p.value","pp.method","pp.data.name",
                        "vrtest.")
      #print(newRow)
      resultsDF = rbind(resultsDF,newRow)
    }
    
  }
  print(head(resultsDF))
  #print(head(resultsDF))
  
}

ADF_automate(test,"1988-01-01","2018-01-01")







