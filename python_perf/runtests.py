import gettrades
import opentrades
import closetrades

import time
import oandapy

token = "b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22"
oanda = oandapy.API(environment="practice", access_token=token)

gettrades.run(oanda, 1, trades=1)

print ("waiting...")
time.sleep(1)

# OPEN AND CLOSE TRADES
closetrades.run(oanda, 30);

"""
print "--start--"
time.sleep(1)
trials = 70

print ("\n10 trades")
gettrades.run(oanda, trials, trades=10)

print ("\n100 trades")
gettrades.run(oanda, trials, trades=100)

print ("\n50 trades")
gettrades.run(oanda, trials, trades=50)

print ("\n500 trades")
gettrades.run(oanda, trials, trades=500)
"""