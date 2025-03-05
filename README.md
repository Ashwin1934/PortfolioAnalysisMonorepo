# PortfolioAnalysisMonorepo

### Introduction

The idea behind this project is to automate investment analysis by creating a data pipeline. 
I currently research stocks in my portfolio and watchlist via Google Sheets. This requires 
some manual work for each stock. The goal is to automate this manual work via the data pipeline
which will just require a list of tickers. 

The data pipeline will consist of a client that fetches Yahoo finance data via the Yfinance API in python.
(Chose yfinance because most of the numbers I generally use are from there...) This client will in turn
send the fetched data to a server (Java or CPP) via UDP Datagram Channels. The server in turn will parallelize the
valuation process, computing the values and sending the data to a Kafka broker. The aforementioned Kafka broker will run on a custom built server that I constructed at home from scratch. A Python kafka consumer will read from the valuation Kafka topic and push data
to a google sheet where I can see all the valuations with some cell formatting perhaps. 

#### Underlying Valuation Technique
The underlying valuation technique is not a DCF or anything super complex -- it's a simple formula
adapted from Ben Graham's Intelligent Investor. It attempts to come up with a valuation of a stock,
or more so a price estimate that could be compared with the actual market price to make an investment
decision. 

![Alt text](Images/ValuationFormula.png)

The formula is comprised of:
* EPS 
    * Trailing twelve month earnings per share. Note that these numbers are reported in GAAP/ non GAAP formats depending on the source.
* PE ratio no growth
    * I took this to mean the acceptable PE ratio for a company with no growth prospects. In Ben Graham's original 
    formula this value was 8.5 but I corrected this to 7.
* g - Growth rate
    * Obviously no one can really predict the growth rate, but the numbers from Wall Street are better than any number the layman comes up with.
* Y - 20 Year Corporate Bond Yield
    * TODO: double check why this is used in the formula.

Disclaimer:
I understand that valuation isn't a sure fire investment technique. A stock could be under valued as per this formula and drop the next day. But as much as valuation can be used to decide to buy a stock, it could also be used to decide when NOT to buy a stock. For example, some companies with negative earnings per share aren't even profitable. Obviously, that same company could be on the way to profitability but you'll at least have an idea of the current company state...

#### Custom Server Construction
I got an old server from work with no OS and no hard disk, but thought it might be a useful exercise to construct a server myself.
I had an old SATA hard drive with Windows 10 installed on it, and initially used that to boot up the server. It worked for 4 days, but 
the disk itself showed 18% fragmentation... which didn't make sense to me because there was still ~700 GB available on the drive.
Regardless, I ran a built in Windows disk clean up operation. This ran all night and still didn't finish. A short time after this the
hard drive wasn't getting recognized, maybe because I touched it or shifted the server accidentally.. not sure. 

I then had to resort to installing a SATA compatible hard drive and the OS. For the former I purchased a 1 TB Kingston hard drive. For the latter
I created a bootable USB drive with Windows 10 on it from an 8GB flash drive. To use the USB drive you can rearrange the ordering of the boot devices (hard drive, USB drive, etc). You also use the UEFI boot option to boot the system from a hard drive or USB drive. After this, I successfully had the server up and just needed to run/install Kafka on it and open up the port to make it accessible on the local network.


#### Architecture
TODO provide architecture diagram and description

##### UDP Client
A Python client that leverages the yfinance 