import oandapy

import pytz
from time import time
from datetime import datetime
from time import mktime
import rfc3339

f = open('result.txt', 'w+')

class MyStreamer(oandapy.Streamer):
    def __init__(self, *args, **kwargs):
        oandapy.Streamer.__init__(self, *args, **kwargs)
        self.ticks = 0

    def on_success(self, data):
        now = datetime.now(pytz.utc)

        #print ("-------------------")
        #print (data)
        
        if data.has_key("heartbeat"):
            tick_time = data.get("heartbeat").get("time")
        else:
            tick_time = data.get("time")

        tick_time = rfc3339.parse_datetime(tick_time)

        #print ( tick_time )
        #print ( now )
        
        diff = now - tick_time
        print ( "%.2f\n" % (diff.total_seconds()*1000) )
        f.write ( "%.2f\n" % (diff.total_seconds()*1000) )
        
        #diff = now - tick_time
        #print diff

        self.ticks += 1
        if self.ticks == 100:
            self.disconnect()

    def on_error(self, data):
        print (data)
        self.disconnect()
        f.close()

stream = MyStreamer(environment="practice", access_token="b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22")
stream.start(accountId=3922748, instruments="EUR_USD")