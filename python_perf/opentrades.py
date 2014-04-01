import time

def run(client, num_trials=15):
    account_id = 3922748

    time1 = time.time()
    totaltime = 0

    for i in range(0,num_trials):
        singletime1 = time.time()
        response = client.create_order(account_id, 
                                  instrument="EUR_USD", 
                                  side="buy", 
                                  units=10, 
                                  type="market")
        print '%0.3f' % ((time.time()-singletime1)*1000.0)
        totaltime += time.time()-singletime1

    print 'ORDER AVERAGE TIME: %0.3f ms' % ((time.time()-time1)*1000.0/num_trials)
    print 'AVERAGE FROM SUM: %0.3f ms' % (totaltime*1000.0/num_trials)