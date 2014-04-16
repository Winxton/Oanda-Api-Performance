import sys
import time
import csv

omp_open_trade_latency = []
omp_close_trade_latency = []


def latency(begin, end):
    decimal = begin.find('.')
    begin = float(begin[decimal - 2:decimal + 4])
    decimal = end.find('.')
    end = float(end[decimal - 2:decimal + 4])
    diff = end - begin
    if 0 < diff:
        return int(diff * 1000)
    else:
        return int(diff * 1000) + 1000

def generate_open_trade_report(omp_latency):
    with open('OMP_Performance_Report.csv', 'a') as csvfile:
        reportwriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        reportwriter.writerow(["OMP Performance Test"])
        reportwriter.writerow(["TEST 1: Open Trade"])
        SumOfLatency = 0
        for element in omp_latency:
            reportwriter.writerow([element])
            SumOfLatency += element
        reportwriter.writerow(["Average Open Trade", 1.0*SumOfLatency/len(omp_latency)])

def generate_close_trade_report(omp_latency):
    with open('OMP_Performance_Report.csv', 'a') as csvfile:
        reportwriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        reportwriter.writerow([])
        reportwriter.writerow(["TEST 2: Close Trade"])
        SumOfLatency = 0
        for element in omp_latency:
            reportwriter.writerow([element])
            SumOfLatency += element
        reportwriter.writerow(["Average Open Trade", 1.0*SumOfLatency/len(omp_latency)])

def main():
    open('OMP_Performance_Report.csv', 'w').close()
    with open('performance_log.txt', 'r') as report:
        for line in report:
            if '/fxtrade/fxe/MarketOrderRequest' in line:
                open_trade_request = line
                while True:
                    try:
                        line = next(report)
                        if '/fxtrade/fxe/FXEResponse' in line:
                            open_trade_response = line
                            omp_open_trade_latency.append(latency(open_trade_request.split()[1], open_trade_response.split()[1]))
                            break
                    except Exception as e:
                        break
            if '/fxtrade/fxe/CloseTradeRequest' in line:
                close_trade_request = line
                while True:
                    try:
                        line = next(report)
                        if '/fxtrade/fxe/FXEResponse' in line:
                            close_trade_response = line
                            omp_close_trade_latency.append(latency(close_trade_request.split()[1], close_trade_response.split()[1]))
                            break
                    except Exception as e:
                        break
    generate_open_trade_report(omp_open_trade_latency)
    generate_close_trade_report(omp_close_trade_latency)
    sys.exit("Work Complete")

if __name__ == '__main__':
    main()