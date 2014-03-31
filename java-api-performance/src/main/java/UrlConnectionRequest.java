import org.apache.http.protocol.HTTP;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;

/**
 * Created by wwu on 28/03/14.
 */
public class UrlConnectionRequest {
    public static JSONObject makeRequest(URLConnection connection) throws IOException {

        long startTime = System.nanoTime();

        InputStream response = connection.getInputStream();

        long totalTime = System.nanoTime() - startTime;
        System.out.println(1.0*totalTime/1000000);

        BufferedReader br = new BufferedReader(new InputStreamReader(response));
        JSONObject jsonObj = (JSONObject) JSONValue.parse(br);
        return jsonObj;
    }

    public static JSONObject getTrades(int count) throws IOException {
        String url = "https://api-fxpractice.oanda.com/v1/accounts/3922748/trades?count="+count;
        String charset = "UTF-8";
        URLConnection connection = new URL(url).openConnection();
        connection.setRequestProperty("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22");
        connection.setRequestProperty("Accept-Charset", charset);
        return makeRequest(connection);
    }

    public static JSONObject makeOrder() throws IOException {
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

        OutputStream output = connection.getOutputStream();
        try {
            output.write(query.getBytes(charset));
        } finally {
            try { output.close(); } catch (IOException logOrIgnore) {}
        }

        return makeRequest(connection);
    }

    public static JSONObject closeTrade(int tradeId) throws IOException {
        String url = "https://api-fxpractice.oanda.com/v1/accounts/3922748/trades/"+tradeId;
        HttpURLConnection connection = (HttpURLConnection)new URL(url).openConnection();
        connection.setDoInput(true);
        connection.setRequestProperty("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22");
        connection.setRequestProperty(
                "Content-Type", "application/x-www-form-urlencoded" );
        connection.setRequestMethod("DELETE");
        return makeRequest(connection);
    }

}
