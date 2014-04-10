import gettrades
import opentrades
import closetrades
import get_prices

import sys
import time
import oandapy

if len(sys.argv) == 4:

    trials = int(sys.argv[1])
    keep_alive = True if int(sys.argv[2]) == 1 else False
    compress = True if int(sys.argv[3]) == 1 else False

    print ("keep alive " + str(keep_alive))
    print ("compress " + str(compress))

    token = "b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22"
    oanda = oandapy.API(environment="practice", access_token=token, keep_alive=keep_alive, compress=compress)

    # OPEN AND CLOSE TRADES

    print ("\nquote: 10 instruments")
    get_prices.run(oanda, trials, 10)

    print ("\nquote: 50 instruments")
    get_prices.run(oanda, trials, 50)

    print ("\nquote: 120 instruments")
    get_prices.run(oanda, trials, 120)

    """
    print "\nopen and close trades"
    closetrades.run(oanda, trials)
    
    print ("\n10 trades")
    gettrades.run(oanda, trials, trades=10)

    print ("\n50 trades")
    gettrades.run(oanda, trials, trades=50)

    print ("\n100 trades")
    gettrades.run(oanda, trials, trades=100)

    print ("\n500 trades")
    gettrades.run(oanda, trials, trades=500)
    """ 
else:
    print "Enter [number of trials] [keep-alive] [compress]"
