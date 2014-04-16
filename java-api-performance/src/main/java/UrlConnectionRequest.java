import com.alibaba.fastjson.JSONArray;
import net.minidev.json.JSONAware;
import org.apache.http.protocol.HTTP;
import org.apache.http.util.EntityUtils;

/*
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;
*/

/*
import net.minidev.json.JSONObject;
import net.minidev.json.JSONValue;
*/

import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.JSON;

import org.apache.commons.io.IOUtils;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.List;
import java.util.Map;
import java.util.zip.GZIPInputStream;
import java.util.zip.ZipException;

/**
 * Created by wwu on 28/03/14.
 */
public class UrlConnectionRequest {
    public boolean keepAlive;
    public boolean compress;
    private String token;

    public UrlConnectionRequest(String token, boolean keepAlive, boolean compress) {
        this.keepAlive = keepAlive;
        this.compress = compress;
        this.token = token;
    }

    public JSONObject makeRequest(URLConnection connection, boolean printTime) throws IOException, InterruptedException {
        long startTime = System.nanoTime();

        InputStream stream = connection.getInputStream();
        if ("gzip".equals(connection.getContentEncoding())) {
            stream = new GZIPInputStream(stream);
        }

        /*
        String header = connection.getHeaderField(0);
        System.out.println(header);
        System.out.println("---Start of headers---");
        int i = 1;
        while ((header = connection.getHeaderField(i)) != null) {
            String key = connection.getHeaderFieldKey(i);
            System.out.println(((key==null) ? "" : key + ": ") + header);
            i++;
        }
        */


        byte[] content = IOUtils.toByteArray(stream);
        JSONObject jsonObj = (JSONObject) JSON.parse(content);

        long totalTime = System.nanoTime() - startTime;

        if (printTime)
            System.out.println(1.0*(totalTime)/1000000);

        Thread.sleep(100);
        return jsonObj;
    }

    public void prepareRequest (URLConnection connection) {
        if (compress) connection.setRequestProperty("Accept-Encoding", "deflate, compress, gzip");
        if (!keepAlive) connection.setRequestProperty("Connection", "close");
    }

    public JSONObject getTrades(int count) throws IOException, InterruptedException {
        String url = "https://api-fxpractice.oanda.com/v1/accounts/3922748/trades?count="+count;
        URLConnection connection = new URL(url).openConnection();
        connection.setRequestProperty("Authorization", "Bearer "+token);

        prepareRequest(connection);
        return makeRequest(connection, true);
    }

    public JSONObject makeOrder() throws IOException, InterruptedException {
        String url = "https://api-fxpractice.oanda.com/v1/accounts/3922748/orders";
        String charset = "UTF-8";
        String instrument = "EUR_USD";
        String side = "buy";
        String type = "market";
        String units = "10";

        String query = String.format("instrument=%s&side=%s&type=%s&units=%s",
                URLEncoder.encode(instrument, charset),
                URLEncoder.encode(side, charset),
                URLEncoder.encode(type, charset),
                URLEncoder.encode(units, charset)
        );

        URLConnection connection = new URL(url).openConnection();
        connection.setDoOutput(true); // Triggers POST.
        connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded;charset=" + charset);
        connection.setRequestProperty("Authorization", "Bearer "+token);

        prepareRequest(connection);

        OutputStream output = connection.getOutputStream();
        try {
            output.write(query.getBytes(charset));
        } finally {
            try { output.close(); } catch (IOException logOrIgnore) {}
        }

        return makeRequest(connection, true);
    }

    public JSONObject closeTrade(int tradeId) throws IOException, InterruptedException {
        String url = "https://api-fxpractice.oanda.com/v1/accounts/3922748/trades/"+tradeId;
        HttpURLConnection connection = (HttpURLConnection)new URL(url).openConnection();
        connection.setDoInput(true);
        connection.setRequestProperty("Authorization", "Bearer "+token);

        connection.setRequestProperty(
                "Content-Type", "application/x-www-form-urlencoded" );
        connection.setRequestMethod("DELETE");

        prepareRequest(connection);
        return makeRequest(connection, true);
    }

    public String getInstrumentList(int count) throws IOException, InterruptedException {
        String url = "https://api-fxpractice.oanda.com/v1/instruments?accountId=3922748";
        URLConnection connection = new URL(url).openConnection();
        connection.setRequestProperty("Authorization", "Bearer "+token);

        prepareRequest(connection);
        JSONObject response =  makeRequest(connection, false);
        JSONArray instruments = (JSONArray)response.get("instruments");

        String instrumentList = "";
        for (int i=0; i<count; i++) {
            if (i!=0)
                instrumentList += "%2C";

            JSONObject instrument = (JSONObject)instruments.get(i);
            String instrumentStr = (String)instrument.get("instrument");
            instrumentList += instrumentStr;
        }

        return instrumentList;
    }

    public JSONObject getQuotes(String instrumentList) throws IOException, InterruptedException {
        String url = "https://api-fxpractice.oanda.com/v1/quote?instruments="+instrumentList;
        URLConnection connection = new URL(url).openConnection();
        connection.setRequestProperty("Authorization", "Bearer "+token);

        prepareRequest(connection);
        return makeRequest(connection, true);
    }

}
