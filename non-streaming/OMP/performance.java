import java.util.Vector;
import java.io.*;

import com.oanda.fxtrade.api.*;
import com.oanda.fxtrade.api.API;
import com.oanda.fxtrade.api.FXClient;
import com.oanda.fxtrade.api.FXEventInfo;
import com.oanda.fxtrade.api.FXEventManager;
import com.oanda.fxtrade.api.FXRateEvent;
import com.oanda.fxtrade.api.FXRateEventInfo;
import com.oanda.fxtrade.api.SessionException;
import com.oanda.fxtrade.api.Instrument;

public class performance extends Thread {
    private FXClient fxclient = null;
    private String username = "";
    private String password = "";
    private Account accountSetup(String mode){
        if(mode == "trade"){
            fxclient  = API.createFXTrade();
            username = "devOC11";
            password = "oanda123";
        }
        else if (mode == "game"){
            fxclient  = API.createFXGame();
            username = "winxton";
            password = "sync31415";
        }

        try {
            fxclient.setWithKeepAliveThread(true);
            fxclient.setWithRateThread(true);
            fxclient.login(username, password, "Example1 Test");
        }
        catch (OAException oe){
            System.out.println("Example: caught: " + oe);
        }

        Account account = null;
        try {
            User me = fxclient.getUser();
            Vector<?> accounts = me.getAccounts();
            account = (Account)accounts.firstElement();
        }
        catch (SessionException se){
            System.out.println("Example: caught: " + se);
        }
        return account;
    }
    private MarketOrder mktorderSetup(){
        MarketOrder mktorder = API.createMarketOrder();
        mktorder.setUnits(1);
        mktorder.setPair(API.createFXPair("EUR/USD"));
        return mktorder;
    }
    private void cleanup(Account account){
        Vector<?> trades = new Vector<Object>();
        long startTime, endTime;
        try{
            trades = account.getTrades();
            startTime = System.nanoTime();
            account.closeAllMarketOrders();
            endTime = System.nanoTime();
        }
        catch (OAException oe){
            System.out.println("Example: caught: " + oe);
        }
    }
    private void makeTrade(int count, Account account, MarketOrder order){
        long startTime, endTime;
        long sum = 0;
        for (int i = 0; i < count; i++){
            try {
                startTime = System.nanoTime();
                account.execute(order);
                endTime = System.nanoTime();
                sum += endTime - startTime;
                account.close(order);
            }
            catch (OAException oe){
                System.out.println("Example: caught: " + oe);
            }
        }
    }
    public static void main(String[] args) throws Exception {
        performance test = new performance();

        //SET UP ENVIRONMENT
        Account myaccount = test.accountSetup("game");
        MarketOrder mktorder = test.mktorderSetup();
        myaccount.closeAllMarketOrders();

        if (myaccount != null){
            //TEST1: MAKE 50 TRADES
            test.makeTrade(50, myaccount, mktorder);

            //TEST2: CLOSE 50 TRADES
            test.cleanup(myaccount);
        }
        System.exit(0);
    }
}