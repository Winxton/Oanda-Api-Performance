#include <iostream>
#include <Poco/Net/HTTPSClientSession.h>
#include <Poco/Net/HTTPRequest.h>
#include <Poco/Net/HTTPResponse.h>
#include <Poco/Net/SSLManager.h>
#include <Poco/StreamCopier.h>
#include <Poco/Path.h>
#include <Poco/URI.h>
#include <Poco/Exception.h>
#include <string>
#include <sstream>
#include <chrono>

#include <unistd.h>
#include "cJSON.h"
using namespace Poco;
using namespace Poco::Net;
using namespace std;


int openTrade(HTTPSClientSession &session) {
    string path = "/v1/accounts/3922748/orders";

    // send request
    HTTPRequest req(HTTPRequest::HTTP_POST, path, HTTPMessage::HTTP_1_1);
    req.set("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22");
    req.setContentType("application/x-www-form-urlencoded");
    string requestBody("instrument=EUR_USD&side=buy&units=10&type=market");
    req.setContentLength( requestBody.length() );

    auto startInd = std::chrono::high_resolution_clock::now();

    session.sendRequest(req) << requestBody;
    // get response
    HTTPResponse res;
    //cout << res.getStatus() << " " << res.getReason() << endl;

    ostringstream oss;
    oss << session.receiveResponse(res).rdbuf();
    //cout << s << endl;

    cJSON *root = cJSON_Parse(oss.str().c_str());
    cJSON *tradeOpened = cJSON_GetObjectItem(root,"tradeOpened");
    //cout << cJSON_GetObjectItem(tradeOpened, "id")->valueint << endl;

    auto finishInd = std::chrono::high_resolution_clock::now();
    cout << 1.0*std::chrono::duration_cast<std::chrono::nanoseconds>(finishInd-startInd).count()/1000000 << "\n";
    
    return cJSON_GetObjectItem(tradeOpened, "id")->valueint;
}

void closeTrades(HTTPSClientSession &session, int trade_id) {
    string path = "/v1/accounts/3922748/trades/" + to_string(trade_id);

    // send request
    HTTPRequest req(HTTPRequest::HTTP_DELETE, path, HTTPMessage::HTTP_1_1);
    req.set("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22");
    req.set("Accept-Encoding", "deflate, compress, gzip");
    req.setContentType("application/x-www-form-urlencoded");

    auto startInd = std::chrono::high_resolution_clock::now();

    session.sendRequest(req);
    // get response
    HTTPResponse res;
    ostringstream oss;
    oss << session.receiveResponse(res).rdbuf();
    //cout << oss.str() << endl;
    cJSON *root = cJSON_Parse(oss.str().c_str());

    auto finishInd = std::chrono::high_resolution_clock::now();
    cout << 1.0*std::chrono::duration_cast<std::chrono::nanoseconds>(finishInd-startInd).count()/1000000 << "\n";
}


void getTrades(HTTPSClientSession &session, int numTrades, bool showJsonTime=false) {
    string path = "/v1/accounts/3922748/trades?count=" + to_string(numTrades);

    // send request
    HTTPRequest req(HTTPRequest::HTTP_GET, path, HTTPMessage::HTTP_1_1);
    req.set("Authorization", "Bearer b47aa58922aeae119bcc4de139f7ea1e-27de2d1074bb442b4ad2fe0d637dec22");
    req.set("Accept-Encoding", "deflate, compress, gzip");
    auto startInd = std::chrono::high_resolution_clock::now();

    //cout << "sending request..." << endl;
    session.sendRequest(req);

    // get response
    HTTPResponse res;
    //cout << res.getStatus() << " " << res.getReason() << endl;
    
    // print response
    ostringstream oss;
    oss << session.receiveResponse(res).rdbuf();
    
    auto jsonStart = std::chrono::high_resolution_clock::now();
    cJSON *root = cJSON_Parse(oss.str().c_str());

    if (showJsonTime)
        cout << "JSONTIME: " << 1.0*std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now()-jsonStart).count()/1000000 << "\n";

    //cout << s << endl;
    
    auto finishInd = std::chrono::high_resolution_clock::now();
    cout << 1.0*std::chrono::duration_cast<std::chrono::nanoseconds>(finishInd-startInd).count()/1000000 << "\n";
}

int main (int argc, char* argv[]) {
    
    try {
        const Context::Ptr context = new Context(Context::CLIENT_USE, "", "", "", Context::VERIFY_NONE, 9, false, "ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH");

        if (argc == 2) {
            const int NUM_REQ = atoi(argv[1]);

            cout << NUM_REQ << " Requests" << endl; 

            // prepare session
            string host = "api-fxpractice.oanda.com";
            HTTPSClientSession session(host, 443, context);
            session.setKeepAlive(true);
            
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

        } else {
            cout << "enter [number of requests]" << endl;
        }



    } catch (const Exception &e) {
        cerr << e.displayText() << endl;
    }
}
