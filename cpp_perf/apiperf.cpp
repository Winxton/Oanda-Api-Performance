#include <iostream>
#include <Poco/Net/HTTPSClientSession.h>
#include <Poco/Net/HTTPRequest.h>
#include <Poco/Net/HTTPResponse.h>
#include <Poco/Net/SSLManager.h>
#include <Poco/StreamCopier.h>
#include <Poco/Path.h>
#include <Poco/URI.h>
#include <Poco/Exception.h>

#include "Poco/InflatingStream.h"

#include <string>
#include <sstream>
#include <chrono>
#include <zlib.h>

#include <unistd.h>
#include "cJSON.h"
using namespace Poco;
using namespace Poco::Net;
using namespace std;

bool keepAlive = true;
bool doCompress = true;
string access_token = "b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22";

void prepareRequestHeaders (HTTPRequest &request) {
    if (!keepAlive) request.set("Connection", "close");
    if (doCompress) request.set("Accept-Encoding", "deflate, compress, gzip");
    request.set("Authorization", "Bearer "+access_token);
}

cJSON *makeRequest (HTTPSClientSession &session, HTTPRequest &request, string &requestBody, bool showTime=true) {
    auto startInd = std::chrono::high_resolution_clock::now();

    // send request

    session.sendRequest(request) << requestBody;
    
    // get response
    HTTPResponse res;

    ostringstream ss;
    istream& is = session.receiveResponse(res);

    /*
    cout << res.getStatus() << " " << res.getReason() 
    << " " << res.get("Connection") << " " << res.get("content-encoding") << endl;  
    */
    if (res.has("content-encoding") &&  res.get("content-encoding")=="gzip") {
        Poco::InflatingInputStream inflater(is, Poco::InflatingStreamBuf::STREAM_GZIP);
        StreamCopier::copyStream( inflater, ss );
    } else {
        StreamCopier::copyStream( is, ss );
    }
    //cout << ss.str() << endl;
    
    //decode json
    cJSON *root = cJSON_Parse(ss.str().c_str());

    auto finishInd = std::chrono::high_resolution_clock::now();

    if (showTime)
        cout << 1.0*std::chrono::duration_cast<std::chrono::nanoseconds>(finishInd-startInd).count()/1000000 << "\n";

    return root;
}

int openTrade(HTTPSClientSession &session) {
    string path = "/v1/accounts/3922748/orders";

    // send request
    HTTPRequest req(HTTPRequest::HTTP_POST, path, HTTPMessage::HTTP_1_1);
    prepareRequestHeaders(req);
    req.setContentType("application/x-www-form-urlencoded");

    string requestBody("instrument=EUR_USD&side=buy&units=10&type=market");
    req.setContentLength( requestBody.length() );

    cJSON *root = makeRequest(session, req, requestBody);

    cJSON *tradeOpened = cJSON_GetObjectItem(root,"tradeOpened");

    return cJSON_GetObjectItem(tradeOpened, "id")->valueint;
}

cJSON *closeTrades(HTTPSClientSession &session, int trade_id) {
    string path = "/v1/accounts/3922748/trades/" + to_string(trade_id);

    // send request
    HTTPRequest req(HTTPRequest::HTTP_DELETE, path, HTTPMessage::HTTP_1_1);
    prepareRequestHeaders(req);
    req.setContentType("application/x-www-form-urlencoded");

    string requestBody = "";
    return makeRequest(session, req, requestBody);
}


cJSON *getTrades(HTTPSClientSession &session, int numTrades) {
    string path = "/v1/accounts/3922748/trades?count=" + std::to_string(numTrades);

    // send request
    HTTPRequest req(HTTPRequest::HTTP_GET, path, HTTPMessage::HTTP_1_1);
    prepareRequestHeaders(req);

    string requestBody = "";
    return makeRequest(session, req, requestBody);
}

cJSON *getQuotes(HTTPSClientSession &session, string instrumentList) {
    string path = "/v1/quote?instruments="+instrumentList;

    // send request
    HTTPRequest req(HTTPRequest::HTTP_GET, path, HTTPMessage::HTTP_1_1);
    prepareRequestHeaders(req);

    string requestBody = "";
    return makeRequest(session, req, requestBody);
}

/* randomly gets a number of instruments */
string getInstrumentList(HTTPSClientSession &session, int numInstruments) {
    HTTPRequest instrumentsRequest(HTTPRequest::HTTP_GET, "/v1/instruments?accountId=3922748", HTTPMessage::HTTP_1_1);
    instrumentsRequest.set("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22");
    prepareRequestHeaders(instrumentsRequest);
    string body = "";

    cJSON *response = makeRequest(session, instrumentsRequest, body, false);
    cJSON *instruments = cJSON_GetObjectItem(response,"instruments");

    //cout << cJSON_GetArraySize(instruments) << endl;
    stringstream ss;

    for (int i=0; i< numInstruments; i++) {
        cJSON *instrument = cJSON_GetArrayItem(instruments, i);
        string item = cJSON_GetObjectItem(instrument, "instrument")->valuestring;
        if (i!=0)
            ss << "%2c";
        ss << item;
    }

    return ss.str();
}

int main (int argc, char* argv[]) {
    
    try {
        const Context::Ptr context = new Context(Context::CLIENT_USE, "", "", "", Context::VERIFY_NONE, 9, false, "ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH");

        if (argc == 4) {
            const int NUM_REQ = atoi(argv[1]);
            keepAlive = atoi(argv[2]) == 1 ? true : false;
            doCompress = atoi(argv[3]) == 1 ? true : false;

            cout << NUM_REQ << " Requests" << endl; 
            cout << "Keep alive: " << keepAlive << endl;
            cout << "Compression: " << doCompress << endl; 

            // prepare session
            string host = "api-fxpractice.oanda.com";
            HTTPSClientSession session(host, 443, context);
            session.setKeepAlive(true);

            string instrumentList = getInstrumentList(session, 10);
            cout << "\nGET 10 QUOTES" << endl;
            for (int i =0; i<NUM_REQ; i++) {
                getQuotes(session, instrumentList);
            }

            instrumentList = getInstrumentList(session, 50);
            cout << "\nGET 50 QUOTES" << endl;
            for (int i =0; i<NUM_REQ; i++) {
                getQuotes(session, instrumentList);
            }

            instrumentList = getInstrumentList(session, 120);
            cout << "\nGET 120 QUOTES" << endl;
            for (int i =0; i<NUM_REQ; i++) {
                getQuotes(session, instrumentList);
            }

            /*
            vector<int> trades;

            cout << "\nOPEN TRADES" << endl;
            for (int i =0; i<NUM_REQ; i++) {
                int trade_id = openTrade(session);
                trades.push_back(trade_id);
            }
            
            cout << "\nCLOSE TRADES" << endl;
            for(int trade_id : trades) {
                closeTrades(session, trade_id);
            }

            cout << "\nGET 10 TRADES" << endl;
            for (int i = 0 ; i < NUM_REQ ; i++)
            {
                getTrades(session, 10);
            }

            cout << "\nGET 50 TRADES" << endl;
            for (int i = 0 ; i < NUM_REQ ; i++)
            {
                getTrades(session, 50);
            }

            cout << "\nGET 100 TRADES" << endl;
            for (int i = 0 ; i < NUM_REQ ; i++)
            {
                getTrades(session, 100);
            }

            cout << "\nGET 500 TRADES" << endl;
            for (int i = 0 ; i < NUM_REQ ; i++)
            {
                getTrades(session, 500);
            }
            */

        } else {
            cout << "enter [number of requests] [keep-alive] [compress]" << endl;
        }
    } catch (const Exception &e) {
        cerr << e.displayText() << endl;
    }
}
