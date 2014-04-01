import java.io.IOException;
import java.io.InputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.TimeUnit;

import org.apache.http.*;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.*;
import org.apache.http.conn.ConnectionKeepAliveStrategy;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultConnectionKeepAliveStrategy;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicHeader;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.params.HttpParams;
import org.apache.http.protocol.HTTP;
import org.apache.http.util.EntityUtils;

/*
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;
*/

/*
import net.minidev.json.JSONObject;
import net.minidev.json.JSONValue;
*/

import com.alibaba.fastjson.JSONObject;

public class JavaPerformance {

    public static void main (String[]args) throws Exception {

        DefaultHttpClient httpClient = new DefaultHttpClient();

        try {
            int TIMES = 5;

            if (args.length == 1) {
                TIMES = Integer.parseInt(args[0]);
            } else {
                System.out.println("Enter Number of trails");
            }

            JSONObject obj = null;

            ArrayList<Integer> tradeIds = new ArrayList<Integer>();

            //CREATE TRADES
            System.out.println("Create Trades");
            for (int i =0; i<TIMES; i++) {
                JSONObject response = UrlConnectionRequest.makeOrder();
                int id = Integer.parseInt(((JSONObject)response.get("tradeOpened")).get("id").toString());
                tradeIds.add(id);
            }
            //CLOSE TRADES
            System.out.println("\nClose Trades");
            for (int tradeId : tradeIds) {
                UrlConnectionRequest.closeTrade(tradeId);
            }
            //GET TRADES
            System.out.println("\nGet 10 trades:");
            for (int i =0; i<TIMES; i++) {
                UrlConnectionRequest.getTrades(10);
                //System.out.println(obj);
            }
            System.out.println("\nGet 50 trades:");
            for (int i =0; i<TIMES; i++) {
                UrlConnectionRequest.getTrades(50);
            }
            System.out.println("\nGet 100 trades:");
            for (int i =0; i<TIMES; i++) {
                UrlConnectionRequest.getTrades(100);
            }

            System.out.println("\nGet 500 trades:");
            for (int i =0; i<TIMES; i++) {
                UrlConnectionRequest.getTrades(500);
            }


        } finally {
            httpClient.getConnectionManager().shutdown();
        }
    }
}
