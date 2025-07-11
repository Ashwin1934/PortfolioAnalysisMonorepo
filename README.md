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
    * https://fred.stlouisfed.org/series/AAA

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

![Alt text](Images/IMG_6505.jpg)

##### Kafka Broker Setup and Port Opening on Local Subnet
After installing Kafka on the server, I opened the port Kafka runs on to my home network. This requires editing the
Windows Firewall to allow incoming connections. I then pinged the server from my laptop as seen below. 

Connection Succeeded:
```
curl -vvv 127.0.0.1:9092
*   Trying 127.0.0.1:9092...
* Connected to 127.0.0.1 (127.0.0.1) port 9092
> GET / HTTP/1.1
> Host: 127.0.0.1:9092
> User-Agent: curl/8.7.1
> Accept: */*
>
* Request completely sent off
* Empty reply from server
* Closing connection
curl: (52) Empty reply from server
```
Connection Failed:
```
curl -vvv 127.0.0.1:9092
*   Trying 127.0.0.1:9092...
* connect to 127.0.0.1 port 9092 from 0.0.0.0 port 61519 failed: Connection timed out
* Failed to connect to 127.0.0.1 port 9092 after 21036 ms: Couldn't connect to server
* Closing connection
curl: (28) Failed to connect to 127.0.0.1 port 9092 after 21036 ms: Couldn't connect to server
```

#### Architecture

![Alt text](Images/sora_architecture_diagram.png) 

### Execution Times
Execution times for publishing all messages to Kafka in different scenarios.

#### Publish Messages with broker down, built in thread pool
Use CompletableFuture's built in thread pool. Uses ForkJoinPool.commonPool() as the underlying thread pool.

| Description        | Execution Time | Number of Tickers | Threads |
|--------------------|---------------|-------------------|------|
| Publish messages with broker down        | **12194 ms**          | 23               | Built in thread pool |

###### Sample Output
<details>
<summary>Output</summary>

```
Entered shutdownUDPServerAfterSetDuration.
Start time MS: 1743473984225
UDP server up and listening on 127.0.0.1: 5005
Received message number 1 from /127.0.0.1:55798
Message 1 for ticker: AMD handled by thread: ForkJoinPool.commonPool-worker-1
Received message number 2 from /127.0.0.1:55798
Valuation for ticker: AMD: 2.2379323364661654
Message 2 for ticker: AMZN handled by thread: ForkJoinPool.commonPool-worker-2
Valuation for ticker: AMZN: 8.421918217462405
Creating kafka publisher
SLF4J(W): No SLF4J providers were found.
SLF4J(W): Defaulting to no-operation (NOP) logger implementation
SLF4J(W): See https://www.slf4j.org/codes.html#noProviders for further details.
Received message number 3 from /127.0.0.1:55798
Message 3 for ticker: DELL handled by thread: ForkJoinPool.commonPool-worker-3
Valuation for ticker: DELL: 9.32756766917293
Received message number 4 from /127.0.0.1:55798
Message 4 for ticker: INTC handled by thread: ForkJoinPool.commonPool-worker-4
Valuation for ticker: INTC: -6.546110714285715
Received message number 5 from /127.0.0.1:55798
Message 5 for ticker: LCID handled by thread: ForkJoinPool.commonPool-worker-5
Valuation for ticker: LCID: -1.0118202141541353
Received message number 6 from /127.0.0.1:55798
Message 6 for ticker: MTH handled by thread: ForkJoinPool.commonPool-worker-6
Valuation for ticker: MTH: 15.50319172932331
Publishing kafka message: 4 for ticker: INTC
Publishing kafka message: 6 for ticker: MTH
Publishing kafka message: 1 for ticker: AMD
Publishing kafka message: 2 for ticker: AMZN
Publishing kafka message: 5 for ticker: LCID
Publishing kafka message: 3 for ticker: DELL
Error sending message 4 for ticker INTC at currentTimeMS 1743473992344: Topic test_topic not present in metadata after 100 ms.
Error sending message 1 for ticker AMD at currentTimeMS 1743473992344: Topic test_topic not present in metadata after 100 ms.
Error sending message 5 for ticker LCID at currentTimeMS 1743473992334: Topic test_topic not present in metadata after 100 ms.      
Error sending message 3 for ticker DELL at currentTimeMS 1743473992350: Topic test_topic not present in metadata after 100 ms.      
Error sending message 2 for ticker AMZN at currentTimeMS 1743473992350: Topic test_topic not present in metadata after 100 ms.      
Error sending message 6 for ticker MTH at currentTimeMS 1743473992351: Topic test_topic not present in metadata after 100 ms.       
Received message number 7 from /127.0.0.1:55798
Message 7 for ticker: MCHP handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: MCHP: 1.5717801694943607
Publishing kafka message: 7 for ticker: MCHP
Error sending message 7 for ticker MCHP at currentTimeMS 1743473992539: Topic test_topic not present in metadata after 100 ms.
Received message number 8 from /127.0.0.1:55798
ComputeValuation: message 5 processed by KafkaMessagePublisher for: LCID
ComputeValuation: message 3 processed by KafkaMessagePublisher for: DELL
ComputeValuation: message 1 processed by KafkaMessagePublisher for: AMD
ComputeValuation: message 4 processed by KafkaMessagePublisher for: INTC
ComputeValuation: message 6 processed by KafkaMessagePublisher for: MTH
ComputeValuation: message 2 processed by KafkaMessagePublisher for: AMZN
ComputeValuation: message 7 processed by KafkaMessagePublisher for: MCHP
Message 8 for ticker: PYPL handled by thread: ForkJoinPool.commonPool-worker-5
Valuation for ticker: PYPL: 6.210492664672932
Publishing kafka message: 8 for ticker: PYPL
Received message number 9 from /127.0.0.1:55798
Message 9 for ticker: PBR handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: PBR: 2.3486736838834585
Publishing kafka message: 9 for ticker: PBR
Error sending message 8 for ticker PYPL at currentTimeMS 1743473992954: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 8 processed by KafkaMessagePublisher for: PYPL
Error sending message 9 for ticker PBR at currentTimeMS 1743473993032: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 9 processed by KafkaMessagePublisher for: PBR
Received message number 10 from /127.0.0.1:55798
Message 10 for ticker: PONY handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: PONY: -2.3336015037593985
Publishing kafka message: 10 for ticker: PONY
Error sending message 10 for ticker PONY at currentTimeMS 1743473993248: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 10 processed by KafkaMessagePublisher for: PONY
Received message number 11 from /127.0.0.1:55798
Message 11 for ticker: IOT handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: IOT: 0.43132293233082714
Publishing kafka message: 11 for ticker: IOT
Error sending message 11 for ticker IOT at currentTimeMS 1743473993517: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 11 processed by KafkaMessagePublisher for: IOT
Received message number 12 from /127.0.0.1:55798
Message 12 for ticker: SNOW handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: SNOW: -4.6517379916917285
Publishing kafka message: 12 for ticker: SNOW
Error sending message 12 for ticker SNOW at currentTimeMS 1743473993744: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 12 processed by KafkaMessagePublisher for: SNOW
Received message number 13 from /127.0.0.1:55798
Message 13 for ticker: TGT handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: TGT: 12.673820300751878
Publishing kafka message: 13 for ticker: TGT
Error sending message 13 for ticker TGT at currentTimeMS 1743473993958: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 13 processed by KafkaMessagePublisher for: TGT
Received message number 14 from /127.0.0.1:55798
Message 14 for ticker: WMT handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: WMT: 4.079729605263158
Publishing kafka message: 14 for ticker: WMT
Error sending message 14 for ticker WMT at currentTimeMS 1743473994183: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 14 processed by KafkaMessagePublisher for: WMT
Received message number 15 from /127.0.0.1:55798
Message 15 for ticker: BAC handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: BAC: 5.211945761625939
Publishing kafka message: 15 for ticker: BAC
Error sending message 15 for ticker BAC at currentTimeMS 1743473994433: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 15 processed by KafkaMessagePublisher for: BAC
Received message number 16 from /127.0.0.1:55798
Message 16 for ticker: AI handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: AI: -2.1360657894736836
Publishing kafka message: 16 for ticker: AI
Error sending message 16 for ticker AI at currentTimeMS 1743473994715: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 16 processed by KafkaMessagePublisher for: AI
Received message number 17 from /127.0.0.1:55798
Message 17 for ticker: ENPH handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: ENPH: 1.8652960505169172
Publishing kafka message: 17 for ticker: ENPH
Error sending message 17 for ticker ENPH at currentTimeMS 1743473994974: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 17 processed by KafkaMessagePublisher for: ENPH
Received message number 18 from /127.0.0.1:55798
Message 18 for ticker: FSLR handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: FSLR: 18.142871736729322
Publishing kafka message: 18 for ticker: FSLR
Error sending message 18 for ticker FSLR at currentTimeMS 1743473995216: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 18 processed by KafkaMessagePublisher for: FSLR
Received message number 19 from /127.0.0.1:55798
Message 19 for ticker: JPM handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: JPM: 27.209837898214285
Publishing kafka message: 19 for ticker: JPM
Error sending message 19 for ticker JPM at currentTimeMS 1743473995434: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 19 processed by KafkaMessagePublisher for: JPM
Received message number 20 from /127.0.0.1:55798
Message 20 for ticker: PLTR handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: PLTR: 1.090444454887218
Publishing kafka message: 20 for ticker: PLTR
Error sending message 20 for ticker PLTR at currentTimeMS 1743473995700: Topic test_topic not present in metadata after 100 ms.     
ComputeValuation: message 20 processed by KafkaMessagePublisher for: PLTR
Received message number 21 from /127.0.0.1:55798
Message 21 for ticker: GOOG handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: GOOG: 11.736028195488721
Publishing kafka message: 21 for ticker: GOOG
Error sending message 21 for ticker GOOG at currentTimeMS 1743473995927: Topic test_topic not present in metadata after 100 ms.     
ComputeValuation: message 21 processed by KafkaMessagePublisher for: GOOG
Received message number 22 from /127.0.0.1:55798
Message 22 for ticker: AAPL handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: AAPL: 9.347821247718043
Publishing kafka message: 22 for ticker: AAPL
Error sending message 22 for ticker AAPL at currentTimeMS 1743473996177: Topic test_topic not present in metadata after 100 ms.     
ComputeValuation: message 22 processed by KafkaMessagePublisher for: AAPL
Received message number 23 from /127.0.0.1:55798
Message 23 for ticker: SMCI handled by thread: ForkJoinPool.commonPool-worker-7
Valuation for ticker: SMCI: 4.119396616541352
Publishing kafka message: 23 for ticker: SMCI
Error sending message 23 for ticker SMCI at currentTimeMS 1743473996419: Topic test_topic not present in metadata after 100 ms.     
ComputeValuation: message 23 processed by KafkaMessagePublisher for: SMCI
Messages consumed: 23
DatagramChannel closed.
UDP Server down after 1 minutes.
Executor Service shutdown
Scheduled Executor Service shutdown.
KafkaMessagePublisher shutdown
```
</details>

#### Publish Messages with broker down, custom 8 thread pool

| Description        | Execution Time | Number of Tickers | Threads |
|--------------------|---------------|-------------------|------|
| Publish messages with broker down        | **11720**         | 23              | 8  |

###### Sample Output
<details>
<summary>Output</summary>

```
Entered shutdownUDPServerAfterSetDuration.
Start time MS: 1743474307121
UDP server up and listening on 127.0.0.1: 5005
Received message number 1 from /127.0.0.1:54438
Message 1 for ticker: AMD handled by thread: pool-2-thread-1
Valuation for ticker: AMD: 2.2379323364661654
Received message number 2 from /127.0.0.1:54438
Message 2 for ticker: AMZN handled by thread: pool-2-thread-2
Valuation for ticker: AMZN: 8.421918217462405
Creating kafka publisher
SLF4J(W): No SLF4J providers were found.
SLF4J(W): Defaulting to no-operation (NOP) logger implementation
SLF4J(W): See https://www.slf4j.org/codes.html#noProviders for further details.
Received message number 3 from /127.0.0.1:54438
Message 3 for ticker: DELL handled by thread: pool-2-thread-3
Valuation for ticker: DELL: 9.32756766917293
Received message number 4 from /127.0.0.1:54438
Message 4 for ticker: INTC handled by thread: pool-2-thread-4
Valuation for ticker: INTC: -6.546110714285715
Received message number 5 from /127.0.0.1:54438
Message 5 for ticker: LCID handled by thread: pool-2-thread-5
Valuation for ticker: LCID: -1.0118202141541353
Publishing kafka message: 3 for ticker: DELL
Publishing kafka message: 4 for ticker: INTC
Publishing kafka message: 1 for ticker: AMD
Publishing kafka message: 2 for ticker: AMZN
Publishing kafka message: 5 for ticker: LCID
Error sending message 2 for ticker AMZN at currentTimeMS 1743474314168: Topic test_topic not present in metadata after 100 ms.
Error sending message 5 for ticker LCID at currentTimeMS 1743474314167: Topic test_topic not present in metadata after 100 ms.
Error sending message 4 for ticker INTC at currentTimeMS 1743474314168: Topic test_topic not present in metadata after 100 ms.      
Error sending message 3 for ticker DELL at currentTimeMS 1743474314168: Topic test_topic not present in metadata after 100 ms.      
Error sending message 1 for ticker AMD at currentTimeMS 1743474314168: Topic test_topic not present in metadata after 100 ms.       
Received message number 6 from /127.0.0.1:54438
Message 6 for ticker: MTH handled by thread: pool-2-thread-6
Valuation for ticker: MTH: 15.50319172932331
Publishing kafka message: 6 for ticker: MTH
Error sending message 6 for ticker MTH at currentTimeMS 1743474314345: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 6 processed by KafkaMessagePublisher for: MTH
ComputeValuation: message 1 processed by KafkaMessagePublisher for: AMD
ComputeValuation: message 2 processed by KafkaMessagePublisher for: AMZN
ComputeValuation: message 3 processed by KafkaMessagePublisher for: DELL
ComputeValuation: message 4 processed by KafkaMessagePublisher for: INTC
ComputeValuation: message 5 processed by KafkaMessagePublisher for: LCID
Received message number 7 from /127.0.0.1:54438
Message 7 for ticker: MCHP handled by thread: pool-2-thread-7
Valuation for ticker: MCHP: 1.5717801694943607
Publishing kafka message: 7 for ticker: MCHP
Error sending message 7 for ticker MCHP at currentTimeMS 1743474314672: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 7 processed by KafkaMessagePublisher for: MCHP
Received message number 8 from /127.0.0.1:54438
Message 8 for ticker: PYPL handled by thread: pool-2-thread-8
Valuation for ticker: PYPL: 6.210492664672932
Publishing kafka message: 8 for ticker: PYPL
Error sending message 8 for ticker PYPL at currentTimeMS 1743474314923: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 8 processed by KafkaMessagePublisher for: PYPL
Received message number 9 from /127.0.0.1:54438
Message 9 for ticker: PBR handled by thread: pool-2-thread-6
Valuation for ticker: PBR: 2.3486736838834585
Publishing kafka message: 9 for ticker: PBR
Error sending message 9 for ticker PBR at currentTimeMS 1743474315160: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 9 processed by KafkaMessagePublisher for: PBR
Received message number 10 from /127.0.0.1:54438
Message 10 for ticker: PONY handled by thread: pool-2-thread-1
Valuation for ticker: PONY: -2.3336015037593985
Publishing kafka message: 10 for ticker: PONY
Error sending message 10 for ticker PONY at currentTimeMS 1743474315538: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 10 processed by KafkaMessagePublisher for: PONY
Received message number 11 from /127.0.0.1:54438
Message 11 for ticker: IOT handled by thread: pool-2-thread-2
Valuation for ticker: IOT: 0.43132293233082714
Publishing kafka message: 11 for ticker: IOT
Error sending message 11 for ticker IOT at currentTimeMS 1743474315789: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 11 processed by KafkaMessagePublisher for: IOT
Received message number 12 from /127.0.0.1:54438
Message 12 for ticker: SNOW handled by thread: pool-2-thread-3
Valuation for ticker: SNOW: -4.6517379916917285
Publishing kafka message: 12 for ticker: SNOW
Error sending message 12 for ticker SNOW at currentTimeMS 1743474316028: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 12 processed by KafkaMessagePublisher for: SNOW
Received message number 13 from /127.0.0.1:54438
Message 13 for ticker: TGT handled by thread: pool-2-thread-4
Valuation for ticker: TGT: 12.673820300751878
Publishing kafka message: 13 for ticker: TGT
Error sending message 13 for ticker TGT at currentTimeMS 1743474316249: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 13 processed by KafkaMessagePublisher for: TGT
Received message number 14 from /127.0.0.1:54438
Message 14 for ticker: WMT handled by thread: pool-2-thread-5
Valuation for ticker: WMT: 4.079729605263158
Publishing kafka message: 14 for ticker: WMT
Error sending message 14 for ticker WMT at currentTimeMS 1743474316469: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 14 processed by KafkaMessagePublisher for: WMT
Received message number 15 from /127.0.0.1:54438
Message 15 for ticker: BAC handled by thread: pool-2-thread-7
Valuation for ticker: BAC: 5.211945761625939
Publishing kafka message: 15 for ticker: BAC
Error sending message 15 for ticker BAC at currentTimeMS 1743474316722: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 15 processed by KafkaMessagePublisher for: BAC
Received message number 16 from /127.0.0.1:54438
Message 16 for ticker: AI handled by thread: pool-2-thread-8
Valuation for ticker: AI: -2.1360657894736836
Publishing kafka message: 16 for ticker: AI
Error sending message 16 for ticker AI at currentTimeMS 1743474317010: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 16 processed by KafkaMessagePublisher for: AI
Received message number 17 from /127.0.0.1:54438
Message 17 for ticker: ENPH handled by thread: pool-2-thread-6
Valuation for ticker: ENPH: 1.8652960505169172
Publishing kafka message: 17 for ticker: ENPH
Error sending message 17 for ticker ENPH at currentTimeMS 1743474317275: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 17 processed by KafkaMessagePublisher for: ENPH
Received message number 18 from /127.0.0.1:54438
Message 18 for ticker: FSLR handled by thread: pool-2-thread-1
Valuation for ticker: FSLR: 18.142871736729322
Publishing kafka message: 18 for ticker: FSLR
Error sending message 18 for ticker FSLR at currentTimeMS 1743474317529: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 18 processed by KafkaMessagePublisher for: FSLR
Received message number 19 from /127.0.0.1:54438
Message 19 for ticker: JPM handled by thread: pool-2-thread-2
Valuation for ticker: JPM: 27.209837898214285
Publishing kafka message: 19 for ticker: JPM
Error sending message 19 for ticker JPM at currentTimeMS 1743474317767: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 19 processed by KafkaMessagePublisher for: JPM
Received message number 20 from /127.0.0.1:54438
Message 20 for ticker: PLTR handled by thread: pool-2-thread-3
Valuation for ticker: PLTR: 1.090444454887218
Publishing kafka message: 20 for ticker: PLTR
Error sending message 20 for ticker PLTR at currentTimeMS 1743474318005: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 20 processed by KafkaMessagePublisher for: PLTR
Received message number 21 from /127.0.0.1:54438
Message 21 for ticker: GOOG handled by thread: pool-2-thread-4
Valuation for ticker: GOOG: 11.736028195488721
Publishing kafka message: 21 for ticker: GOOG
Error sending message 21 for ticker GOOG at currentTimeMS 1743474318303: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 21 processed by KafkaMessagePublisher for: GOOG
Received message number 22 from /127.0.0.1:54438
Message 22 for ticker: AAPL handled by thread: pool-2-thread-5
Valuation for ticker: AAPL: 9.347821247718043
Publishing kafka message: 22 for ticker: AAPL
Error sending message 22 for ticker AAPL at currentTimeMS 1743474318558: Topic test_topic not present in metadata after 100 ms.     
ComputeValuation: message 22 processed by KafkaMessagePublisher for: AAPL
Received message number 23 from /127.0.0.1:54438
Message 23 for ticker: SMCI handled by thread: pool-2-thread-7
Valuation for ticker: SMCI: 4.119396616541352
Publishing kafka message: 23 for ticker: SMCI
Error sending message 23 for ticker SMCI at currentTimeMS 1743474318841: Topic test_topic not present in metadata after 100 ms.     
ComputeValuation: message 23 processed by KafkaMessagePublisher for: SMCI
Messages consumed: 23
DatagramChannel closed.
UDP Server down after 1 minutes.
Executor Service shutdown
Scheduled Executor Service shutdown.
KafkaMessagePublisher shutdown
```

</details>

#### Publish Messages with broker down, custom 1 thread pool

| Description        | Execution Time | Number of Tickers | Threads |
|--------------------|---------------|-------------------|------|
| Publish messages with broker down        | **12464**         | 23              | 1  |

###### Sample Output
<details>
<summary>Output</summary>

```
Entered shutdownUDPServerAfterSetDuration.
Start time MS: 1743556493609
UDP server up and listening on 127.0.0.1: 5005
Received message number 1 from /127.0.0.1:55154
Message 1 for ticker: AMD handled by thread: pool-2-thread-1
Valuation for ticker: AMD: 2.2379323364661654
Creating kafka publisher
SLF4J(W): No SLF4J providers were found.
SLF4J(W): Defaulting to no-operation (NOP) logger implementation
SLF4J(W): See https://www.slf4j.org/codes.html#noProviders for further details.
Received message number 2 from /127.0.0.1:55154
Publishing kafka message: 1 for ticker: AMD
Received message number 3 from /127.0.0.1:55154
Error sending message 1 for ticker AMD at currentTimeMS 1743556499361: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 1 processed by KafkaMessagePublisher for: AMD
Message 2 for ticker: AMZN handled by thread: pool-2-thread-1
Valuation for ticker: AMZN: 8.420980999417292
Publishing kafka message: 2 for ticker: AMZN
Received message number 4 from /127.0.0.1:55154
Error sending message 2 for ticker AMZN at currentTimeMS 1743556499658: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 2 processed by KafkaMessagePublisher for: AMZN
Message 3 for ticker: DELL handled by thread: pool-2-thread-1
Valuation for ticker: DELL: 9.43551052631579
Publishing kafka message: 3 for ticker: DELL
Error sending message 3 for ticker DELL at currentTimeMS 1743556499769: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 3 processed by KafkaMessagePublisher for: DELL
Message 4 for ticker: INTC handled by thread: pool-2-thread-1
Valuation for ticker: INTC: -6.546110714285715
Publishing kafka message: 4 for ticker: INTC
Error sending message 4 for ticker INTC at currentTimeMS 1743556499880: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 4 processed by KafkaMessagePublisher for: INTC
Received message number 5 from /127.0.0.1:55154
Message 5 for ticker: LCID handled by thread: pool-2-thread-1
Valuation for ticker: LCID: -0.9275963416353381
Publishing kafka message: 5 for ticker: LCID
Error sending message 5 for ticker LCID at currentTimeMS 1743556500098: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 5 processed by KafkaMessagePublisher for: LCID
Received message number 6 from /127.0.0.1:55154
Message 6 for ticker: MTH handled by thread: pool-2-thread-1
Valuation for ticker: MTH: 15.394479699248121
Publishing kafka message: 6 for ticker: MTH
Error sending message 6 for ticker MTH at currentTimeMS 1743556500425: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 6 processed by KafkaMessagePublisher for: MTH
Received message number 7 from /127.0.0.1:55154
Message 7 for ticker: MCHP handled by thread: pool-2-thread-1
Valuation for ticker: MCHP: 1.5717801694943607
Publishing kafka message: 7 for ticker: MCHP
Error sending message 7 for ticker MCHP at currentTimeMS 1743556500812: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 7 processed by KafkaMessagePublisher for: MCHP
Received message number 8 from /127.0.0.1:55154
Message 8 for ticker: PYPL handled by thread: pool-2-thread-1
Valuation for ticker: PYPL: 6.210492664672932
Publishing kafka message: 8 for ticker: PYPL
Error sending message 8 for ticker PYPL at currentTimeMS 1743556501206: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 8 processed by KafkaMessagePublisher for: PYPL
Received message number 9 from /127.0.0.1:55154
Message 9 for ticker: PBR handled by thread: pool-2-thread-1
Valuation for ticker: PBR: 2.3486736838834585
Publishing kafka message: 9 for ticker: PBR
Error sending message 9 for ticker PBR at currentTimeMS 1743556501483: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 9 processed by KafkaMessagePublisher for: PBR
Received message number 10 from /127.0.0.1:55154
Message 10 for ticker: PONY handled by thread: pool-2-thread-1
Valuation for ticker: PONY: -2.3336015037593985
Publishing kafka message: 10 for ticker: PONY
Error sending message 10 for ticker PONY at currentTimeMS 1743556501827: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 10 processed by KafkaMessagePublisher for: PONY
Received message number 11 from /127.0.0.1:55154
Message 11 for ticker: IOT handled by thread: pool-2-thread-1
Valuation for ticker: IOT: 0.43132293233082714
Publishing kafka message: 11 for ticker: IOT
Error sending message 11 for ticker IOT at currentTimeMS 1743556502139: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 11 processed by KafkaMessagePublisher for: IOT
Received message number 12 from /127.0.0.1:55154
Message 12 for ticker: SNOW handled by thread: pool-2-thread-1
Valuation for ticker: SNOW: -4.651955639097745
Publishing kafka message: 12 for ticker: SNOW
Error sending message 12 for ticker SNOW at currentTimeMS 1743556502440: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 12 processed by KafkaMessagePublisher for: SNOW
Received message number 13 from /127.0.0.1:55154
Message 13 for ticker: TGT handled by thread: pool-2-thread-1
Valuation for ticker: TGT: 12.673820300751878
Publishing kafka message: 13 for ticker: TGT
Error sending message 13 for ticker TGT at currentTimeMS 1743556502815: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 13 processed by KafkaMessagePublisher for: TGT
Received message number 14 from /127.0.0.1:55154
Message 14 for ticker: WMT handled by thread: pool-2-thread-1
Valuation for ticker: WMT: 4.079729605263158
Publishing kafka message: 14 for ticker: WMT
Error sending message 14 for ticker WMT at currentTimeMS 1743556503097: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 14 processed by KafkaMessagePublisher for: WMT
Received message number 15 from /127.0.0.1:55154
Message 15 for ticker: BAC handled by thread: pool-2-thread-1
Valuation for ticker: BAC: 5.208596992481203
Publishing kafka message: 15 for ticker: BAC
Error sending message 15 for ticker BAC at currentTimeMS 1743556503428: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 15 processed by KafkaMessagePublisher for: BAC
Received message number 16 from /127.0.0.1:55154
Message 16 for ticker: AI handled by thread: pool-2-thread-1
Valuation for ticker: AI: -2.1360657894736836
Publishing kafka message: 16 for ticker: AI
Error sending message 16 for ticker AI at currentTimeMS 1743556503723: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 16 processed by KafkaMessagePublisher for: AI
Received message number 17 from /127.0.0.1:55154
Message 17 for ticker: ENPH handled by thread: pool-2-thread-1
Valuation for ticker: ENPH: 1.8652960505169172
Publishing kafka message: 17 for ticker: ENPH
Error sending message 17 for ticker ENPH at currentTimeMS 1743556504035: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 17 processed by KafkaMessagePublisher for: ENPH
Received message number 18 from /127.0.0.1:55154
Message 18 for ticker: FSLR handled by thread: pool-2-thread-1
Valuation for ticker: FSLR: 18.142871736729322
Publishing kafka message: 18 for ticker: FSLR
Error sending message 18 for ticker FSLR at currentTimeMS 1743556504424: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 18 processed by KafkaMessagePublisher for: FSLR
Received message number 19 from /127.0.0.1:55154
Message 19 for ticker: JPM handled by thread: pool-2-thread-1
Valuation for ticker: JPM: 27.207610460173875
Publishing kafka message: 19 for ticker: JPM
Error sending message 19 for ticker JPM at currentTimeMS 1743556504754: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 19 processed by KafkaMessagePublisher for: JPM
Received message number 20 from /127.0.0.1:55154
Message 20 for ticker: PLTR handled by thread: pool-2-thread-1
Valuation for ticker: PLTR: 1.090444454887218
Publishing kafka message: 20 for ticker: PLTR
Error sending message 20 for ticker PLTR at currentTimeMS 1743556505132: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 20 processed by KafkaMessagePublisher for: PLTR
Received message number 21 from /127.0.0.1:55154
Message 21 for ticker: GOOG handled by thread: pool-2-thread-1
Valuation for ticker: GOOG: 11.734212406015036
Publishing kafka message: 21 for ticker: GOOG
Error sending message 21 for ticker GOOG at currentTimeMS 1743556505462: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 21 processed by KafkaMessagePublisher for: GOOG
Received message number 22 from /127.0.0.1:55154
Message 22 for ticker: AAPL handled by thread: pool-2-thread-1
Valuation for ticker: AAPL: 9.347821247718043
Publishing kafka message: 22 for ticker: AAPL
Error sending message 22 for ticker AAPL at currentTimeMS 1743556505759: Topic test_topic not present in metadata after 100 ms.     
ComputeValuation: message 22 processed by KafkaMessagePublisher for: AAPL
Received message number 23 from /127.0.0.1:55154
Message 23 for ticker: SMCI handled by thread: pool-2-thread-1
Valuation for ticker: SMCI: 4.119396616541352
Publishing kafka message: 23 for ticker: SMCI
Error sending message 23 for ticker SMCI at currentTimeMS 1743556506073: Topic test_topic not present in metadata after 100 ms.     
ComputeValuation: message 23 processed by KafkaMessagePublisher for: SMCI
Messages consumed: 23
DatagramChannel closed.
UDP Server down after 1 minutes.
Executor Service shutdown
Scheduled Executor Service shutdown.
KafkaMessagePublisher shutdown
```

</details>

#### Publish Messages with broker up, custom 8 thread pool

| Description        | Execution Time | Number of Tickers | Threads |
|--------------------|---------------|-------------------|------|
| Publish messages with broker up        | **16382**         | 45              | 8  |

15220
13872
###### Sample Output
<details>
<summary>Output</summary>

```
Entered shutdownUDPServerAfterSetDuration.
Start time MS: 1744244281556
UDP server up and listening on 127.0.0.1: 5005
Received message number 1 from /127.0.0.1:51586
Message 1 for ticker: AMD handled by thread: pool-2-thread-1
Valuation for ticker: AMD: 2.2381860958646618
Creating kafka publisher
SLF4J(W): No SLF4J providers were found.
SLF4J(W): Defaulting to no-operation (NOP) logger implementation
SLF4J(W): See https://www.slf4j.org/codes.html#noProviders for further details.
Received message number 2 from /127.0.0.1:51586
Message 2 for ticker: AMZN handled by thread: pool-2-thread-2
Valuation for ticker: AMZN: 8.411951237396616
Received message number 3 from /127.0.0.1:51586
Message 3 for ticker: DELL handled by thread: pool-2-thread-3
Valuation for ticker: DELL: 9.463033270676691
Publishing kafka message: 3 for ticker: DELL
Publishing kafka message: 2 for ticker: AMZN
Publishing kafka message: 1 for ticker: AMD
Received message number 4 from /127.0.0.1:51586
Message 4 for ticker: INTC handled by thread: pool-2-thread-4
Valuation for ticker: INTC: -6.547839661654134
Publishing kafka message: 4 for ticker: INTC
Error sending message 2 for ticker AMZN at currentTimeMS 1744244287639: Topic test_topic not present in metadata after 100 ms.
Error sending message 3 for ticker DELL at currentTimeMS 1744244287639: Topic test_topic not present in metadata after 100 ms.
Error sending message 1 for ticker AMD at currentTimeMS 1744244287639: Topic test_topic not present in metadata after 100 ms.
Error sending message 4 for ticker INTC at currentTimeMS 1744244287650: Topic test_topic not present in metadata after 100 ms.
Received message number 5 from /127.0.0.1:51586
Message 5 for ticker: LCID handled by thread: pool-2-thread-5
Valuation for ticker: LCID: -0.9268562030075185
Publishing kafka message: 5 for ticker: LCID
Error sending message 5 for ticker LCID at currentTimeMS 1744244287957: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 1 processed by KafkaMessagePublisher for: AMD
ComputeValuation: message 3 processed by KafkaMessagePublisher for: DELL
ComputeValuation: message 5 processed by KafkaMessagePublisher for: LCID
ComputeValuation: message 2 processed by KafkaMessagePublisher for: AMZN
ComputeValuation: message 4 processed by KafkaMessagePublisher for: INTC
Received message number 6 from /127.0.0.1:51586
Message 6 for ticker: MTH handled by thread: pool-2-thread-6
Valuation for ticker: MTH: 15.394479699248121
Publishing kafka message: 6 for ticker: MTH
Error sending message 6 for ticker MTH at currentTimeMS 1744244288174: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 6 processed by KafkaMessagePublisher for: MTH
Received message number 7 from /127.0.0.1:51586
Message 7 for ticker: MCHP handled by thread: pool-2-thread-7
Valuation for ticker: MCHP: 1.5717801694943607
Publishing kafka message: 7 for ticker: MCHP
Error sending message 7 for ticker MCHP at currentTimeMS 1744244288443: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 7 processed by KafkaMessagePublisher for: MCHP
Received message number 8 from /127.0.0.1:51586
Message 8 for ticker: PYPL handled by thread: pool-2-thread-8
Valuation for ticker: PYPL: 6.206217669172933
Publishing kafka message: 8 for ticker: PYPL
Error sending message 8 for ticker PYPL at currentTimeMS 1744244288696: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 8 processed by KafkaMessagePublisher for: PYPL
Received message number 9 from /127.0.0.1:51586
Message 9 for ticker: PBR handled by thread: pool-2-thread-3
Valuation for ticker: PBR: 2.3553785715266917
Publishing kafka message: 9 for ticker: PBR
ComputeValuation: message 9 processed by KafkaMessagePublisher for: PBR
Sent message number=9 at currentTimeMS=1744244288967 with value={"ticker":"PBR","ttm_eps":1.16,"price_tgt":16.27921,"price":11.46,"1yg":0.0061000003,"LTG":"NaN","Valuation":2.3553785715266917} to partition=0 offset=38
Received message number 10 from /127.0.0.1:51586
Message 10 for ticker: PONY handled by thread: pool-2-thread-1
Valuation for ticker: PONY: -2.3336015037593985
Publishing kafka message: 10 for ticker: PONY
ComputeValuation: message 10 processed by KafkaMessagePublisher for: PONY
Sent message number=10 at currentTimeMS=1744244289308 with value={"ticker":"PONY","ttm_eps":-2.4,"price_tgt":21.75,"price":5.77,"1yg":0.0041,"LTG":"NaN","Valuation":-2.3336015037593985} to partition=0 offset=39
Received message number 11 from /127.0.0.1:51586
Message 11 for ticker: IOT handled by thread: pool-2-thread-5
Valuation for ticker: IOT: 0.4312834586466166
Publishing kafka message: 11 for ticker: IOT
ComputeValuation: message 11 processed by KafkaMessagePublisher for: IOT
Sent message number=11 at currentTimeMS=1744244289577 with value={"ticker":"IOT","ttm_eps":-0.28,"price_tgt":48.56333,"price":34.16,"1yg":0.3466,"LTG":"NaN","Valuation":0.4312834586466166} to partition=0 offset=40
Received message number 12 from /127.0.0.1:51586
Message 12 for ticker: SNOW handled by thread: pool-2-thread-2
Valuation for ticker: SNOW: -4.645207894736841
Publishing kafka message: 12 for ticker: SNOW
ComputeValuation: message 12 processed by KafkaMessagePublisher for: SNOW
Sent message number=12 at currentTimeMS=1744244289851 with value={"ticker":"SNOW","ttm_eps":-3.86,"price_tgt":201.862,"price":133.51,"1yg":0.3614,"LTG":"NaN","Valuation":-4.645207894736841} to partition=0 offset=41
Received message number 13 from /127.0.0.1:51586
Message 13 for ticker: TGT handled by thread: pool-2-thread-4
Valuation for ticker: TGT: 12.680315426024436
Publishing kafka message: 13 for ticker: TGT
ComputeValuation: message 13 processed by KafkaMessagePublisher for: TGT
Sent message number=13 at currentTimeMS=1744244290103 with value={"ticker":"TGT","ttm_eps":8.86,"price_tgt":133.96875,"price":88.76,"1yg":0.078200005,"LTG":"NaN","Valuation":12.680315426024436} to partition=0 offset=42
Received message number 14 from /127.0.0.1:51586
Message 14 for ticker: WMT handled by thread: pool-2-thread-6
Valuation for ticker: WMT: 4.079865504121241
Publishing kafka message: 14 for ticker: WMT
ComputeValuation: message 14 processed by KafkaMessagePublisher for: WMT
Sent message number=14 at currentTimeMS=1744244290344 with value={"ticker":"WMT","ttm_eps":2.41,"price_tgt":107.4085,"price":81.79,"1yg":0.120299995,"LTG":"NaN","Valuation":4.079865504121241} to partition=0 offset=43
Received message number 15 from /127.0.0.1:51586
Message 15 for ticker: BAC handled by thread: pool-2-thread-7
Valuation for ticker: BAC: 5.2086875
Publishing kafka message: 15 for ticker: BAC
ComputeValuation: message 15 processed by KafkaMessagePublisher for: BAC
Sent message number=15 at currentTimeMS=1744244290570 with value={"ticker":"BAC","ttm_eps":3.21,"price_tgt":50.02381,"price":35.03,"1yg":0.1745,"LTG":"NaN","Valuation":5.2086875} to partition=0 offset=44
Received message number 16 from /127.0.0.1:51586
Message 16 for ticker: AI handled by thread: pool-2-thread-8
Valuation for ticker: AI: -2.1360657894736836
Publishing kafka message: 16 for ticker: AI
ComputeValuation: message 16 processed by KafkaMessagePublisher for: AI
Sent message number=16 at currentTimeMS=1744244290844 with value={"ticker":"AI","ttm_eps":-2.23,"price_tgt":30.99867,"price":18.24,"1yg":0.046,"LTG":"NaN","Valuation":-2.1360657894736836} to partition=0 offset=45
Received message number 17 from /127.0.0.1:51586
Message 17 for ticker: ENPH handled by thread: pool-2-thread-3
Valuation for ticker: ENPH: 1.8633082706766917
Publishing kafka message: 17 for ticker: ENPH
ComputeValuation: message 17 processed by KafkaMessagePublisher for: ENPH
Sent message number=17 at currentTimeMS=1744244291076 with value={"ticker":"ENPH","ttm_eps":0.75,"price_tgt":78.40611,"price":49.52,"1yg":0.2336,"LTG":"NaN","Valuation":1.8633082706766917} to partition=0 offset=46
Received message number 18 from /127.0.0.1:51586
Message 18 for ticker: FSLR handled by thread: pool-2-thread-1
Valuation for ticker: FSLR: 18.165239747951127
Publishing kafka message: 18 for ticker: FSLR
ComputeValuation: message 18 processed by KafkaMessagePublisher for: FSLR
Sent message number=18 at currentTimeMS=1744244291387 with value={"ticker":"FSLR","ttm_eps":12.02,"price_tgt":236.7344,"price":120.38,"1yg":0.44919997,"LTG":"NaN","Valuation":18.165239747951127} to partition=0 offset=47
Received message number 19 from /127.0.0.1:51586
Message 19 for ticker: JPM handled by thread: pool-2-thread-5
Valuation for ticker: JPM: 27.21149624060151
Publishing kafka message: 19 for ticker: JPM
ComputeValuation: message 19 processed by KafkaMessagePublisher for: JPM
Sent message number=19 at currentTimeMS=1744244291628 with value={"ticker":"JPM","ttm_eps":19.76,"price_tgt":260.1195,"price":216.87,"1yg":0.069,"LTG":"NaN","Valuation":27.21149624060151} to partition=0 offset=48
Received message number 20 from /127.0.0.1:51586
Message 20 for ticker: PLTR handled by thread: pool-2-thread-2
Valuation for ticker: PLTR: 1.0904283834586466
Publishing kafka message: 20 for ticker: PLTR
ComputeValuation: message 20 processed by KafkaMessagePublisher for: PLTR
Sent message number=20 at currentTimeMS=1744244291879 with value={"ticker":"PLTR","ttm_eps":0.19,"price_tgt":86.76818,"price":77.32,"1yg":0.2494,"LTG":"NaN","Valuation":1.0904283834586466} to partition=0 offset=49
Received message number 21 from /127.0.0.1:51586
Message 21 for ticker: GOOG handled by thread: pool-2-thread-4
Valuation for ticker: GOOG: 11.734212406015036
Publishing kafka message: 21 for ticker: GOOG
ComputeValuation: message 21 processed by KafkaMessagePublisher for: GOOG
Sent message number=21 at currentTimeMS=1744244292133 with value={"ticker":"GOOG","ttm_eps":8.05,"price_tgt":210.23529,"price":146.58,"1yg":0.1388,"LTG":"NaN","Valuation":11.734212406015036} to partition=0 offset=50
Received message number 22 from /127.0.0.1:51586
Message 22 for ticker: AAPL handled by thread: pool-2-thread-6
Valuation for ticker: AAPL: 9.294921052631578
Publishing kafka message: 22 for ticker: AAPL
ComputeValuation: message 22 processed by KafkaMessagePublisher for: AAPL
Sent message number=22 at currentTimeMS=1744244292440 with value={"ticker":"AAPL","ttm_eps":6.29,"price_tgt":239.5995,"price":172.42,"1yg":0.108,"LTG":"NaN","Valuation":9.294921052631578} to partition=0 offset=51
Received message number 23 from /127.0.0.1:51586
Message 23 for ticker: SMCI handled by thread: pool-2-thread-7
Valuation for ticker: SMCI: 4.119396616541352
Publishing kafka message: 23 for ticker: SMCI
ComputeValuation: message 23 processed by KafkaMessagePublisher for: SMCI
Sent message number=23 at currentTimeMS=1744244292683 with value={"ticker":"SMCI","ttm_eps":2.3,"price_tgt":52.19357,"price":31.71,"1yg":0.4102,"LTG":"NaN","Valuation":4.119396616541352} to partition=0 offset=52
Received message number 24 from /127.0.0.1:51586
Message 24 for ticker: WOLF handled by thread: pool-2-thread-8
Valuation for ticker: WOLF: -10.027034868421053
Publishing kafka message: 24 for ticker: WOLF
ComputeValuation: message 24 processed by KafkaMessagePublisher for: WOLF
Sent message number=24 at currentTimeMS=1744244292952 with value={"ticker":"WOLF","ttm_eps":-7.69,"price_tgt":7.16923,"price":2.18,"1yg":0.3393,"LTG":"NaN","Valuation":-10.027034868421053} to partition=0 offset=53
Received message number 25 from /127.0.0.1:51586
Message 25 for ticker: KC handled by thread: pool-2-thread-3
Valuation for ticker: KC: -0.8966976503759396
Publishing kafka message: 25 for ticker: KC
ComputeValuation: message 25 processed by KafkaMessagePublisher for: KC
Sent message number=25 at currentTimeMS=1744244293205 with value={"ticker":"KC","ttm_eps":-1.11,"price_tgt":17.2882,"price":11.465,"1yg":0.8411,"LTG":"NaN","Valuation":-0.8966976503759396} to partition=0 offset=54
Received message number 26 from /127.0.0.1:51586
Message 26 for ticker: EVLV handled by thread: pool-2-thread-1
Valuation for ticker: EVLV: 0.6650988721804512
Publishing kafka message: 26 for ticker: EVLV
ComputeValuation: message 26 processed by KafkaMessagePublisher for: EVLV
Sent message number=26 at currentTimeMS=1744244293458 with value={"ticker":"EVLV","ttm_eps":-0.11,"price_tgt":4.75,"price":3.0,"1yg":0.5556,"LTG":"NaN","Valuation":0.6650988721804512} to partition=0 offset=55
Received message number 27 from /127.0.0.1:51586
Message 27 for ticker: OKTA handled by thread: pool-2-thread-5
Valuation for ticker: OKTA: 0.9077625939849624
Publishing kafka message: 27 for ticker: OKTA
ComputeValuation: message 27 processed by KafkaMessagePublisher for: OKTA
Sent message number=27 at currentTimeMS=1744244293705 with value={"ticker":"OKTA","ttm_eps":0.06,"price_tgt":117.28795,"price":91.39,"1yg":0.1033,"LTG":"NaN","Valuation":0.9077625939849624} to partition=0 offset=56
Received message number 28 from /127.0.0.1:51586
Message 28 for ticker: QRVO handled by thread: pool-2-thread-2
Valuation for ticker: QRVO: 1.1993255641466165
Publishing kafka message: 28 for ticker: QRVO
ComputeValuation: message 28 processed by KafkaMessagePublisher for: QRVO
Sent message number=28 at currentTimeMS=1744244293921 with value={"ticker":"QRVO","ttm_eps":0.28,"price_tgt":91.1219,"price":50.81,"1yg":0.048600003,"LTG":"NaN","Valuation":1.1993255641466165} to partition=0 offset=57
Received message number 29 from /127.0.0.1:51586
Message 29 for ticker: JNPR handled by thread: pool-2-thread-4
Valuation for ticker: JNPR: 1.9767842105263156
Publishing kafka message: 29 for ticker: JNPR
ComputeValuation: message 29 processed by KafkaMessagePublisher for: JNPR
Sent message number=29 at currentTimeMS=1744244294171 with value={"ticker":"JNPR","ttm_eps":0.86,"price_tgt":39.88889,"price":33.93,"1yg":0.0748,"LTG":"NaN","Valuation":1.9767842105263156} to partition=0 offset=58
Received message number 30 from /127.0.0.1:51586
Message 30 for ticker: UBER handled by thread: pool-2-thread-6
Valuation for ticker: UBER: 7.227053383458645
Publishing kafka message: 30 for ticker: UBER
ComputeValuation: message 30 processed by KafkaMessagePublisher for: UBER
Sent message number=30 at currentTimeMS=1744244294387 with value={"ticker":"UBER","ttm_eps":4.56,"price_tgt":88.7798,"price":65.07,"1yg":0.3111,"LTG":"NaN","Valuation":7.227053383458645} to partition=0 offset=59
Received message number 31 from /127.0.0.1:51586
Message 31 for ticker: DKNG handled by thread: pool-2-thread-7
Valuation for ticker: DKNG: -0.7652119242481202
Publishing kafka message: 31 for ticker: DKNG
ComputeValuation: message 31 processed by KafkaMessagePublisher for: DKNG
Sent message number=31 at currentTimeMS=1744244294634 with value={"ticker":"DKNG","ttm_eps":-1.05,"price_tgt":56.725,"price":31.89,"1yg":0.71169996,"LTG":"NaN","Valuation":-0.7652119242481202} to partition=0 offset=60
Received message number 32 from /127.0.0.1:51586
Message 32 for ticker: RBRK handled by thread: pool-2-thread-8
Valuation for ticker: RBRK: -9.987507894736842
Publishing kafka message: 32 for ticker: RBRK
ComputeValuation: message 32 processed by KafkaMessagePublisher for: RBRK
Sent message number=32 at currentTimeMS=1744244294864 with value={"ticker":"RBRK","ttm_eps":-7.48,"price_tgt":78.4225,"price":52.81,"1yg":0.4611,"LTG":"NaN","Valuation":-9.987507894736842} to partition=0 offset=61
Received message number 33 from /127.0.0.1:51586
Message 33 for ticker: ORCL handled by thread: pool-2-thread-3
Valuation for ticker: ORCL: 6.57718685411654
Publishing kafka message: 33 for ticker: ORCL
ComputeValuation: message 33 processed by KafkaMessagePublisher for: ORCL
Sent message number=33 at currentTimeMS=1744244295095 with value={"ticker":"ORCL","ttm_eps":4.26,"price_tgt":184.26471,"price":124.5,"1yg":0.12060001,"LTG":"NaN","Valuation":6.57718685411654} to partition=0 offset=62
Received message number 34 from /127.0.0.1:51586
Message 34 for ticker: MRVL handled by thread: pool-2-thread-1
Valuation for ticker: MRVL: -0.6037603383458645
Publishing kafka message: 34 for ticker: MRVL
ComputeValuation: message 34 processed by KafkaMessagePublisher for: MRVL
Sent message number=34 at currentTimeMS=1744244295307 with value={"ticker":"MRVL","ttm_eps":-1.02,"price_tgt":110.17944,"price":50.03,"1yg":0.3085,"LTG":"NaN","Valuation":-0.6037603383458645} to partition=0 offset=63
Received message number 35 from /127.0.0.1:51586
Message 35 for ticker: NKE handled by thread: pool-2-thread-5
Valuation for ticker: NKE: 4.781907800497273
Publishing kafka message: 35 for ticker: NKE
ComputeValuation: message 35 processed by KafkaMessagePublisher for: NKE
Sent message number=35 at currentTimeMS=1744244295551 with value={"ticker":"NKE","ttm_eps":3.01,"price_tgt":79.68088,"price":53.27,"1yg":-0.0067000003,"LTG":"NaN","Valuation":4.781907800497273} to partition=0 offset=64
Received message number 36 from /127.0.0.1:51586
Message 36 for ticker: SNAP handled by thread: pool-2-thread-2
Valuation for ticker: SNAP: 0.21924003759398505
Publishing kafka message: 36 for ticker: SNAP
ComputeValuation: message 36 processed by KafkaMessagePublisher for: SNAP
Sent message number=36 at currentTimeMS=1744244295778 with value={"ticker":"SNAP","ttm_eps":-0.42,"price_tgt":12.54361,"price":7.23,"1yg":0.4661,"LTG":"NaN","Valuation":0.21924003759398505} to partition=0 offset=65
Received message number 37 from /127.0.0.1:51586
Message 37 for ticker: OKLO handled by thread: pool-2-thread-4
Valuation for ticker: OKLO: -0.11118834586466154
Publishing kafka message: 37 for ticker: OKLO
ComputeValuation: message 37 processed by KafkaMessagePublisher for: OKLO
Sent message number=37 at currentTimeMS=1744244295999 with value={"ticker":"OKLO","ttm_eps":-0.74,"price_tgt":48.48833,"price":20.23,"1yg":-0.1698,"LTG":"NaN","Valuation":-0.11118834586466154} to partition=0 offset=66
Received message number 38 from /127.0.0.1:51586
Message 38 for ticker: ICE handled by thread: pool-2-thread-6
Valuation for ticker: ICE: 7.270858082706766
Publishing kafka message: 38 for ticker: ICE
ComputeValuation: message 38 processed by KafkaMessagePublisher for: ICE
Sent message number=38 at currentTimeMS=1744244296260 with value={"ticker":"ICE","ttm_eps":4.78,"price_tgt":188.5,"price":151.62,"1yg":0.1145,"LTG":"NaN","Valuation":7.270858082706766} to partition=0 offset=67
Received message number 39 from /127.0.0.1:51586
Message 39 for ticker: CME handled by thread: pool-2-thread-7
Valuation for ticker: CME: 13.67617105263158
Publishing kafka message: 39 for ticker: CME
ComputeValuation: message 39 processed by KafkaMessagePublisher for: CME
Sent message number=39 at currentTimeMS=1744244296582 with value={"ticker":"CME","ttm_eps":9.67,"price_tgt":265.82352,"price":255.03,"1yg":0.046,"LTG":"NaN","Valuation":13.67617105263158} to partition=0 offset=68
Received message number 40 from /127.0.0.1:51586
Message 40 for ticker: CBOE handled by thread: pool-2-thread-8
Valuation for ticker: CBOE: 10.447526315789473
Publishing kafka message: 40 for ticker: CBOE
ComputeValuation: message 40 processed by KafkaMessagePublisher for: CBOE
Sent message number=40 at currentTimeMS=1744244296789 with value={"ticker":"CBOE","ttm_eps":7.2,"price_tgt":222.0,"price":208.13,"1yg":0.0723,"LTG":"NaN","Valuation":10.447526315789473} to partition=0 offset=69
Received message number 41 from /127.0.0.1:51586
Message 41 for ticker: NDAQ handled by thread: pool-2-thread-3
Valuation for ticker: NDAQ: 3.4341276315789475
Publishing kafka message: 41 for ticker: NDAQ
ComputeValuation: message 41 processed by KafkaMessagePublisher for: NDAQ
Sent message number=41 at currentTimeMS=1744244297025 with value={"ticker":"NDAQ","ttm_eps":1.93,"price_tgt":84.33333,"price":66.4,"1yg":0.1242,"LTG":"NaN","Valuation":3.4341276315789475} to partition=0 offset=70
Received message number 42 from /127.0.0.1:51586
Message 42 for ticker: APLD handled by thread: pool-2-thread-1
Valuation for ticker: APLD: -1.68278947368421
Publishing kafka message: 42 for ticker: APLD
ComputeValuation: message 42 processed by KafkaMessagePublisher for: APLD
Sent message number=42 at currentTimeMS=1744244297229 with value={"ticker":"APLD","ttm_eps":-1.9,"price_tgt":12.44444,"price":5.08,"1yg":0.0184,"LTG":"NaN","Valuation":-1.68278947368421} to partition=0 offset=71
Received message number 43 from /127.0.0.1:51586
Message 43 for ticker: CEG handled by thread: pool-2-thread-5
Received message number 42 from /127.0.0.1:51586
Message 42 for ticker: APLD handled by thread: pool-2-thread-1
Valuation for ticker: APLD: -1.68278947368421
Publishing kafka message: 42 for ticker: APLD
ComputeValuation: message 42 processed by KafkaMessagePublisher for: APLD
Sent message number=42 at currentTimeMS=1744244297229 with value={"ticker":"APLD","ttm_eps":-1.9,"price_tgt":12.44444,"price":5.08,"1yg":0.0184,"LTG":"NaN","Valuation":-1.68278947368421} to partition=0 offset=71
Received message number 43 from /127.0.0.1:51586
Message 43 for ticker: CEG handled by thread: pool-2-thread-5
Valuation for ticker: APLD: -1.68278947368421
Publishing kafka message: 42 for ticker: APLD
ComputeValuation: message 42 processed by KafkaMessagePublisher for: APLD
Sent message number=42 at currentTimeMS=1744244297229 with value={"ticker":"APLD","ttm_eps":-1.9,"price_tgt":12.44444,"price":5.08,"1yg":0.0184,"LTG":"NaN","Valuation":-1.68278947368421} to partition=0 offset=71
Received message number 43 from /127.0.0.1:51586
Message 43 for ticker: CEG handled by thread: pool-2-thread-5
ComputeValuation: message 42 processed by KafkaMessagePublisher for: APLD
Sent message number=42 at currentTimeMS=1744244297229 with value={"ticker":"APLD","ttm_eps":-1.9,"price_tgt":12.44444,"price":5.08,"1yg":0.0184,"LTG":"NaN","Valuation":-1.68278947368421} to partition=0 offset=71
Received message number 43 from /127.0.0.1:51586
Message 43 for ticker: CEG handled by thread: pool-2-thread-5
Sent message number=42 at currentTimeMS=1744244297229 with value={"ticker":"APLD","ttm_eps":-1.9,"price_tgt":12.44444,"price":5.08,"1yg":0.0184,"LTG":"NaN","Valuation":-1.68278947368421} to partition=0 offset=71
Received message number 43 from /127.0.0.1:51586
Message 43 for ticker: CEG handled by thread: pool-2-thread-5
aluation":-1.68278947368421} to partition=0 offset=71
Received message number 43 from /127.0.0.1:51586
Message 43 for ticker: CEG handled by thread: pool-2-thread-5
Message 43 for ticker: CEG handled by thread: pool-2-thread-5
Valuation for ticker: CEG: 16.86169370300752
Publishing kafka message: 43 for ticker: CEG
ComputeValuation: message 43 processed by KafkaMessagePublisher for: CEG
Sent message number=43 at currentTimeMS=1744244297502 with value={"ticker":"CEG","ttm_eps":11.89,"price_tgt":312.42215,"price":184.94,"1yg":0.1163,"LTG":"NaN","Valuation":16.86169370300752} to partition=0 offset=72
Received message number 44 from /127.0.0.1:51586
Message 44 for ticker: TLN handled by thread: pool-2-thread-2
Valuation for ticker: TLN: 29.49691578947368
Publishing kafka message: 44 for ticker: TLN
ComputeValuation: message 44 processed by KafkaMessagePublisher for: TLN
Sent message number=44 at currentTimeMS=1744244297740 with value={"ticker":"TLN","ttm_eps":17.68,"price_tgt":259.67154,"price":182.615,"1yg":1.0846,"LTG":"NaN","Valuation":29.49691578947368} to partition=0 offset=73
Received message number 45 from /127.0.0.1:51586
ComputeValuation: message 43 processed by KafkaMessagePublisher for: CEG
Sent message number=43 at currentTimeMS=1744244297502 with value={"ticker":"CEG","ttm_eps":11.89,"price_tgt":312.42215,"price":184.94,"1yg":0.1163,"LTG":"NaN","Valuation":16.86169370300752} to partition=0 offset=72
Received message number 44 from /127.0.0.1:51586
Message 44 for ticker: TLN handled by thread: pool-2-thread-2
Valuation for ticker: TLN: 29.49691578947368
Publishing kafka message: 44 for ticker: TLN
ComputeValuation: message 44 processed by KafkaMessagePublisher for: TLN
Sent message number=44 at currentTimeMS=1744244297740 with value={"ticker":"TLN","ttm_eps":17.68,"price_tgt":259.67154,"price":182.615,"1yg":1.0846,"LTG":"NaN","Valuation":29.49691578947368} to partition=0 offset=73
Received message number 45 from /127.0.0.1:51586
Message 44 for ticker: TLN handled by thread: pool-2-thread-2
Valuation for ticker: TLN: 29.49691578947368
Publishing kafka message: 44 for ticker: TLN
ComputeValuation: message 44 processed by KafkaMessagePublisher for: TLN
Sent message number=44 at currentTimeMS=1744244297740 with value={"ticker":"TLN","ttm_eps":17.68,"price_tgt":259.67154,"price":182.615,"1yg":1.0846,"LTG":"NaN","Valuation":29.49691578947368} to partition=0 offset=73
Received message number 45 from /127.0.0.1:51586
Valuation for ticker: TLN: 29.49691578947368
Publishing kafka message: 44 for ticker: TLN
ComputeValuation: message 44 processed by KafkaMessagePublisher for: TLN
Sent message number=44 at currentTimeMS=1744244297740 with value={"ticker":"TLN","ttm_eps":17.68,"price_tgt":259.67154,"price":182.615,"1yg":1.0846,"LTG":"NaN","Valuation":29.49691578947368} to partition=0 offset=73
Received message number 45 from /127.0.0.1:51586
Publishing kafka message: 44 for ticker: TLN
ComputeValuation: message 44 processed by KafkaMessagePublisher for: TLN
Sent message number=44 at currentTimeMS=1744244297740 with value={"ticker":"TLN","ttm_eps":17.68,"price_tgt":259.67154,"price":182.615,"1yg":1.0846,"LTG":"NaN","Valuation":29.49691578947368} to partition=0 offset=73
Received message number 45 from /127.0.0.1:51586
","Valuation":29.49691578947368} to partition=0 offset=73
Received message number 45 from /127.0.0.1:51586
Received message number 45 from /127.0.0.1:51586
Message 45 for ticker: VST handled by thread: pool-2-thread-4
Valuation for ticker: VST: 10.471607142857142
Publishing kafka message: 45 for ticker: VST
ComputeValuation: message 45 processed by KafkaMessagePublisher for: VST
Sent message number=45 at currentTimeMS=1744244297938 with value={"ticker":"VST","ttm_eps":7.0,"price_tgt":168.99944,"price":102.19,"1yg":0.2199,"LTG":"NaN","Valuation":10.471607142857142} to partition=0 offset=74
Messages consumed: 45
DatagramChannel closed.
UDP Server down after 1 minutes.
Executor Service shutdown
Scheduled Executor Service shutdown.
KafkaMessagePublisher shutdown
```

</details>

Note the errors sending the first 5 messages can be quickly addressed by increasing the kafka property ```delivery.timeout.ms``` above 100ms. This property dictates how long we want to wait when searching for a given topic.

#### Publish Messages with broker up, custom 1 thread pool

| Description        | Execution Time | Number of Tickers | Threads |
|--------------------|---------------|-------------------|------|
| Publish messages with broker up        | **18829**         | 45              | 1  |
14245
14037
###### Sample Output
<details>
<summary>Output</summary>

```
Entered shutdownUDPServerAfterSetDuration.
Start time MS: 1744244703912
UDP server up and listening on 127.0.0.1: 5005
Received message number 1 from /127.0.0.1:63077
Message 1 for ticker: AMD handled by thread: pool-2-thread-1
Valuation for ticker: AMD: 2.2381860958646618
Creating kafka publisher
SLF4J(W): No SLF4J providers were found.
SLF4J(W): Defaulting to no-operation (NOP) logger implementation
SLF4J(W): See https://www.slf4j.org/codes.html#noProviders for further details.
Received message number 2 from /127.0.0.1:63077
Received message number 3 from /127.0.0.1:63077
Publishing kafka message: 1 for ticker: AMD
Received message number 4 from /127.0.0.1:63077
Error sending message 1 for ticker AMD at currentTimeMS 1744244712495: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 1 processed by KafkaMessagePublisher for: AMD
Message 2 for ticker: AMZN handled by thread: pool-2-thread-1
Valuation for ticker: AMZN: 8.411951237396616
Publishing kafka message: 2 for ticker: AMZN
Received message number 5 from /127.0.0.1:63077
Error sending message 2 for ticker AMZN at currentTimeMS 1744244712788: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 2 processed by KafkaMessagePublisher for: AMZN
Message 3 for ticker: DELL handled by thread: pool-2-thread-1
Valuation for ticker: DELL: 9.463033270676691
Publishing kafka message: 3 for ticker: DELL
Error sending message 3 for ticker DELL at currentTimeMS 1744244712897: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 3 processed by KafkaMessagePublisher for: DELL
Message 4 for ticker: INTC handled by thread: pool-2-thread-1
Valuation for ticker: INTC: -6.547839661654134
Publishing kafka message: 4 for ticker: INTC
Received message number 6 from /127.0.0.1:63077
Error sending message 4 for ticker INTC at currentTimeMS 1744244713007: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 4 processed by KafkaMessagePublisher for: INTC
Message 5 for ticker: LCID handled by thread: pool-2-thread-1
Valuation for ticker: LCID: -0.9268562030075185
Publishing kafka message: 5 for ticker: LCID
Error sending message 5 for ticker LCID at currentTimeMS 1744244713115: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 5 processed by KafkaMessagePublisher for: LCID
Message 6 for ticker: MTH handled by thread: pool-2-thread-1
Valuation for ticker: MTH: 15.394479699248121
Publishing kafka message: 6 for ticker: MTH
Error sending message 6 for ticker MTH at currentTimeMS 1744244713223: Topic test_topic not present in metadata after 100 ms.
ComputeValuation: message 6 processed by KafkaMessagePublisher for: MTH
Received message number 7 from /127.0.0.1:63077
Message 7 for ticker: MCHP handled by thread: pool-2-thread-1
Valuation for ticker: MCHP: 1.5717801694943607
Publishing kafka message: 7 for ticker: MCHP
ComputeValuation: message 7 processed by KafkaMessagePublisher for: MCHP
Sent message number=7 at currentTimeMS=1744244713370 with value={"ticker":"MCHP","ttm_eps":0.57,"price_tgt":64.5187,"price":35.34,"1yg":-0.032899998,"LTG":"NaN","Valuation":1.5717801694943607} to partition=0 offset=75
Received message number 8 from /127.0.0.1:63077
Message 8 for ticker: PYPL handled by thread: pool-2-thread-1
Valuation for ticker: PYPL: 6.206217669172933
Publishing kafka message: 8 for ticker: PYPL
ComputeValuation: message 8 processed by KafkaMessagePublisher for: PYPL
Sent message number=8 at currentTimeMS=1744244713478 with value={"ticker":"PYPL","ttm_eps":3.99,"price_tgt":91.44833,"price":57.41,"1yg":0.1148,"LTG":"NaN","Valuation":6.206217669172933} to partition=0 offset=76
Received message number 9 from /127.0.0.1:63077
Message 9 for ticker: PBR handled by thread: pool-2-thread-1
Valuation for ticker: PBR: 2.3553785715266917
Publishing kafka message: 9 for ticker: PBR
ComputeValuation: message 9 processed by KafkaMessagePublisher for: PBR
Sent message number=9 at currentTimeMS=1744244713822 with value={"ticker":"PBR","ttm_eps":1.16,"price_tgt":16.27921,"price":11.46,"1yg":0.0061000003,"LTG":"NaN","Valuation":2.3553785715266917} to partition=0 offset=77
Received message number 10 from /127.0.0.1:63077
Message 10 for ticker: PONY handled by thread: pool-2-thread-1
Valuation for ticker: PONY: -2.3336015037593985
Publishing kafka message: 10 for ticker: PONY
ComputeValuation: message 10 processed by KafkaMessagePublisher for: PONY
Sent message number=10 at currentTimeMS=1744244714039 with value={"ticker":"PONY","ttm_eps":-2.4,"price_tgt":21.75,"price":5.77,"1yg":0.0041,"LTG":"NaN","Valuation":-2.3336015037593985} to partition=0 offset=78
Received message number 11 from /127.0.0.1:63077
Message 11 for ticker: IOT handled by thread: pool-2-thread-1
Valuation for ticker: IOT: 0.4312834586466166
Publishing kafka message: 11 for ticker: IOT
ComputeValuation: message 11 processed by KafkaMessagePublisher for: IOT
Sent message number=11 at currentTimeMS=1744244714262 with value={"ticker":"IOT","ttm_eps":-0.28,"price_tgt":48.56333,"price":34.16,"1yg":0.3466,"LTG":"NaN","Valuation":0.4312834586466166} to partition=0 offset=79
Received message number 12 from /127.0.0.1:63077
Message 12 for ticker: SNOW handled by thread: pool-2-thread-1
Valuation for ticker: SNOW: -4.645207894736841
Publishing kafka message: 12 for ticker: SNOW
ComputeValuation: message 12 processed by KafkaMessagePublisher for: SNOW
Sent message number=12 at currentTimeMS=1744244714557 with value={"ticker":"SNOW","ttm_eps":-3.86,"price_tgt":201.862,"price":133.51,"1yg":0.3614,"LTG":"NaN","Valuation":-4.645207894736841} to partition=0 offset=80
Received message number 13 from /127.0.0.1:63077
Message 13 for ticker: TGT handled by thread: pool-2-thread-1
Valuation for ticker: TGT: 12.680315426024436
Publishing kafka message: 13 for ticker: TGT
ComputeValuation: message 13 processed by KafkaMessagePublisher for: TGT
Sent message number=13 at currentTimeMS=1744244714786 with value={"ticker":"TGT","ttm_eps":8.86,"price_tgt":133.96875,"price":88.76,"1yg":0.078200005,"LTG":"NaN","Valuation":12.680315426024436} to partition=0 offset=81
Received message number 14 from /127.0.0.1:63077
Message 14 for ticker: WMT handled by thread: pool-2-thread-1
Valuation for ticker: WMT: 4.079865504121241
Publishing kafka message: 14 for ticker: WMT
ComputeValuation: message 14 processed by KafkaMessagePublisher for: WMT
Sent message number=14 at currentTimeMS=1744244714996 with value={"ticker":"WMT","ttm_eps":2.41,"price_tgt":107.4085,"price":81.79,"1yg":0.120299995,"LTG":"NaN","Valuation":4.079865504121241} to partition=0 offset=82
Received message number 15 from /127.0.0.1:63077
Message 15 for ticker: BAC handled by thread: pool-2-thread-1
Valuation for ticker: BAC: 5.2086875
Publishing kafka message: 15 for ticker: BAC
ComputeValuation: message 15 processed by KafkaMessagePublisher for: BAC
Sent message number=15 at currentTimeMS=1744244715232 with value={"ticker":"BAC","ttm_eps":3.21,"price_tgt":50.02381,"price":35.03,"1yg":0.1745,"LTG":"NaN","Valuation":5.2086875} to partition=0 offset=83
Received message number 16 from /127.0.0.1:63077
Message 16 for ticker: AI handled by thread: pool-2-thread-1
Valuation for ticker: AI: -2.1360657894736836
Publishing kafka message: 16 for ticker: AI
ComputeValuation: message 16 processed by KafkaMessagePublisher for: AI
Sent message number=16 at currentTimeMS=1744244715466 with value={"ticker":"AI","ttm_eps":-2.23,"price_tgt":30.99867,"price":18.24,"1yg":0.046,"LTG":"NaN","Valuation":-2.1360657894736836} to partition=0 offset=84
Received message number 17 from /127.0.0.1:63077
Message 17 for ticker: ENPH handled by thread: pool-2-thread-1
Valuation for ticker: ENPH: 1.8633082706766917
Publishing kafka message: 17 for ticker: ENPH
ComputeValuation: message 17 processed by KafkaMessagePublisher for: ENPH
Sent message number=17 at currentTimeMS=1744244715730 with value={"ticker":"ENPH","ttm_eps":0.75,"price_tgt":78.40611,"price":49.52,"1yg":0.2336,"LTG":"NaN","Valuation":1.8633082706766917} to partition=0 offset=85
Received message number 18 from /127.0.0.1:63077
Message 18 for ticker: FSLR handled by thread: pool-2-thread-1
Valuation for ticker: FSLR: 18.165239747951127
Publishing kafka message: 18 for ticker: FSLR
ComputeValuation: message 18 processed by KafkaMessagePublisher for: FSLR
Sent message number=18 at currentTimeMS=1744244715946 with value={"ticker":"FSLR","ttm_eps":12.02,"price_tgt":236.7344,"price":120.38,"1yg":0.44919997,"LTG":"NaN","Valuation":18.165239747951127} to partition=0 offset=86
Received message number 19 from /127.0.0.1:63077
Message 19 for ticker: JPM handled by thread: pool-2-thread-1
Valuation for ticker: JPM: 27.21149624060151
Publishing kafka message: 19 for ticker: JPM
ComputeValuation: message 19 processed by KafkaMessagePublisher for: JPM
Error sending message 19 for ticker JPM at currentTimeMS 1744244716274: Expiring 1 record(s) for test_topic-0:115 ms has passed since batch creation
Received message number 20 from /127.0.0.1:63077
Message 20 for ticker: PLTR handled by thread: pool-2-thread-1
Valuation for ticker: PLTR: 1.0904283834586466
Publishing kafka message: 20 for ticker: PLTR
ComputeValuation: message 20 processed by KafkaMessagePublisher for: PLTR
Sent message number=20 at currentTimeMS=1744244716453 with value={"ticker":"PLTR","ttm_eps":0.19,"price_tgt":86.76818,"price":77.32,"1yg":0.2494,"LTG":"NaN","Valuation":1.0904283834586466} to partition=0 offset=88
Received message number 21 from /127.0.0.1:63077
Message 21 for ticker: GOOG handled by thread: pool-2-thread-1
Valuation for ticker: GOOG: 11.734212406015036
Publishing kafka message: 21 for ticker: GOOG
ComputeValuation: message 21 processed by KafkaMessagePublisher for: GOOG
Sent message number=21 at currentTimeMS=1744244716710 with value={"ticker":"GOOG","ttm_eps":8.05,"price_tgt":210.23529,"price":146.58,"1yg":0.1388,"LTG":"NaN","Valuation":11.734212406015036} to partition=0 offset=89
Received message number 22 from /127.0.0.1:63077
Message 22 for ticker: AAPL handled by thread: pool-2-thread-1
Valuation for ticker: AAPL: 9.294921052631578
Publishing kafka message: 22 for ticker: AAPL
ComputeValuation: message 22 processed by KafkaMessagePublisher for: AAPL
Sent message number=22 at currentTimeMS=1744244716956 with value={"ticker":"AAPL","ttm_eps":6.29,"price_tgt":239.5995,"price":172.42,"1yg":0.108,"LTG":"NaN","Valuation":9.294921052631578} to partition=0 offset=90
Received message number 23 from /127.0.0.1:63077
Message 23 for ticker: SMCI handled by thread: pool-2-thread-1
Valuation for ticker: SMCI: 4.119396616541352
Publishing kafka message: 23 for ticker: SMCI
ComputeValuation: message 23 processed by KafkaMessagePublisher for: SMCI
Sent message number=23 at currentTimeMS=1744244717174 with value={"ticker":"SMCI","ttm_eps":2.3,"price_tgt":52.19357,"price":31.71,"1yg":0.4102,"LTG":"NaN","Valuation":4.119396616541352} to partition=0 offset=91
Received message number 24 from /127.0.0.1:63077
Message 24 for ticker: WOLF handled by thread: pool-2-thread-1
Valuation for ticker: WOLF: -10.027034868421053
Publishing kafka message: 24 for ticker: WOLF
ComputeValuation: message 24 processed by KafkaMessagePublisher for: WOLF
Sent message number=24 at currentTimeMS=1744244717479 with value={"ticker":"WOLF","ttm_eps":-7.69,"price_tgt":7.16923,"price":2.18,"1yg":0.3393,"LTG":"NaN","Valuation":-10.027034868421053} to partition=0 offset=92
Received message number 25 from /127.0.0.1:63077
Message 25 for ticker: KC handled by thread: pool-2-thread-1
Valuation for ticker: KC: -0.8966976503759396
Publishing kafka message: 25 for ticker: KC
ComputeValuation: message 25 processed by KafkaMessagePublisher for: KC
Sent message number=25 at currentTimeMS=1744244717744 with value={"ticker":"KC","ttm_eps":-1.11,"price_tgt":17.2882,"price":11.465,"1yg":0.8411,"LTG":"NaN","Valuation":-0.8966976503759396} to partition=0 offset=93
Received message number 26 from /127.0.0.1:63077
Message 26 for ticker: EVLV handled by thread: pool-2-thread-1
Valuation for ticker: EVLV: 0.6650988721804512
Publishing kafka message: 26 for ticker: EVLV
ComputeValuation: message 26 processed by KafkaMessagePublisher for: EVLV
Sent message number=26 at currentTimeMS=1744244717962 with value={"ticker":"EVLV","ttm_eps":-0.11,"price_tgt":4.75,"price":3.0,"1yg":0.5556,"LTG":"NaN","Valuation":0.6650988721804512} to partition=0 offset=94
Received message number 27 from /127.0.0.1:63077
Message 27 for ticker: OKTA handled by thread: pool-2-thread-1
Valuation for ticker: OKTA: 0.9077625939849624
Publishing kafka message: 27 for ticker: OKTA
ComputeValuation: message 27 processed by KafkaMessagePublisher for: OKTA
Sent message number=27 at currentTimeMS=1744244718293 with value={"ticker":"OKTA","ttm_eps":0.06,"price_tgt":117.28795,"price":91.39,"1yg":0.1033,"LTG":"NaN","Valuation":0.9077625939849624} to partition=0 offset=95
Received message number 28 from /127.0.0.1:63077
Message 28 for ticker: QRVO handled by thread: pool-2-thread-1
Valuation for ticker: QRVO: 1.1993255641466165
Publishing kafka message: 28 for ticker: QRVO
ComputeValuation: message 28 processed by KafkaMessagePublisher for: QRVO
Sent message number=28 at currentTimeMS=1744244718530 with value={"ticker":"QRVO","ttm_eps":0.28,"price_tgt":91.1219,"price":50.81,"1yg":0.048600003,"LTG":"NaN","Valuation":1.1993255641466165} to partition=0 offset=96
Received message number 29 from /127.0.0.1:63077
Message 29 for ticker: JNPR handled by thread: pool-2-thread-1
Valuation for ticker: JNPR: 1.9767842105263156
Publishing kafka message: 29 for ticker: JNPR
ComputeValuation: message 29 processed by KafkaMessagePublisher for: JNPR
Sent message number=29 at currentTimeMS=1744244718795 with value={"ticker":"JNPR","ttm_eps":0.86,"price_tgt":39.88889,"price":33.93,"1yg":0.0748,"LTG":"NaN","Valuation":1.9767842105263156} to partition=0 offset=97
Received message number 30 from /127.0.0.1:63077
Message 30 for ticker: UBER handled by thread: pool-2-thread-1
Valuation for ticker: UBER: 7.227053383458645
Publishing kafka message: 30 for ticker: UBER
ComputeValuation: message 30 processed by KafkaMessagePublisher for: UBER
Sent message number=30 at currentTimeMS=1744244719078 with value={"ticker":"UBER","ttm_eps":4.56,"price_tgt":88.7798,"price":65.07,"1yg":0.3111,"LTG":"NaN","Valuation":7.227053383458645} to partition=0 offset=98
Received message number 31 from /127.0.0.1:63077
Message 31 for ticker: DKNG handled by thread: pool-2-thread-1
Valuation for ticker: DKNG: -0.7652119242481202
Publishing kafka message: 31 for ticker: DKNG
ComputeValuation: message 31 processed by KafkaMessagePublisher for: DKNG
Sent message number=31 at currentTimeMS=1744244719311 with value={"ticker":"DKNG","ttm_eps":-1.05,"price_tgt":56.725,"price":31.89,"1yg":0.71169996,"LTG":"NaN","Valuation":-0.7652119242481202} to partition=0 offset=99
Received message number 32 from /127.0.0.1:63077
Message 32 for ticker: RBRK handled by thread: pool-2-thread-1
Valuation for ticker: RBRK: -9.987507894736842
Publishing kafka message: 32 for ticker: RBRK
ComputeValuation: message 32 processed by KafkaMessagePublisher for: RBRK
Sent message number=32 at currentTimeMS=1744244719560 with value={"ticker":"RBRK","ttm_eps":-7.48,"price_tgt":78.4225,"price":52.81,"1yg":0.4611,"LTG":"NaN","Valuation":-9.987507894736842} to partition=0 offset=100
Received message number 33 from /127.0.0.1:63077
Message 33 for ticker: ORCL handled by thread: pool-2-thread-1
Valuation for ticker: ORCL: 6.57718685411654
Publishing kafka message: 33 for ticker: ORCL
ComputeValuation: message 33 processed by KafkaMessagePublisher for: ORCL
Sent message number=33 at currentTimeMS=1744244719823 with value={"ticker":"ORCL","ttm_eps":4.26,"price_tgt":184.26471,"price":124.5,"1yg":0.12060001,"LTG":"NaN","Valuation":6.57718685411654} to partition=0 offset=101
Received message number 34 from /127.0.0.1:63077
Message 34 for ticker: MRVL handled by thread: pool-2-thread-1
Valuation for ticker: MRVL: -0.6037603383458645
Publishing kafka message: 34 for ticker: MRVL
ComputeValuation: message 34 processed by KafkaMessagePublisher for: MRVL
Sent message number=34 at currentTimeMS=1744244720035 with value={"ticker":"MRVL","ttm_eps":-1.02,"price_tgt":110.17944,"price":50.03,"1yg":0.3085,"LTG":"NaN","Valuation":-0.6037603383458645} to partition=0 offset=102
Received message number 35 from /127.0.0.1:63077
Message 35 for ticker: NKE handled by thread: pool-2-thread-1
Valuation for ticker: NKE: 4.781907800497273
Publishing kafka message: 35 for ticker: NKE
ComputeValuation: message 35 processed by KafkaMessagePublisher for: NKE
Sent message number=35 at currentTimeMS=1744244720277 with value={"ticker":"NKE","ttm_eps":3.01,"price_tgt":79.68088,"price":53.27,"1yg":-0.0067000003,"LTG":"NaN","Valuation":4.781907800497273} to partition=0 offset=103
Received message number 36 from /127.0.0.1:63077
Message 36 for ticker: SNAP handled by thread: pool-2-thread-1
Valuation for ticker: SNAP: 0.21924003759398505
Publishing kafka message: 36 for ticker: SNAP
ComputeValuation: message 36 processed by KafkaMessagePublisher for: SNAP
Sent message number=36 at currentTimeMS=1744244720535 with value={"ticker":"SNAP","ttm_eps":-0.42,"price_tgt":12.54361,"price":7.23,"1yg":0.4661,"LTG":"NaN","Valuation":0.21924003759398505} to partition=0 offset=104
Received message number 37 from /127.0.0.1:63077
Message 37 for ticker: OKLO handled by thread: pool-2-thread-1
Valuation for ticker: OKLO: -0.11118834586466154
Publishing kafka message: 37 for ticker: OKLO
ComputeValuation: message 37 processed by KafkaMessagePublisher for: OKLO
Sent message number=37 at currentTimeMS=1744244720773 with value={"ticker":"OKLO","ttm_eps":-0.74,"price_tgt":48.48833,"price":20.23,"1yg":-0.1698,"LTG":"NaN","Valuation":-0.11118834586466154} to partition=0 offset=105
Received message number 38 from /127.0.0.1:63077
Message 38 for ticker: ICE handled by thread: pool-2-thread-1
Valuation for ticker: ICE: 7.270858082706766
Publishing kafka message: 38 for ticker: ICE
ComputeValuation: message 38 processed by KafkaMessagePublisher for: ICE
Sent message number=38 at currentTimeMS=1744244721002 with value={"ticker":"ICE","ttm_eps":4.78,"price_tgt":188.5,"price":151.62,"1yg":0.1145,"LTG":"NaN","Valuation":7.270858082706766} to partition=0 offset=106
Received message number 39 from /127.0.0.1:63077
Message 39 for ticker: CME handled by thread: pool-2-thread-1
Valuation for ticker: CME: 13.67617105263158
Publishing kafka message: 39 for ticker: CME
ComputeValuation: message 39 processed by KafkaMessagePublisher for: CME
Sent message number=39 at currentTimeMS=1744244721241 with value={"ticker":"CME","ttm_eps":9.67,"price_tgt":265.82352,"price":255.03,"1yg":0.046,"LTG":"NaN","Valuation":13.67617105263158} to partition=0 offset=107
Received message number 40 from /127.0.0.1:63077
Message 40 for ticker: CBOE handled by thread: pool-2-thread-1
Valuation for ticker: CBOE: 10.447526315789473
Publishing kafka message: 40 for ticker: CBOE
ComputeValuation: message 40 processed by KafkaMessagePublisher for: CBOE
Sent message number=40 at currentTimeMS=1744244721513 with value={"ticker":"CBOE","ttm_eps":7.2,"price_tgt":222.0,"price":208.13,"1yg":0.0723,"LTG":"NaN","Valuation":10.447526315789473} to partition=0 offset=108
Received message number 41 from /127.0.0.1:63077
Message 41 for ticker: NDAQ handled by thread: pool-2-thread-1
Valuation for ticker: NDAQ: 3.4341276315789475
Publishing kafka message: 41 for ticker: NDAQ
ComputeValuation: message 41 processed by KafkaMessagePublisher for: NDAQ
Sent message number=41 at currentTimeMS=1744244721740 with value={"ticker":"NDAQ","ttm_eps":1.93,"price_tgt":84.33333,"price":66.4,"1yg":0.1242,"LTG":"NaN","Valuation":3.4341276315789475} to partition=0 offset=109
Received message number 42 from /127.0.0.1:63077
Message 42 for ticker: APLD handled by thread: pool-2-thread-1
Valuation for ticker: APLD: -1.68278947368421
Publishing kafka message: 42 for ticker: APLD
ComputeValuation: message 42 processed by KafkaMessagePublisher for: APLD
Sent message number=42 at currentTimeMS=1744244721961 with value={"ticker":"APLD","ttm_eps":-1.9,"price_tgt":12.44444,"price":5.08,"1yg":0.0184,"LTG":"NaN","Valuation":-1.68278947368421} to partition=0 offset=110
Received message number 43 from /127.0.0.1:63077
Message 43 for ticker: CEG handled by thread: pool-2-thread-1
Valuation for ticker: CEG: 16.86169370300752
Publishing kafka message: 43 for ticker: CEG
ComputeValuation: message 43 processed by KafkaMessagePublisher for: CEG
Sent message number=43 at currentTimeMS=1744244722281 with value={"ticker":"CEG","ttm_eps":11.89,"price_tgt":312.42215,"price":184.94,"1yg":0.1163,"LTG":"NaN","Valuation":16.86169370300752} to partition=0 offset=111
Received message number 44 from /127.0.0.1:63077
Message 44 for ticker: TLN handled by thread: pool-2-thread-1
Valuation for ticker: TLN: 29.49691578947368
Publishing kafka message: 44 for ticker: TLN
ComputeValuation: message 44 processed by KafkaMessagePublisher for: TLN
Sent message number=44 at currentTimeMS=1744244722509 with value={"ticker":"TLN","ttm_eps":17.68,"price_tgt":259.67154,"price":182.615,"1yg":1.0846,"LTG":"NaN","Valuation":29.49691578947368} to partition=0 offset=112
Received message number 45 from /127.0.0.1:63077
Message 45 for ticker: VST handled by thread: pool-2-thread-1
Valuation for ticker: VST: 10.471607142857142
Publishing kafka message: 45 for ticker: VST
ComputeValuation: message 45 processed by KafkaMessagePublisher for: VST
Sent message number=45 at currentTimeMS=1744244722741 with value={"ticker":"VST","ttm_eps":7.0,"price_tgt":168.99944,"price":102.19,"1yg":0.2199,"LTG":"NaN","Valuation":10.471607142857142} to partition=0 offset=113
UDP Server down after 3 minutes.
Messages consumed: 45
DatagramChannel closed.
Executor Service shutdown
Scheduled Executor Service shutdown.
KafkaMessagePublisher shutdown
```

</details>

## Attempt to Optimize Receiving, Processing and Publishing
My intention was to receive messages in a single thread, and to hand off the processing to another thread(s). From the logs, it looked like
receiving, processing, and publishing were executing as an atomic operation (see logs). I played around with many changes including CompletableFuture, multiple thread pools, different thread sizes, increasing number of tickers (to see if order gets interleaved), datagram channel buffer copy / reuse, and switching to async logging. If you look at the logs, the processing and publishing are in fact getting executed in separate threads. But for a given stock, it doesn't seem to be receiving new messages until the processing is done for the current ticker. Or at least that's what it looks like in the logs. I tried increasing the number of tickers to see if the commands get interweaved, but the operations for each ticker still seem to be atomic and serial. I was testing all this in OptimizedUDPServer. 

### Update
I was testing with the broker down and had lowered some of the timeouts to 100ms. So the async processing was done before the next message was even received,
giving the impression that everything is executing serially. After just increasing it to 300ms from 100ms you can see that some of the messages are sent in a more random manner now as expected. The logs below show how the publishing is getting executed asynchronously and not directly after. 
<details>
<summary>Output</summary>

```
[main] INFO SocketTesting.OptimizedUDPServer - UDP server up and listening on 127.0.0.1: 5005
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-2] INFO Valuation.ComputeValuationCallable - Message for ticker: AMD handled by thread: pool-1-thread-2
[pool-1-thread-2] INFO Valuation.ComputeValuationCallable - Valuation for ticker: AMD: 6.214131578947369
[pool-2-thread-1] INFO SocketTesting.OptimizedUDPServer - Valuation for message 1: {"ticker":"AMD","ttm_eps":1.0,"price_tgt":140.47905,"price":87.5,"1yg":0.3423,"LTG":"NaN","Valuation":6.214131578947369} sent by thread: pool-2-thread-1
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Message for ticker: AMZN handled by thread: pool-1-thread-4
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Valuation for ticker: AMZN: 33.29122369091729
[pool-2-thread-2] INFO SocketTesting.OptimizedUDPServer - Valuation for message 2: {"ticker":"AMZN","ttm_eps":5.52,"price_tgt":249.40323,"price":172.61,"1yg":0.19469999,"LTG":"NaN","Valuation":33.29122369091729} sent by thread: pool-2-thread-2
[pool-2-thread-1] ERROR SocketTesting.OptimizedUDPServer - Error sending message 1 at currentTimeMS 1745291271434: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-6] INFO Valuation.ComputeValuationCallable - Message for ticker: DELL handled by thread: pool-1-thread-6
[pool-1-thread-6] INFO Valuation.ComputeValuationCallable - Valuation for ticker: DELL: 37.940468872180446
[pool-2-thread-3] INFO SocketTesting.OptimizedUDPServer - Valuation for message 3: {"ticker":"DELL","ttm_eps":6.38,"price_tgt":127.06304,"price":84.8,"1yg":0.1268,"LTG":"NaN","Valuation":37.940468872180446} sent by thread: pool-2-thread-3
[pool-2-thread-2] ERROR SocketTesting.OptimizedUDPServer - Error sending message 2 at currentTimeMS 1745291271595: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Message for ticker: INTC handled by thread: pool-1-thread-8
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Valuation for ticker: INTC: -32.41264218045113
[pool-2-thread-4] INFO SocketTesting.OptimizedUDPServer - Valuation for message 4: {"ticker":"INTC","ttm_eps":-4.38,"price_tgt":22.44091,"price":18.93,"1yg":1.2983,"LTG":"NaN","Valuation":-32.41264218045113} sent by thread: pool-2-thread-4
[pool-2-thread-3] ERROR SocketTesting.OptimizedUDPServer - Error sending message 3 at currentTimeMS 1745291271805: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Message for ticker: LCID handled by thread: pool-1-thread-1
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Valuation for ticker: LCID: -7.714938909774437
[pool-2-thread-5] INFO SocketTesting.OptimizedUDPServer - Valuation for message 5: {"ticker":"LCID","ttm_eps":-1.25,"price_tgt":2.59308,"price":2.38,"1yg":0.3083,"LTG":"NaN","Valuation":-7.714938909774437} sent by thread: pool-2-thread-5
[pool-2-thread-4] ERROR SocketTesting.OptimizedUDPServer - Error sending message 4 at currentTimeMS 1745291272053: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Message for ticker: MTH handled by thread: pool-1-thread-4
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Valuation for ticker: MTH: 64.37988691729325
[pool-2-thread-6] INFO SocketTesting.OptimizedUDPServer - Valuation for message 6: {"ticker":"MTH","ttm_eps":10.72,"price_tgt":95.84,"price":65.13,"1yg":0.1742,"LTG":"NaN","Valuation":64.37988691729325} sent by thread: pool-2-thread-6
[pool-2-thread-5] ERROR SocketTesting.OptimizedUDPServer - Error sending message 5 at currentTimeMS 1745291272317: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-6] INFO Valuation.ComputeValuationCallable - Message for ticker: MCHP handled by thread: pool-1-thread-6
[pool-1-thread-6] INFO Valuation.ComputeValuationCallable - Valuation for ticker: MCHP: 3.2593392857142853
[pool-2-thread-7] INFO SocketTesting.OptimizedUDPServer - Valuation for message 7: {"ticker":"MCHP","ttm_eps":0.57,"price_tgt":60.99696,"price":38.56,"1yg":-0.0575,"LTG":"NaN","Valuation":3.2593392857142853} sent by thread: pool-2-thread-7
[pool-2-thread-6] ERROR SocketTesting.OptimizedUDPServer - Error sending message 6 at currentTimeMS 1745291272553: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Message for ticker: PYPL handled by thread: pool-1-thread-8
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Valuation for ticker: PYPL: 23.658359975250004
[pool-2-thread-8] INFO SocketTesting.OptimizedUDPServer - Valuation for message 8: {"ticker":"PYPL","ttm_eps":3.99,"price_tgt":86.03081,"price":61.0,"1yg":0.112799995,"LTG":"NaN","Valuation":23.658359975250004} sent by thread: pool-2-thread-8
[pool-2-thread-7] ERROR SocketTesting.OptimizedUDPServer - Error sending message 7 at currentTimeMS 1745291272805: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Message for ticker: PBR handled by thread: pool-1-thread-1
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Valuation for ticker: PBR: 6.724567970356541
[pool-2-thread-9] INFO SocketTesting.OptimizedUDPServer - Valuation for message 9: {"ticker":"PBR","ttm_eps":1.16,"price_tgt":16.31321,"price":11.62,"1yg":0.0061000003,"LTG":"NaN","Valuation":6.724567970356541} sent by thread: pool-2-thread-9
[pool-2-thread-8] ERROR SocketTesting.OptimizedUDPServer - Error sending message 8 at currentTimeMS 1745291273023: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Message for ticker: PONY handled by thread: pool-1-thread-4
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Valuation for ticker: PONY: -13.906944360902255
[pool-2-thread-10] INFO SocketTesting.OptimizedUDPServer - Valuation for message 10: {"ticker":"PONY","ttm_eps":-2.4,"price_tgt":21.75,"price":4.48,"1yg":0.0041,"LTG":"NaN","Valuation":-13.906944360902255} sent by thread: pool-2-thread-10
[pool-2-thread-9] ERROR SocketTesting.OptimizedUDPServer - Error sending message 9 at currentTimeMS 1745291273242: Topic test_topic not present in metadata after 300 ms.
[pool-2-thread-10] ERROR SocketTesting.OptimizedUDPServer - Error sending message 10 at currentTimeMS 1745291273474: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Message for ticker: IOT handled by thread: pool-1-thread-5
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Valuation for ticker: IOT: -1.7414505263157896
[pool-2-thread-11] INFO SocketTesting.OptimizedUDPServer - Valuation for message 11: {"ticker":"IOT","ttm_eps":-0.28,"price_tgt":47.45222,"price":37.52,"1yg":0.3466,"LTG":"NaN","Valuation":-1.7414505263157896} sent by thread: pool-2-thread-11
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Message for ticker: SNOW handled by thread: pool-1-thread-8
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Valuation for ticker: SNOW: -24.043054812030075
[pool-2-thread-12] INFO SocketTesting.OptimizedUDPServer - Valuation for message 12: {"ticker":"SNOW","ttm_eps":-3.86,"price_tgt":197.062,"price":143.43,"1yg":0.3541,"LTG":"NaN","Valuation":-24.043054812030075} sent by thread: pool-2-thread-12
[pool-2-thread-11] ERROR SocketTesting.OptimizedUDPServer - Error sending message 11 at currentTimeMS 1745291273847: Topic test_topic not present in metadata after 300 ms.
[pool-2-thread-12] ERROR SocketTesting.OptimizedUDPServer - Error sending message 12 at currentTimeMS 1745291274051: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Message for ticker: TGT handled by thread: pool-1-thread-1
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Valuation for ticker: TGT: 52.133405789473684
[pool-2-thread-13] INFO SocketTesting.OptimizedUDPServer - Valuation for message 13: {"ticker":"TGT","ttm_eps":8.86,"price_tgt":129.18182,"price":93.11,"1yg":0.0763,"LTG":"NaN","Valuation":52.133405789473684} sent by thread: pool-2-thread-13
[kafka-producer-network-thread | producer-1] INFO org.apache.kafka.clients.NetworkClient - [Producer clientId=producer-1] Disconnecting from node -1 due to socket connection setup timeout. The timeout value is 11464 ms.
[kafka-producer-network-thread | producer-1] WARN org.apache.kafka.clients.NetworkClient - [Producer clientId=producer-1] Bootstrap broker 192.168.1.154:9092 (id: -1 rack: null) disconnected
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-3] INFO Valuation.ComputeValuationCallable - Message for ticker: WMT handled by thread: pool-1-thread-3
[pool-1-thread-3] INFO Valuation.ComputeValuationCallable - Valuation for ticker: WMT: 14.317393233082708
[pool-2-thread-14] INFO SocketTesting.OptimizedUDPServer - Valuation for message 14: {"ticker":"WMT","ttm_eps":2.41,"price_tgt":106.59366,"price":93.22,"1yg":0.122,"LTG":"NaN","Valuation":14.317393233082708} sent by thread: pool-2-thread-14
[pool-2-thread-13] ERROR SocketTesting.OptimizedUDPServer - Error sending message 13 at currentTimeMS 1745291274486: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Message for ticker: BAC handled by thread: pool-1-thread-5
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Valuation for ticker: BAC: 20.07341409774436
[pool-2-thread-15] INFO SocketTesting.OptimizedUDPServer - Valuation for message 15: {"ticker":"BAC","ttm_eps":3.35,"price_tgt":48.64286,"price":37.41,"1yg":0.1633,"LTG":"NaN","Valuation":20.07341409774436} sent by thread: pool-2-thread-15
[pool-2-thread-14] ERROR SocketTesting.OptimizedUDPServer - Error sending message 14 at currentTimeMS 1745291274674: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-7] INFO Valuation.ComputeValuationCallable - Message for ticker: AI handled by thread: pool-1-thread-7
[pool-1-thread-7] INFO Valuation.ComputeValuationCallable - Valuation for ticker: AI: -13.082605187969925
[pool-2-thread-16] INFO SocketTesting.OptimizedUDPServer - Valuation for message 16: {"ticker":"AI","ttm_eps":-2.23,"price_tgt":29.46533,"price":19.35,"1yg":0.0622,"LTG":"NaN","Valuation":-13.082605187969925} sent by thread: pool-2-thread-16
[pool-2-thread-15] ERROR SocketTesting.OptimizedUDPServer - Error sending message 15 at currentTimeMS 1745291274876: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Message for ticker: ENPH handled by thread: pool-1-thread-1
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Valuation for ticker: ENPH: 4.548758449342106
[pool-2-thread-1] INFO SocketTesting.OptimizedUDPServer - Valuation for message 17: {"ticker":"ENPH","ttm_eps":0.75,"price_tgt":72.26722,"price":52.54,"1yg":0.22209999,"LTG":"NaN","Valuation":4.548758449342106} sent by thread: pool-2-thread-1
[pool-2-thread-16] ERROR SocketTesting.OptimizedUDPServer - Error sending message 16 at currentTimeMS 1745291275066: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Message for ticker: FSLR handled by thread: pool-1-thread-4
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Valuation for ticker: FSLR: 76.38786819548872
[pool-2-thread-2] INFO SocketTesting.OptimizedUDPServer - Valuation for message 18: {"ticker":"FSLR","ttm_eps":12.02,"price_tgt":231.38147,"price":127.98,"1yg":0.4559,"LTG":"NaN","Valuation":76.38786819548872} sent by thread: pool-2-thread-2
[pool-2-thread-1] ERROR SocketTesting.OptimizedUDPServer - Error sending message 17 at currentTimeMS 1745291275316: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Message for ticker: JPM handled by thread: pool-1-thread-5
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Valuation for ticker: JPM: 119.51153789473683
[pool-2-thread-3] INFO SocketTesting.OptimizedUDPServer - Valuation for message 19: {"ticker":"JPM","ttm_eps":20.38,"price_tgt":257.75046,"price":231.96,"1yg":0.0602,"LTG":"NaN","Valuation":119.51153789473683} sent by thread: pool-2-thread-3
[pool-2-thread-2] ERROR SocketTesting.OptimizedUDPServer - Error sending message 18 at currentTimeMS 1745291275565: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-7] INFO Valuation.ComputeValuationCallable - Message for ticker: PLTR handled by thread: pool-1-thread-7
[pool-1-thread-7] INFO Valuation.ComputeValuationCallable - Valuation for ticker: PLTR: 1.1598714285714287
[pool-2-thread-4] INFO SocketTesting.OptimizedUDPServer - Valuation for message 20: {"ticker":"PLTR","ttm_eps":0.19,"price_tgt":87.04727,"price":93.78,"1yg":0.254,"LTG":"NaN","Valuation":1.1598714285714287} sent by thread: pool-2-thread-4
[pool-2-thread-3] ERROR SocketTesting.OptimizedUDPServer - Error sending message 19 at currentTimeMS 1745291275801: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Message for ticker: GOOG handled by thread: pool-1-thread-1
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Valuation for ticker: GOOG: 47.91753421052632
[pool-2-thread-5] INFO SocketTesting.OptimizedUDPServer - Valuation for message 21: {"ticker":"GOOG","ttm_eps":8.05,"price_tgt":201.7857,"price":153.36,"1yg":0.1314,"LTG":"NaN","Valuation":47.91753421052632} sent by thread: pool-2-thread-5
[pool-2-thread-4] ERROR SocketTesting.OptimizedUDPServer - Error sending message 20 at currentTimeMS 1745291275989: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Message for ticker: AAPL handled by thread: pool-1-thread-4
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Valuation for ticker: AAPL: 37.28339996092105
[pool-2-thread-6] INFO SocketTesting.OptimizedUDPServer - Valuation for message 22: {"ticker":"AAPL","ttm_eps":6.3,"price_tgt":237.3895,"price":196.98,"1yg":0.103599995,"LTG":"NaN","Valuation":37.28339996092105} sent by thread: pool-2-thread-6
[pool-2-thread-5] ERROR SocketTesting.OptimizedUDPServer - Error sending message 21 at currentTimeMS 1745291276255: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-6] INFO Valuation.ComputeValuationCallable - Message for ticker: SMCI handled by thread: pool-1-thread-6
[pool-1-thread-6] INFO Valuation.ComputeValuationCallable - Valuation for ticker: SMCI: 14.484249999999998
[pool-2-thread-7] INFO SocketTesting.OptimizedUDPServer - Valuation for message 23: {"ticker":"SMCI","ttm_eps":2.3,"price_tgt":51.765,"price":31.505,"1yg":0.4095,"LTG":"NaN","Valuation":14.484249999999998} sent by thread: pool-2-thread-7
[pool-2-thread-6] ERROR SocketTesting.OptimizedUDPServer - Error sending message 22 at currentTimeMS 1745291276442: Topic test_topic not present in metadata after 300 ms.
[pool-2-thread-7] ERROR SocketTesting.OptimizedUDPServer - Error sending message 23 at currentTimeMS 1745291276642: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-7] INFO Valuation.ComputeValuationCallable - Message for ticker: WOLF handled by thread: pool-1-thread-7
[pool-1-thread-7] INFO Valuation.ComputeValuationCallable - Valuation for ticker: WOLF: -47.91737274152632
[pool-2-thread-8] INFO SocketTesting.OptimizedUDPServer - Valuation for message 24: {"ticker":"WOLF","ttm_eps":-7.69,"price_tgt":5.7,"price":2.47,"1yg":0.35599998,"LTG":"NaN","Valuation":-47.91737274152632} sent by thread: pool-2-thread-8
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Message for ticker: KC handled by thread: pool-1-thread-1
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Valuation for ticker: KC: -7.516237969924814
[pool-2-thread-9] INFO SocketTesting.OptimizedUDPServer - Valuation for message 25: {"ticker":"KC","ttm_eps":-1.1,"price_tgt":17.4068,"price":11.035,"1yg":0.8411,"LTG":"NaN","Valuation":-7.516237969924814} sent by thread: pool-2-thread-9
[pool-2-thread-8] ERROR SocketTesting.OptimizedUDPServer - Error sending message 24 at currentTimeMS 1745291277035: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Message for ticker: EVLV handled by thread: pool-1-thread-4
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Valuation for ticker: EVLV: -0.7126627067669173
[pool-2-thread-10] INFO SocketTesting.OptimizedUDPServer - Valuation for message 26: {"ticker":"EVLV","ttm_eps":-0.11,"price_tgt":4.75,"price":3.31,"1yg":0.5556,"LTG":"NaN","Valuation":-0.7126627067669173} sent by thread: pool-2-thread-10
[pool-2-thread-9] ERROR SocketTesting.OptimizedUDPServer - Error sending message 25 at currentTimeMS 1745291277223: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-6] INFO Valuation.ComputeValuationCallable - Message for ticker: OKTA handled by thread: pool-1-thread-6
[pool-1-thread-6] INFO Valuation.ComputeValuationCallable - Valuation for ticker: OKTA: 0.35503533834586465
[pool-2-thread-11] INFO SocketTesting.OptimizedUDPServer - Valuation for message 27: {"ticker":"OKTA","ttm_eps":0.06,"price_tgt":116.98026,"price":97.93,"1yg":0.103,"LTG":"NaN","Valuation":0.35503533834586465} sent by thread: pool-2-thread-11
[pool-2-thread-10] ERROR SocketTesting.OptimizedUDPServer - Error sending message 26 at currentTimeMS 1745291277426: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-7] INFO Valuation.ComputeValuationCallable - Message for ticker: QRVO handled by thread: pool-1-thread-7
[pool-1-thread-7] INFO Valuation.ComputeValuationCallable - Valuation for ticker: QRVO: 1.6387336842105265
[pool-2-thread-12] INFO SocketTesting.OptimizedUDPServer - Valuation for message 28: {"ticker":"QRVO","ttm_eps":0.28,"price_tgt":88.678,"price":57.63,"1yg":0.0509,"LTG":"NaN","Valuation":1.6387336842105265} sent by thread: pool-2-thread-12
[pool-2-thread-11] ERROR SocketTesting.OptimizedUDPServer - Error sending message 27 at currentTimeMS 1745291277661: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Message for ticker: JNPR handled by thread: pool-1-thread-1
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Valuation for ticker: JNPR: 5.059072862477443
[pool-2-thread-13] INFO SocketTesting.OptimizedUDPServer - Valuation for message 29: {"ticker":"JNPR","ttm_eps":0.86,"price_tgt":39.88889,"price":34.33,"1yg":0.075100005,"LTG":"NaN","Valuation":5.059072862477443} sent by thread: pool-2-thread-13
[pool-2-thread-12] ERROR SocketTesting.OptimizedUDPServer - Error sending message 28 at currentTimeMS 1745291277850: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Message for ticker: UBER handled by thread: pool-1-thread-4
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Valuation for ticker: UBER: 28.17917142857143
[pool-2-thread-14] INFO SocketTesting.OptimizedUDPServer - Valuation for message 30: {"ticker":"UBER","ttm_eps":4.56,"price_tgt":88.48354,"price":75.24,"1yg":0.3145,"LTG":"NaN","Valuation":28.17917142857143} sent by thread: pool-2-thread-14
[pool-2-thread-13] ERROR SocketTesting.OptimizedUDPServer - Error sending message 29 at currentTimeMS 1745291278055: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Message for ticker: DKNG handled by thread: pool-1-thread-5
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Valuation for ticker: DKNG: -7.051882894736843
[pool-2-thread-15] INFO SocketTesting.OptimizedUDPServer - Valuation for message 31: {"ticker":"DKNG","ttm_eps":-1.05,"price_tgt":56.38125,"price":33.61,"1yg":0.7469,"LTG":"NaN","Valuation":-7.051882894736843} sent by thread: pool-2-thread-15
[pool-2-thread-14] ERROR SocketTesting.OptimizedUDPServer - Error sending message 30 at currentTimeMS 1745291278307: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-7] INFO Valuation.ComputeValuationCallable - Message for ticker: RBRK handled by thread: pool-1-thread-7
[pool-1-thread-7] INFO Valuation.ComputeValuationCallable - Valuation for ticker: RBRK: -47.584132481203014
[pool-2-thread-16] INFO SocketTesting.OptimizedUDPServer - Valuation for message 32: {"ticker":"RBRK","ttm_eps":-7.48,"price_tgt":79.9225,"price":61.61,"1yg":0.4611,"LTG":"NaN","Valuation":-47.584132481203014} sent by thread: pool-2-thread-16
[pool-2-thread-15] ERROR SocketTesting.OptimizedUDPServer - Error sending message 31 at currentTimeMS 1745291278554: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-2] INFO Valuation.ComputeValuationCallable - Message for ticker: ORCL handled by thread: pool-1-thread-2
[pool-1-thread-2] INFO Valuation.ComputeValuationCallable - Valuation for ticker: ORCL: 25.29048293233083
[pool-2-thread-1] INFO SocketTesting.OptimizedUDPServer - Valuation for message 33: {"ticker":"ORCL","ttm_eps":4.26,"price_tgt":180.4706,"price":128.62,"1yg":0.1187,"LTG":"NaN","Valuation":25.29048293233083} sent by thread: pool-2-thread-1
[pool-2-thread-16] ERROR SocketTesting.OptimizedUDPServer - Error sending message 32 at currentTimeMS 1745291278838: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Message for ticker: MRVL handled by thread: pool-1-thread-4
[pool-1-thread-4] INFO Valuation.ComputeValuationCallable - Valuation for ticker: MRVL: -6.291846992481203
[pool-2-thread-2] INFO SocketTesting.OptimizedUDPServer - Valuation for message 34: {"ticker":"MRVL","ttm_eps":-1.02,"price_tgt":106.04056,"price":51.7,"1yg":0.3055,"LTG":"NaN","Valuation":-6.291846992481203} sent by thread: pool-2-thread-2
[pool-2-thread-1] ERROR SocketTesting.OptimizedUDPServer - Error sending message 33 at currentTimeMS 1745291279057: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-6] INFO Valuation.ComputeValuationCallable - Message for ticker: NKE handled by thread: pool-1-thread-6
[pool-1-thread-6] INFO Valuation.ComputeValuationCallable - Valuation for ticker: NKE: 17.353498684210525
[pool-2-thread-3] INFO SocketTesting.OptimizedUDPServer - Valuation for message 35: {"ticker":"NKE","ttm_eps":3.01,"price_tgt":76.61167,"price":55.76,"1yg":-0.0195,"LTG":"NaN","Valuation":17.353498684210525} sent by thread: pool-2-thread-3
[pool-2-thread-2] ERROR SocketTesting.OptimizedUDPServer - Error sending message 34 at currentTimeMS 1745291279276: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Message for ticker: SNAP handled by thread: pool-1-thread-8
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Valuation for ticker: SNAP: -2.6661568421052633
[pool-2-thread-4] INFO SocketTesting.OptimizedUDPServer - Valuation for message 36: {"ticker":"SNAP","ttm_eps":-0.42,"price_tgt":11.74917,"price":7.88,"1yg":0.4502,"LTG":"NaN","Valuation":-2.6661568421052633} sent by thread: pool-2-thread-4
[pool-2-thread-3] ERROR SocketTesting.OptimizedUDPServer - Error sending message 35 at currentTimeMS 1745291279481: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-2] INFO Valuation.ComputeValuationCallable - Message for ticker: OKLO handled by thread: pool-1-thread-2
[pool-1-thread-2] INFO Valuation.ComputeValuationCallable - Valuation for ticker: OKLO: -4.1993831578947365
[pool-2-thread-5] INFO SocketTesting.OptimizedUDPServer - Valuation for message 37: {"ticker":"OKLO","ttm_eps":-0.74,"price_tgt":45.46333,"price":21.98,"1yg":-0.0924,"LTG":"NaN","Valuation":-4.1993831578947365} sent by thread: pool-2-thread-5
[pool-2-thread-4] ERROR SocketTesting.OptimizedUDPServer - Error sending message 36 at currentTimeMS 1745291279700: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-3] INFO Valuation.ComputeValuationCallable - Message for ticker: ICE handled by thread: pool-1-thread-3
[pool-1-thread-3] INFO Valuation.ComputeValuationCallable - Valuation for ticker: ICE: 28.289220249234585
[pool-2-thread-6] INFO SocketTesting.OptimizedUDPServer - Valuation for message 38: {"ticker":"ICE","ttm_eps":4.77,"price_tgt":187.375,"price":158.64,"1yg":0.113800004,"LTG":"NaN","Valuation":28.289220249234585} sent by thread: pool-2-thread-6
[pool-2-thread-5] ERROR SocketTesting.OptimizedUDPServer - Error sending message 37 at currentTimeMS 1745291279920: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Message for ticker: CME handled by thread: pool-1-thread-5
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Valuation for ticker: CME: 56.505153133926314
[pool-2-thread-7] INFO SocketTesting.OptimizedUDPServer - Valuation for message 39: {"ticker":"CME","ttm_eps":9.66,"price_tgt":266.9412,"price":262.53,"1yg":0.048299998,"LTG":"NaN","Valuation":56.505153133926314} sent by thread: pool-2-thread-7
[pool-2-thread-6] ERROR SocketTesting.OptimizedUDPServer - Error sending message 38 at currentTimeMS 1745291280124: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Message for ticker: CBOE handled by thread: pool-1-thread-8
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Valuation for ticker: CBOE: 42.24248120300752
[pool-2-thread-8] INFO SocketTesting.OptimizedUDPServer - Valuation for message 40: {"ticker":"CBOE","ttm_eps":7.2,"price_tgt":220.33333,"price":217.07,"1yg":0.0625,"LTG":"NaN","Valuation":42.24248120300752} sent by thread: pool-2-thread-8
[pool-2-thread-7] ERROR SocketTesting.OptimizedUDPServer - Error sending message 39 at currentTimeMS 1745291280328: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-2] INFO Valuation.ComputeValuationCallable - Message for ticker: NDAQ handled by thread: pool-1-thread-2
[pool-1-thread-2] INFO Valuation.ComputeValuationCallable - Valuation for ticker: NDAQ: 11.461965263157895
[pool-2-thread-9] INFO SocketTesting.OptimizedUDPServer - Valuation for message 41: {"ticker":"NDAQ","ttm_eps":1.93,"price_tgt":83.05556,"price":72.18,"1yg":0.1204,"LTG":"NaN","Valuation":11.461965263157895} sent by thread: pool-2-thread-9
[pool-2-thread-8] ERROR SocketTesting.OptimizedUDPServer - Error sending message 40 at currentTimeMS 1745291280534: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-3] INFO Valuation.ComputeValuationCallable - Message for ticker: APLD handled by thread: pool-1-thread-3
[pool-1-thread-3] INFO Valuation.ComputeValuationCallable - Valuation for ticker: APLD: -7.948466842105264
[pool-2-thread-10] INFO SocketTesting.OptimizedUDPServer - Valuation for message 42: {"ticker":"APLD","ttm_eps":-1.47,"price_tgt":10.05556,"price":3.95,"1yg":-0.3082,"LTG":"NaN","Valuation":-7.948466842105264} sent by thread: pool-2-thread-10
[pool-2-thread-9] ERROR SocketTesting.OptimizedUDPServer - Error sending message 41 at currentTimeMS 1745291280722: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Message for ticker: CEG handled by thread: pool-1-thread-5
[pool-1-thread-5] INFO Valuation.ComputeValuationCallable - Valuation for ticker: CEG: 70.46648796992483
[pool-2-thread-11] INFO SocketTesting.OptimizedUDPServer - Valuation for message 43: {"ticker":"CEG","ttm_eps":11.88,"price_tgt":291.75858,"price":206.68,"1yg":0.1145,"LTG":"NaN","Valuation":70.46648796992483} sent by thread: pool-2-thread-11
[pool-2-thread-10] ERROR SocketTesting.OptimizedUDPServer - Error sending message 42 at currentTimeMS 1745291280957: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Message for ticker: TLN handled by thread: pool-1-thread-8
[pool-1-thread-8] INFO Valuation.ComputeValuationCallable - Valuation for ticker: TLN: 126.01558563909774
[pool-2-thread-12] INFO SocketTesting.OptimizedUDPServer - Valuation for message 44: {"ticker":"TLN","ttm_eps":17.66,"price_tgt":259.44077,"price":203.46,"1yg":1.0851,"LTG":"NaN","Valuation":126.01558563909774} sent by thread: pool-2-thread-12
[pool-2-thread-11] ERROR SocketTesting.OptimizedUDPServer - Error sending message 43 at currentTimeMS 1745291281191: Topic test_topic not present in metadata after 300 ms.
[main] INFO SocketTesting.OptimizedUDPServer - Received message from /127.0.0.1:63939
[main] INFO SocketTesting.OptimizedUDPServer - Message getting processed asynchronously for /127.0.0.1:63939
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Message for ticker: VST handled by thread: pool-1-thread-1
[pool-1-thread-1] INFO Valuation.ComputeValuationCallable - Valuation for ticker: VST: 42.43597368421053
[pool-2-thread-13] INFO SocketTesting.OptimizedUDPServer - Valuation for message 45: {"ticker":"VST","ttm_eps":7.0,"price_tgt":167.6661,"price":115.42,"1yg":0.2199,"LTG":"NaN","Valuation":42.43597368421053} sent by thread: pool-2-thread-13
[pool-2-thread-12] ERROR SocketTesting.OptimizedUDPServer - Error sending message 44 at currentTimeMS 1745291281427: Topic test_topic not present in metadata after 300 ms.
[pool-2-thread-13] ERROR SocketTesting.OptimizedUDPServer - Error sending message 45 at currentTimeMS 1745291281677: Topic test_topic not present in metadata after 300 ms.
```
</details>



# Redesign

I'm attempting to make this application more accessible by setting up an API server on the custom host. I want to be able to hit this endpoint from my phone via postman or some other application. I want the endpoint to trigger an asynchronous job that computes the valuations and outputs them to Kafka. I want to visualize the kafka messages via Grafana or some other built in dashboard. Incorporating the phone will make this more usable and helpful to me in my investing process.


## Speedup of asynchronous vs synchronous valuation process
Even for a small list of just 6 stocks, asynchronous computation resulted in a (2.47s/1.26s) = ~2x speedup.

<details>
<summary>Logs for Async and Sync Valuation Computations</summary>

```
INFO:     Started server process [1]

INFO:     Waiting for application startup.

INFO:     Application startup complete.

INFO:     Uvicorn running on http://0.0.0.0:8000⁠ (Press CTRL+C to quit)

INFO:     XXX.XX.X.X:34208 - "POST /compute_valuations HTTP/1.1" 200 OK

2025-07-01 15:00:44,396 INFO [AnyIO worker thread] main: Valuation inputs for GOOGL - EPS: 8.95, 1Y Growth Rate: 6.23, 1Y Sales Growth Rate: 10.5900005, Bond Yield: 5.54

2025-07-01 15:00:44,396 INFO [AnyIO worker thread] main: Ticker: GOOGL, Valuation (Growth Rate): 116.19

2025-07-01 15:00:44,396 INFO [AnyIO worker thread] main: Ticker: GOOGL, Valuation (Sales Growth Rate): 162.67

2025-07-01 15:00:44,770 INFO [AnyIO worker thread] main: Valuation inputs for FSLR - EPS: 11.77, 1Y Growth Rate: 56.86, 1Y Sales Growth Rate: 20.799999, Bond Yield: 5.54

2025-07-01 15:00:44,770 INFO [AnyIO worker thread] main: Ticker: FSLR, Valuation (Growth Rate): 862.73

2025-07-01 15:00:44,770 INFO [AnyIO worker thread] main: Ticker: FSLR, Valuation (Sales Growth Rate): 357.09

2025-07-01 15:00:45,146 INFO [AnyIO worker thread] main: Valuation inputs for META - EPS: 25.61, 1Y Growth Rate: 11.690000000000001, 1Y Sales Growth Rate: 13.68, Bond Yield: 5.54

2025-07-01 15:00:45,146 INFO [AnyIO worker thread] main: Ticker: META, Valuation (Growth Rate): 499.04

2025-07-01 15:00:45,147 INFO [AnyIO worker thread] main: Ticker: META, Valuation (Sales Growth Rate): 559.76

2025-07-01 15:00:45,486 INFO [AnyIO worker thread] main: Valuation inputs for AAPL - EPS: 6.42, 1Y Growth Rate: 9.2, 1Y Sales Growth Rate: 5.79, Bond Yield: 5.54

2025-07-01 15:00:45,486 INFO [AnyIO worker thread] main: Ticker: AAPL, Valuation (Growth Rate): 106.06

2025-07-01 15:00:45,487 INFO [AnyIO worker thread] main: Ticker: AAPL, Valuation (Sales Growth Rate): 79.98

2025-07-01 15:00:45,855 INFO [AnyIO worker thread] main: Valuation inputs for NVDA - EPS: 3.1, 1Y Growth Rate: 34.4, 1Y Sales Growth Rate: 25.530002000000003, Bond Yield: 5.54

2025-07-01 15:00:45,855 INFO [AnyIO worker thread] main: Ticker: NVDA, Valuation (Growth Rate): 144.28

2025-07-01 15:00:45,856 INFO [AnyIO worker thread] main: Ticker: NVDA, Valuation (Sales Growth Rate): 111.52

2025-07-01 15:00:46,202 INFO [AnyIO worker thread] main: Valuation inputs for AMD - EPS: 1.38, 1Y Growth Rate: 47.449999999999996, 1Y Sales Growth Rate: 17.84, Bond Yield: 5.54

2025-07-01 15:00:46,202 INFO [AnyIO worker thread] main: Ticker: AMD, Valuation (Growth Rate): 85.68

2025-07-01 15:00:46,203 INFO [AnyIO worker thread] main: Ticker: AMD, Valuation (Sales Growth Rate): 37.00

2025-07-01 15:00:46,203 INFO [AnyIO worker thread] main: Sequential processing completed in 2.47 seconds.

INFO:     XXX.XX.X.X:34638 - "POST /compute_valuations_async HTTP/1.1" 200 OK

2025-07-01 15:00:56,246 INFO [ThreadPoolExecutor-0_4] main: Valuation inputs for NVDA - EPS: 3.1, 1Y Growth Rate: 34.4, 1Y Sales Growth Rate: 25.530002000000003, Bond Yield: 5.54

2025-07-01 15:00:56,246 INFO [ThreadPoolExecutor-0_4] main: Ticker: NVDA, Valuation (Growth Rate): 144.28

2025-07-01 15:00:56,246 INFO [ThreadPoolExecutor-0_4] main: Ticker: NVDA, Valuation (Sales Growth Rate): 111.52

2025-07-01 15:00:56,280 INFO [ThreadPoolExecutor-0_0] main: Valuation inputs for GOOGL - EPS: 8.95, 1Y Growth Rate: 6.23, 1Y Sales Growth Rate: 10.5900005, Bond Yield: 5.54

2025-07-01 15:00:56,280 INFO [ThreadPoolExecutor-0_0] main: Ticker: GOOGL, Valuation (Growth Rate): 116.19

2025-07-01 15:00:56,280 INFO [ThreadPoolExecutor-0_0] main: Ticker: GOOGL, Valuation (Sales Growth Rate): 162.67

2025-07-01 15:00:56,291 INFO [ThreadPoolExecutor-0_5] main: Valuation inputs for AMD - EPS: 1.38, 1Y Growth Rate: 47.449999999999996, 1Y Sales Growth Rate: 17.84, Bond Yield: 5.54

2025-07-01 15:00:56,291 INFO [ThreadPoolExecutor-0_5] main: Ticker: AMD, Valuation (Growth Rate): 85.68

2025-07-01 15:00:56,291 INFO [ThreadPoolExecutor-0_5] main: Ticker: AMD, Valuation (Sales Growth Rate): 37.00

2025-07-01 15:00:56,304 INFO [ThreadPoolExecutor-0_3] main: Valuation inputs for AAPL - EPS: 6.42, 1Y Growth Rate: 9.2, 1Y Sales Growth Rate: 5.79, Bond Yield: 5.54

2025-07-01 15:00:56,304 INFO [ThreadPoolExecutor-0_3] main: Ticker: AAPL, Valuation (Growth Rate): 106.06

2025-07-01 15:00:56,304 INFO [ThreadPoolExecutor-0_3] main: Ticker: AAPL, Valuation (Sales Growth Rate): 79.98

2025-07-01 15:00:56,328 INFO [ThreadPoolExecutor-0_2] main: Valuation inputs for META - EPS: 25.61, 1Y Growth Rate: 11.690000000000001, 1Y Sales Growth Rate: 13.68, Bond Yield: 5.54

2025-07-01 15:00:56,328 INFO [ThreadPoolExecutor-0_2] main: Ticker: META, Valuation (Growth Rate): 499.04

2025-07-01 15:00:56,328 INFO [ThreadPoolExecutor-0_2] main: Ticker: META, Valuation (Sales Growth Rate): 559.76

2025-07-01 15:00:57,180 INFO [ThreadPoolExecutor-0_1] main: Valuation inputs for FSLR - EPS: 11.77, 1Y Growth Rate: 56.86, 1Y Sales Growth Rate: 20.799999, Bond Yield: 5.54

2025-07-01 15:00:57,181 INFO [ThreadPoolExecutor-0_1] main: Ticker: FSLR, Valuation (Growth Rate): 862.73

2025-07-01 15:00:57,181 INFO [ThreadPoolExecutor-0_1] main: Ticker: FSLR, Valuation (Sales Growth Rate): 357.09

2025-07-01 15:00:57,203 INFO [AnyIO worker thread] main: Async processing completed in 1.26 seconds.

```

</details>
## Sample output of Kafka message with valuations for FirstSolar. 

![Alt text](Images/KafkaValuationMessage.PNG)