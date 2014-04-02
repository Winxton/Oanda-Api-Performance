import time

def run(client, num_trials=15):
    account_id = 3922748
    #time1 = time.time()

    trade_ids = []

    print ("OPEN TRADES")

    for i in range(0, num_trials):
        singletime = time.time()
        response = client.create_order(account_id, 
                          instrument="EUR_USD", 
                          side="buy", 
                          units=10, 
                          type="market")
        trade_id = response.get("tradeOpened").get("id")
        trade_ids.append(trade_id)
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