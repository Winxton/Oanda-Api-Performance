import time

def run(client, num_trials=15, num_instruments=10):
    account_id = 3922748
    #time1 = time.time()

    instruments = client.get_instruments(account_id)
    symbol_list = []

    for instrument in instruments.get("instruments"):
      symbol_list.append(instrument.get("instrument"))

    symbol_list = ','.join(symbol_list[:num_instruments])

    for i in range(0, num_trials):
      singletime1 = time.time()
      response = client.get_prices(
        instruments=symbol_list
      )
      #print len(response.get("trades"))
      print '%0.3f' % ((time.time()-singletime1)*1000.0)
      #time.sleep(1)
      #time2 = time.time()
      #print 'GET TRADES AVERAGE TIME: %0.3f ms' % ((time2-time1)*1000.0/ num_trials)