import time
import pytz
from datetime import datetime
import rfc3339

def run(client, num_trials=15):
    account_id = 3922748
    #time1 = time.time()

    trade_ids = []

    print ("OPEN TRADES")

    for i in range(0, num_trials):
        singletime = time.time()
        now = datetime.now(pytz.utc)
        response = client.create_order(account_id, 
                          instrument="EUR_USD", 
                          side="buy", 
                          units=10, 
                          type="market")
        trade_id = response.get("tradeOpened").get("id")
        trade_ids.append(trade_id)

        trade_time = response.get("time")
        trade_time = rfc3339.parse_datetime(trade_time)

        diff = trade_time - now
        print diff.total_seconds()
        
        diff_timestamp = diff.total_seconds()*1000
        print 'Request to Order: %0.3f' % (diff_timestamp)

        print '%0.3f' % ((time.time()-singletime)*1000.0)
        
        #print response

    print ("\nCLOSE TRADES")

    for i in range(0, num_trials):
        singletime = time.time()
        trade_id = trade_ids[i]
        response = client.close_trade(account_id, trade_id)
        print '%0.3f' % ((time.time()-singletime)*1000.0)


    #time2 = time.time()
    #print 'GET TRADES AVERAGE TIME: %0.3f ms' % ((time2-time1)*1000.0/ num_trials)
