oanda-omp-latency-test
======================

OMP latency test client

## Setup

Clone this repo to the location of your choice

Choose a proper client to run (fxpractise/fxtrade); Edit username and password (your Java API username/password)

Compile performance.java with oanda_fxtrade_implementation-2.5.4.jar:

	javac -cp '.:oanda_fxtrade_implementation-2.5.4.jar' performance.java

Start a new script, call it "performance_log.txt" (This is a must!):

	script performance_log.txt

Run the Java test client:

	java -cp '.:oanda_fxtrade_implementation-2.5.4.jar' performance

Exit the script:

	exit

Now you need to process the log file:

	python log_processor.py

Then you should get test results in a file named OMP_Performance_Report.csv
