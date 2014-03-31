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

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

public class JavaPerformance {

    public static void main (String[]args) throws IOException, InterruptedException {

        DefaultHttpClient httpClient = new DefaultHttpClient();

        final int TIMES = 15;

        try {
            JSONObject obj = null;

            int[] times = new int[TIMES];

            for (int i =0; i<TIMES; i++) {
                obj = UrlConnectionRequest.getTrades(10);
                //System.out.println(obj.toString());
            }

            /*
            ArrayList<Integer> tradeIds = new ArrayList<Integer>();
            //CREATE TRADES
            System.out.println("Create Trades");
            for (int i =0; i<TIMES; i++) {
                JSONObject response = ApacheHttpRequest.createTrade(httpClient);
                int id = Integer.parseInt(((JSONObject)response.get("tradeOpened")).get("id").toString());
                tradeIds.add(id);
            }
            //CLOSE TRADES
            System.out.println("\nClose Trades");
            for (int tradeId : tradeIds) {
                ApacheHttpRequest.closeTrade(httpClient, tradeId);
            }
            */

            //GET TRADES
            System.out.println("\n10 trades:");
            for (int i =0; i<TIMES; i++) {
                ApacheHttpRequest.getTrades(httpClient, 10);
            }

            /*
            System.out.println("\n50 trades:");
            for (int i =0; i<TIMES; i++) {
                ApacheHttpRequest.getTrades(httpClient, 50);
            }
            System.out.println("\n100 trades:");
            for (int i =0; i<TIMES; i++) {
                ApacheHttpRequest.getTrades(httpClient, 100);
            }
            System.out.println("\n500 trades:");
            for (int i =0; i<TIMES; i++) {
                ApacheHttpRequest.getTrades(httpClient, 500);
            }
            */

        } finally {
            httpClient.getConnectionManager().shutdown();
        }
    }
}