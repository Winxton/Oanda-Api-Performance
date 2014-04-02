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
    public static JSONObject makeRequest(URLConnection connection) throws IOException, InterruptedException {
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
        System.out.println(1.0*(totalTime)/1000000);
        Thread.sleep(100);

        return jsonObj;
    }

    public static JSONObject getTrades(int count, boolean keepAlive, boolean compress) throws IOException, InterruptedException {
        String url = "https://api-fxpractice.oanda.com/v1/accounts/3922748/trades?count="+count;
        String charset = "UTF-8";
        URLConnection connection = new URL(url).openConnection();
        connection.setRequestProperty("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22");
        connection.setRequestProperty("Accept-Charset", charset);
        if (compress) connection.setRequestProperty("Accept-Encoding", "deflate, compress, gzip");
        if (!keepAlive) connection.setRequestProperty("Connection", "close");

        return makeRequest(connection);
    }

    public static JSONObject makeOrder(boolean keepAlive, boolean compress) throws IOException, InterruptedException {
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
        connection.setRequestProperty("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22");
        if (compress) connection.setRequestProperty("Accept-Encoding", "deflate, compress, gzip");
        if (!keepAlive) connection.setRequestProperty("Connection", "close");

        OutputStream output = connection.getOutputStream();
        try {
            output.write(query.getBytes(charset));
        } finally {
            try { output.close(); } catch (IOException logOrIgnore) {}
        }

        return makeRequest(connection);
    }

    public static JSONObject closeTrade(int tradeId, boolean keepAlive, boolean compress) throws IOException, InterruptedException {
        String url = "https://api-fxpractice.oanda.com/v1/accounts/3922748/trades/"+tradeId;
        HttpURLConnection connection = (HttpURLConnection)new URL(url).openConnection();
        connection.setDoInput(true);
        connection.setRequestProperty("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22");

        connection.setRequestProperty(
                "Content-Type", "application/x-www-form-urlencoded" );
        connection.setRequestMethod("DELETE");

        if (compress) connection.setRequestProperty("Accept-Encoding", "deflate, compress, gzip");
        if (!keepAlive) connection.setRequestProperty("Connection", "close");

        return makeRequest(connection);
    }

}
