import time

def run(client, num_trials=15, trades=10):
    account_id = 3922748
    #time1 = time.time()

    for i in range(0, num_trials):
      singletime1 = time.time()
      response = client.get_trades(account_id, count=trades)
      #print len(response.get("trades"))
      print '%0.3f' % ((time.time()-singletime1)*1000.0)
      #time.sleep(1)
      #time2 = time.time()
      #print 'GET TRADES AVERAGE TIME: %0.3f ms' % ((time2-time1)*1000.0/ num_trials)