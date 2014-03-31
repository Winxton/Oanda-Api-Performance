import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpDelete;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicHeader;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

/**
 * Created by wwu on 28/03/14.
 */
public class ApacheHttpRequest {
    public static JSONObject makeRequest(DefaultHttpClient httpClient, HttpUriRequest request) throws IOException {
        // Time the latency
        long startTime = System.nanoTime();

        HttpResponse resp = httpClient.execute(request);

        long totalTime = System.nanoTime() - startTime;
        System.out.println(1.0*totalTime/1000000);

        HttpEntity entity = resp.getEntity();

        //EntityUtils.consume(entity);

         /*
        Header[] headers = resp.getAllHeaders();
        for (Header header : headers) {
            System.out.println(header.getName() + " " + header.getValue());
        }
        */

        JSONObject respObj;

        if (resp.getStatusLine().getStatusCode() == 200 && entity != null) {
            InputStream stream = entity.getContent();
            BufferedReader br = new BufferedReader(new InputStreamReader(stream));

            respObj = (JSONObject) JSONValue.parse(br);

        } else {
            // print error message
            String responseString = EntityUtils.toString(entity, "UTF-8");
            respObj = (JSONObject)JSONValue.parse(responseString);
        }

        //System.out.println(respObj.toJSONString());
        return respObj;

    }

    public static JSONObject getTrades(DefaultHttpClient httpClient, int numTrades) throws IOException{

        HttpUriRequest httpRequest = new HttpGet("https://api-fxpractice.oanda.com/v1/accounts/3922748/trades?count=" + numTrades);
        httpRequest.setHeader(new BasicHeader("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22"));

        return makeRequest(httpClient, httpRequest);
    }

    public static JSONObject createTrade(DefaultHttpClient httpClient) throws IOException {

        HttpPost httpRequest = new HttpPost("https://api-fxpractice.oanda.com/v1/accounts/3922748/orders");
        httpRequest.setHeader(new BasicHeader("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22"));

        List<NameValuePair> nvps = new ArrayList<NameValuePair>();
        nvps.add(new BasicNameValuePair("instrument", "EUR_USD"));
        nvps.add(new BasicNameValuePair("side", "buy"));
        nvps.add(new BasicNameValuePair("type", "market"));
        nvps.add(new BasicNameValuePair("units", "10"));

        httpRequest.setEntity(new UrlEncodedFormEntity(nvps, "utf-8"));

        return makeRequest(httpClient, httpRequest);
    }

    public static JSONObject closeTrade(DefaultHttpClient httpClient, int tradeId) throws IOException {
        HttpDelete httpRequest = new HttpDelete("https://api-fxpractice.oanda.com/v1/accounts/3922748/trades/" + tradeId);
        httpRequest.setHeader(new BasicHeader("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22"));

        return makeRequest(httpClient, httpRequest);
    }
}
