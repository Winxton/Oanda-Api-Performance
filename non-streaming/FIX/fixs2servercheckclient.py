#!/oanda/system/bin/python2.7

"""fixs2servercheck.py script attempts a login and a EUR/USD snapshot to
verify that a FIXS deployment is working."""

#
# Copyright (c) 2010-2012, OANDA Corporation, all rights reserved.
#
# provided for testing connectivity to the OANDA FIX API only
#


#import testfix
import getopt
import re
import socket
import ssl
import sys
import time
import datetime
import string
import random


#
# args
# -l            - optional boolean flag for login check only
# -u username   - required username
# -p password   - required password
# -H host       - required hostname
# -P port       - required port
#
# -Z            - optional boolean flag for zabbix mode
# -S            - optional boolean flag for SSL socket
# -C cipher     - optional ciper specification (requires -S)
# -B BeginString - optional BeginString <8> (default 'FIX.4.2')
# -T TargetSubID - optional TargetSubID <57> (default none)
# -I HeartBtInt - optional HeartBtInt <108> value (default 300)
# -U            - optional prefix log lines with microsecond-resolution UTC timestamp
#
# -s symbols    - optional symbols to query for rate
# -r nummsgs    - optional symbol incremental refresh mode (requires -s)
# -R MDReqID    - optional MDReqID to use for <V>
# -o OrderSide  - optional side for test order to be sent
# -a Account    - required if -o flag has been set, otherwise optional
# -L LimitPrice - required for client test
# -m message    - optional FIX message to send, prefixed with 35= msgtype
#


#defaults
opt_username = ''
opt_password = ''
opt_host = ''
opt_port = 0
opt_zabbix_mode = False
opt_logincheck = False
opt_ssl = False
opt_cipher = ''
opt_beginstring = 'FIX.4.2'
opt_targetsubid = ''
opt_heartbtint = 300
opt_utctimestamp = False
opt_symbol = None
opt_refresh = None
opt_mdreqid = None
opt_side = None
opt_account = None
opt_limit = None
opt_message = None

opt_symbol_parsed = None
SYMBOL_DELIMITERS = ',.;_-|!@#$%^&*+=~'
SYMBOL_SPLIT_TRANS = string.maketrans(SYMBOL_DELIMITERS, " "*len(SYMBOL_DELIMITERS))


def log( s ) :
    if not opt_zabbix_mode :
        print (datetime.datetime.utcnow().strftime('%Y%m%d-%X.%fZ ') if opt_utctimestamp else '') + s
        pass
    return

def zabbixcode( int_value ) :
    if opt_zabbix_mode :
        print repr( int_value )
        pass
    return

def replace_tag_value( msg, tag, value ) :
    """Replace a value corresponding to a tag in a message."""
    _TAG_RE = re.compile('\x01' + str(tag) + '=' + '[\s\w:-]*' + '\x01')
    msg = _TAG_RE.sub('\x01' + str(tag) + '=' + str(value) + '\x01', msg,1)
    return msg

def format_fix_msg( msg, replace_timestamp=True, replace_length=True ) :
    """Formats a string already mostly a complete FIX message with 9= (if needed),
    52= (if needed), and 10= values.
    Input string must already contain 9= 35= 52= 10= placeholders, and all
    SOH bytes must be present.

    replace_timestamp:
        True => if the user does _not_ have an existing, properly formatted FIX timestamp,
        creates a new timestamp with the current time formatted as a FIX timestamp
        False => leaves the timestamp alone
    replace_length:
        True => replaces the length field with the proper message length
        False => leaves the length alone
    """

    _FULL_FIX_SENDTIME_RE = re.compile('\x0152=[0-9]{8}-[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]{3})?\x01')
    _LENGTH_RE = re.compile('(\x019=[0-9]*)\x01')

    if replace_timestamp :
        # as a last just-in-case, we'll see if the user already put in a full-FIX-formatted ts
        # if so, leave it alone
        full_sendTime_present = _FULL_FIX_SENDTIME_RE.search(msg)
        if not full_sendTime_present :
            msg = replace_tag_value( msg, 52, time.strftime('%Y%m%d-%H:%M:%S',time.gmtime()) )

    # now calculate 9= length
    # hmm. length could be zero if both checksum & msg length aren't there
    len = msg.find('\x0110=') - msg.find('\x0135=')
    len_tag = _LENGTH_RE.search(msg)
    if len_tag and replace_length :
        msg = msg.replace( len_tag.group(1), '\x019=' + str(len) )
    # now calculate checksum
    len_end = msg.find('\x0110=')
    if  len_end != -1 :
        checksum = 0
        for i in msg[:len_end+1] :
            checksum += ord(i)
            msg = msg[:len_end+1] + '10=' + "%03d" % (checksum % 256) + '\x01'
    return msg

def split_fix_msgs( longstring ) :
    """Splits an input string containing multiple complete FIX
    messages into individul FIX messages.
    Returns a tuple, one FIX message per tuple item."""
    return tuple( filter(lambda x: x, re.split('(8=FIX\\.[45]\\.[0-9]\x01.*?\x0110=[0-9]{3}\x01)', longstring)) )

class sockwrap :
    """A wrapper class so that a regular socket presents the read/write
    interface of an SSL-wrapped socket."""

    def __init__( self, s ) :
        self.sock = s
        return

    def connect( self, pair ) :
        return self.sock.connect( pair )

    def read( self, len ) :
        return self.sock.recv( len )

    def write( self, msg ) :
        return self.sock.send( msg )

    def gettimeout( self ) :
        return self.sock.gettimeout()

    def settimeout( self, timeout ) :
        return self.sock.settimeout( timeout )

#
# create socket, optional wrap, connect
#
def do_sock_create_connect( host, port, use_ssl = True, use_cipher = None ) :
    try :
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        s.settimeout( 5.0 )
        if use_ssl :
            if use_cipher :
                sock = ssl.wrap_socket( s, ssl_version = ssl.PROTOCOL_TLSv1, ciphers = use_cipher )
                pass
            else :
                sock = ssl.wrap_socket( s, ssl_version = ssl.PROTOCOL_TLSv1 )
                pass
            pass
        else :
            sock = sockwrap(s)
            pass

        sock.connect( (host, port) )
        return sock
    except Exception as e :
        log( 'do_sock_create_connect exception: ' + repr(e) )
        raise
    return

#
# generate a message template ( populate BeginString, SenderCompID, TargetCompID )
#
def gen_message_template( fix_version, username, targetsubid ) :
    _MESSAGE_TEMPLATE = "8=FIX_VER 9=92 35=MSGTYPE 34=MSGSEQNUM 49=SenderCompID 52= 56=OANDA TARGETSUBID_FIELD BODY_FIELDS 10= "
    if len(targetsubid) :
        tsub = ' 57=' + targetsubid
    else :
        tsub = ''
    return _MESSAGE_TEMPLATE.replace( '8=FIX_VER ', '8=' + fix_version + ' ' ) \
        .replace( ' 49=SenderCompID ', ' 49=' + username + ' ' ) \
        .replace( ' TARGETSUBID_FIELD ', tsub + ' ' )


#
# generate logon message
#
def gen_logon_msg( msg_template, password, heartbtint ) :
    _BODY_FIELDS = ' PASSWORD_FIELDS 98=0 108=HEARTBTINT 141=Y '

    out_msg = msg_template \
        .replace( ' 35=MSGTYPE ',   ' 35=A '     ) \
        .replace( ' 34=MSGSEQNUM ', ' 34=1 '     ) \
        .replace( ' BODY_FIELDS ',  _BODY_FIELDS )

    fix_version = re.search('8=(FIX\.[1-9]\.[0-9]) ',out_msg).group(1)

    if fix_version == 'FIX.4.2' :
        out_msg = out_msg.replace(
            ' PASSWORD_FIELDS ',
            ' 95=' + str(len(password)) + ' 96=' + password + ' '
            ) \
            .replace( ' 108=HEARTBTINT ', ' 108=' + str(heartbtint) + ' ' )
        pass
    elif fix_version == 'FIX.4.3' or fix_version == 'FIX.4.4' :
        out_msg = out_msg.replace(
            ' PASSWORD_FIELDS ', ' 554=' + password + ' '
            ) \
            .replace( ' 108=HEARTBTINT ', ' 108=' + str(heartbtint) + ' ' )
        pass
    else :
        log( 'fix_version \'' + fix_version + '\' not recognized/supported' )
        out_msg = ''
        pass

    return format_fix_msg( out_msg.replace(' ','\x01') )

#
# send logon message, receive logon response, news message
#
def do_logon_news_sequence( sock, msg_template, password, heartbtint ) :

    try :

        out_msg = gen_logon_msg( msg_template, password, heartbtint )

        log( "send: [" + out_msg.replace('\x01',' ') + ']' )

        try :
            bytes_out = sock.write( out_msg )
            pass
        except socket.error as e :
            log( 'do_logon_news_sequence send error: ' + repr(e) )
            raise

        # verify logon response and news message
        logon_resp_received = None
        news_msg_received = None
        logout_resp_received = None

        try :
            while not (logon_resp_received and news_msg_received) and not logout_resp_received :
                data_in = sock.read(4096)
                if not data_in :
                    log("socket closed by remote side")
                    break

                for i in split_fix_msgs( data_in ) :
                    log( "recv: [" + i.replace('\x01',' ') + ']' )
                    if re.search('\x0135=A\x01', i) :
                        log( "logon received" )
                        logon_resp_received = True
                        pass
                    if re.search('\x0135=B\x01', i) :
                        log( "news received" )
                        news_msg_received = True
                        pass
                    if re.search('\x0135=5\x01', i) :
                        log( "logout received" )
                        logout_resp_received = True
                        pass
        except socket.timeout :
            log("timeout encountered")
        except socket.error as e :
            log( 'error: socket error: ' + repr(e) )
            raise

        if logout_resp_received :
            log( "error: logon rejected" )
            return False

        if logon_resp_received :
            log( 'logon successful' )
        else :
            log( 'no logon response received' )
            return False
        pass

    except :
        log( 'exception: ' + repr(sys.exc_info()) )
        return False

    return True

#
# general message
#
def gen_general_msg( msg_template, msgseqnum, msgbody ) :

    # find the 35= part and the remainder
    _MESSAGE_SPLIT = re.compile('35=([^ ]+) (.+)')

    message_parts = _MESSAGE_SPLIT.search( msgbody )

    return format_fix_msg(
        msg_template \
            .replace( ' 35=MSGTYPE ',   ' 35=' + message_parts.group(1) + ' ' ) \
            .replace( ' 34=MSGSEQNUM ', ' 34=' + repr(msgseqnum) + ' ' ) \
            .replace( ' BODY_FIELDS ',  ' ' + message_parts.group(2) + ' ' ) \
            .replace( ' ', '\x01' ) \
        )

#
# market data snapshot request utility method
#
def gen_mdr_msg( msg_template, msgseqnum, symbol_list, mdreqid, requesttype='0' ) :

    MDR_BODY = '35=V 262=MDReqID 263=SubscriptionRequestType 264=1 MDUPDATETYPE MDENTRYTYPES SYMBOLGROUP END'

    # there is likely a better, pythonic way...
    default_mdreqid = ''
    symbol_group = ''
    for i in symbol_list :
        default_mdreqid += '_' + i
        symbol_group += ' 55=' + i
        pass

    return gen_general_msg(
        msg_template,
        msgseqnum,
        MDR_BODY \
            .replace( ' 262=MDReqID ', ' 262=mdreq_' + str(random.randint(10000, 99999)) + ' ' ) \
            .replace( ' 263=SubscriptionRequestType ', ' 263=' + requesttype + ' ' ) \
            .replace( ' MDUPDATETYPE ', ' 265=1 ' if requesttype == '1' else ' ' ) \
            .replace( ' MDENTRYTYPES ', ' 267=2 269=0 269=1 ' if not requesttype == '2' else ' 267=0 ' ) \
            .replace( ' SYMBOLGROUP ', ' 146=' + repr(len(symbol_list)) + symbol_group + ' ' if not requesttype == '2' else ' 146=0 ') \
            .replace( ' END', '' ) #remove last space
        )


def do_symbol_subscription( sock, msg_template, msgseqnum, msgcount, symbol_list, mdreqid ) :

    out_message_counter = 0

    if not do_snapshot_request_response( sock, msg_template, msgseqnum, symbol_list, mdreqid, subscribe = True ) :
        log( 'subscription failure' )
        return out_message_counter

    in_x_msg_counter = 0
    out_message_counter += 1

    sock_original_timeout = sock.gettimeout()

    try :
        sock.settimeout( opt_heartbtint - 5 )
        heartbeat_counter = 0
        heartbeat_msginterval = 10 # dumb, send heartbeat every x messages in
        while in_x_msg_counter < msgcount :
            data_in = sock.read(4096)
            if not data_in :
                log( "socket closed by remote side" )
                break
            for i in split_fix_msgs(data_in) :
                log( "recv: [" + i.replace('\x01',' ') + ']' )
                heartbeat_counter += 1
                if re.search('\x0135=X\x01', i) :
                    in_x_msg_counter += 1
                if heartbeat_counter >= heartbeat_msginterval :
                    heartbeat_counter = 0
                    out_msg = gen_general_msg( msg_template, msgseqnum + out_message_counter, '35=1 112=test' )
                    log( "send: [" + out_msg.replace('\x01',' ') + ']' )
                    try :
                        bytes_out = sock.write( out_msg )
                        out_message_counter += 1
                        pass
                    except socket.error as e :
                        log( 'do_symbol_subscription send error: ' + repr(e) )
                        raise
                    pass #if
                pass # for
            pass # while True
    except socket.timeout :
        log("timeout encountered")
    except socket.error as e :
        log( 'error: socket error: ' + repr(e) )
        raise
    except :
        log( 'exception: ' + repr(sys.exc_info()) )
        raise

    sock.settimeout( sock_original_timeout )

    if in_x_msg_counter < msgcount :
        raise Exception("full incremental refresh count not received")

    out_msg = gen_mdr_msg( msg_template, msgseqnum + out_message_counter, symbol_list, mdreqid, requesttype='2' )
    log( "send: [" + out_msg.replace('\x01',' ') + ']' )
    try :
        bytes_out = sock.write( out_msg )
        out_message_counter += 1
        pass
    except socket.error as e :
        log( 'do_symbol_subscription send error: ' + repr(e) )
        raise

    return out_message_counter

#
# snapshot request/response
#
def do_snapshot_request_response( sock, msg_template, msgseqnum, symbol_list, mdreqid, subscribe = False ) :

    out_message_counter = 0

    out_msg = gen_mdr_msg( msg_template, msgseqnum + out_message_counter, symbol_list, mdreqid, '1' if subscribe else '0' )

    log( "send: [" + out_msg.replace('\x01',' ') + ']' )

    try :
        bytes_out = sock.write( out_msg )
        out_message_counter += 1
        pass
    except socket.error as e :
        log( 'do_snapshot_request_response send error: ' + repr(e) )
        raise

    mdr_fullrefresh_received = 0

    try :
        while mdr_fullrefresh_received < len(symbol_list) :
            data_in = sock.read(4096)
            if not data_in :
                log("socket closed by remote side")
                break

            for i in split_fix_msgs( data_in ) :
                log( "recv: [" + i.replace('\x01',' ') + ']' )

                if re.search('\x0135=W\x01',i) :
                    mdr_fullrefresh_received += 1
                    pass
    except socket.timeout :
        log("timeout encountered")
    except socket.error as e :
        log( 'error: socket error: ' + repr(e) )
        raise

    if mdr_fullrefresh_received == len(symbol_list) :
        log( 'mdr successful' )
    else :
        raise Exception("market data full refresh(es) not received")

    return out_message_counter


#
# new order request/response method
#
def do_neworder_request_response( sock, msg_template, msgseqnum, symbol_list, side, account, clientOrderID ) :

    MDR_BODY = '35=D 1=Account 11=OrderID 21=1 38=1 40=1 54=SIDE 60=Time SYMBOLGROUP END'

    out_msg = gen_general_msg(
        msg_template,
        msgseqnum,
        MDR_BODY \
            .replace( ' 1=Account ', ' 1=' + account + ' ' if account else ' ' ) \
            .replace( ' 11=OrderID ', ' 11=' + clientOrderID + ' ' ) \
            .replace( ' 54=SIDE ', ' 54=' + str(side) + ' ' ) \
            .replace( ' SYMBOLGROUP ', ' 55=' + symbol_list[0] + ' ' ) \
            .replace( ' 60=Time ', ' 60=' + datetime.datetime.utcnow().strftime('%Y%m%d-%H:%M:%S.%f')[:-3] + ' ') \
            .replace( ' END', '' ) #remove last space
        )
    try :
        log( "send: [" + out_msg.replace('\x01',' ') + ']' )
        try :
            bytes_out = sock.write( out_msg )
            pass
        except socket.error as e :
            log( 'do_neworder_request_response send error: ' + repr(e) )
            raise
        response_received = None
        reject_received = None
        try :
            while not (response_received or reject_received):
                data_in = sock.read(4096)
                if not data_in :
                    log("socket closed by remote side")
                    break
                for i in split_fix_msgs(data_in) :
                    log( "recv: [" + i.replace('\x01',' ') + ']' )
                    if re.search('\x0135=[3j]\x01',i) :
                        reject_received = True
                        pass
                    if re.search('\x0135=8\x01.*\x0139=8\x01',i) :
                        reject_received = True
                        pass
                    elif re.search('\x0135=8\x01',i) :
                        response_received = True
                        pass
        except socket.timeout :
            log("no response to request")
        except socket.error as e :
            log( 'error: socket error: ' + repr(e) )
            raise

        if response_received :
            log("Execution Report received")
        elif reject_received :
            log("order reject received")
            raise
        else :
            log("NO RESPONSE RECEIVED")

        pass

    except :
        return False

    return True

#
# new limit order request/response method
#
def do_newlimitorder_request_response( sock, msg_template, msgseqnum, symbol_list, side, account, limit, clientOrderID ) :

    MDR_BODY = '35=D 1=Account 11=OrderID 21=1 38=1 40=2 44=LIMIT 54=SIDE 59=0 60=Time SYMBOLGROUP END'

    out_msg = gen_general_msg(
        msg_template,
        msgseqnum,
        MDR_BODY \
            .replace( ' 1=Account ', ' 1=' + account + ' ' if account else ' ' ) \
            .replace( ' 11=OrderID ', ' 11=' + clientOrderID + ' ' ) \
            .replace( ' 44=LIMIT ', ' 44=' + str(limit) + ' ' ) \
            .replace( ' 54=SIDE ', ' 54=' + str(side) + ' ' ) \
            .replace( ' SYMBOLGROUP ', ' 55=' + symbol_list[0] + ' ' ) \
            .replace( ' 60=Time ', ' 60=' + time.strftime('%Y%m%d-%H:%M:%S',time.gmtime()) + ' ' ) \
            .replace( ' END', '' ) #remove last space
        )
    try :
        log( "send: [" + out_msg.replace('\x01',' ') + ']' )
        try :
            bytes_out = sock.write( out_msg )
            pass
        except socket.error as e :
            log( 'do_newlimitorder_request_response send error: ' + repr(e) )
            raise
        response_received = None
        reject_received = None
        try :
            while not (response_received or reject_received):
                data_in = sock.read(4096)
                if not data_in :
                    log("socket closed by remote side")
                    break
                for i in split_fix_msgs(data_in) :
                    log( "recv: [" + i.replace('\x01',' ') + ']' )
                    if re.search('\x0135=[3j]\x01',i) :
                        reject_received = True
                        pass
                    if re.search('\x0135=8\x01.*\x0139=8\x01',i) :
                        reject_received = True
                        pass
                    elif re.search('\x0135=8\x01',i) :
                        response_received = True
                        pass
        except socket.timeout :
            log("no response to request")
        except socket.error as e :
            log( 'error: socket error: ' + repr(e) )
            raise

        if response_received :
            log("Execution Report received")
        elif reject_received :
            log("order reject received")
            raise
        else :
            log("NO RESPONSE RECEIVED")

        pass

    except :
        return False

    return True

#
# change existing limit order request/response method
#
def do_changeorder_request_response( sock, msg_template, msgseqnum, symbol_list, side, account, limit, origClientOrderID, clientOrderID ) :

    MDR_BODY = '35=G 1=Account 11=OrderID 21=1 38=5 40=2 41=OrigOrderID 44=LIMIT 54=SIDE 59=0 60=Time SYMBOLGROUP END'

    out_msg = gen_general_msg(
        msg_template,
        msgseqnum,
        MDR_BODY \
            .replace( ' 1=Account ', ' 1=' + account + ' ' if account else ' ' ) \
            .replace( ' 11=OrderID ', ' 11=' + clientOrderID + ' ' ) \
            .replace( ' 41=OrigOrderID ', ' 41=' + origClientOrderID + ' ' ) \
            .replace( ' 44=LIMIT ', ' 44=' + str(limit) + ' ' ) \
            .replace( ' 54=SIDE ', ' 54=' + str(side) + ' ' ) \
            .replace( ' SYMBOLGROUP ', ' 55=' + symbol_list[0] + ' ' ) \
            .replace( ' 60=Time ', ' 60=' + time.strftime('%Y%m%d-%H:%M:%S',time.gmtime()) + ' ' ) \
            .replace( ' END', '' ) #remove last space
        )
    try :
        log( "send: [" + out_msg.replace('\x01',' ') + ']' )
        try :
            bytes_out = sock.write( out_msg )
            pass
        except socket.error as e :
            log( 'do_newlimitorder_request_response send error: ' + repr(e) )
            raise
        response_received = None
        reject_received = None
        try :
            while not (response_received or reject_received):
                data_in = sock.read(4096)
                if not data_in :
                    log("socket closed by remote side")
                    break
                for i in split_fix_msgs(data_in) :
                    log( "recv: [" + i.replace('\x01',' ') + ']' )
                    if re.search('\x0135=[3j]\x01',i) :
                        reject_received = True
                        pass
                    if re.search('\x0135=8\x01.*\x0139=8\x01',i) :
                        reject_received = True
                        pass
                    elif re.search('\x0135=8\x01',i) :
                        response_received = True
                        pass
        except socket.timeout :
            log("no response to request")
        except socket.error as e :
            log( 'error: socket error: ' + repr(e) )
            raise

        if response_received :
            log("Execution Report received")
        elif reject_received :
            log("order reject received")
            raise
        else :
            log("NO RESPONSE RECEIVED")

        pass

    except :
        return False

    return True

#
# cancel existing limit order request/response method
#
def do_cancelorder_request_response( sock, msg_template, msgseqnum, symbol_list, side, account, origClientOrderID, clientOrderID ) :

    MDR_BODY = '35=F 1=Account 11=OrderID 41=OrigOrderID 54=SIDE 60=Time SYMBOLGROUP END'

    out_msg = gen_general_msg(
        msg_template,
        msgseqnum,
        MDR_BODY \
            .replace( ' 1=Account ', ' 1=' + account + ' ' if account else ' ' ) \
            .replace( ' 11=OrderID ', ' 11=' + clientOrderID + ' ' ) \
            .replace( ' 41=OrigOrderID ', ' 41=' + origClientOrderID + ' ' ) \
            .replace( ' 54=SIDE ', ' 54=' + str(side) + ' ' ) \
            .replace( ' SYMBOLGROUP ', ' 55=' + symbol_list[0] + ' ' ) \
            .replace( ' 60=Time ', ' 60=' + time.strftime('%Y%m%d-%H:%M:%S',time.gmtime()) + ' ' ) \
            .replace( ' END', '' ) #remove last space
        )
    try :
        log( "send: [" + out_msg.replace('\x01',' ') + ']' )
        try :
            bytes_out = sock.write( out_msg )
            pass
        except socket.error as e :
            log( 'do_newlimitorder_request_response send error: ' + repr(e) )
            raise
        response_received = None
        reject_received = None
        try :
            while not (response_received or reject_received):
                data_in = sock.read(4096)
                if not data_in :
                    log("socket closed by remote side")
                    break
                for i in split_fix_msgs(data_in) :
                    log( "recv: [" + i.replace('\x01',' ') + ']' )
                    if re.search('\x0135=[3j]\x01',i) :
                        reject_received = True
                        pass
                    if re.search('\x0135=8\x01.*\x0139=8\x01',i) :
                        reject_received = True
                        pass
                    elif re.search('\x0135=8\x01',i) :
                        response_received = True
                        pass
        except socket.timeout :
            log("no response to request")
        except socket.error as e :
            log( 'error: socket error: ' + repr(e) )
            raise

        if response_received :
            log("Execution Report received")
        elif reject_received :
            log("order reject received")
            raise
        else :
            log("NO RESPONSE RECEIVED")

        pass

    except :
        return False

    return True

#
# change existing limit order request/response method
#
def do_status_request_response( sock, msg_template, msgseqnum, symbol_list, side, clientOrderID ) :

    MDR_BODY = '35=H 11=OrderID 54=SIDE SYMBOLGROUP 790=REQID END'

    out_msg = gen_general_msg(
        msg_template,
        msgseqnum,
        MDR_BODY \
            .replace( ' 11=OrderID ', ' 11=' + clientOrderID + ' ' ) \
            .replace( ' 54=SIDE ', ' 54=' + str(side) + ' ' ) \
            .replace( ' SYMBOLGROUP ', ' 55=' + symbol_list[0] + ' ' ) \
            .replace( ' 790=REQID ', ' 790=status_' + str(random.randint(10000, 99999)) + ' ' ) \
            .replace( ' END', '' ) #remove last space
        )
    try :
        log( "send: [" + out_msg.replace('\x01',' ') + ']' )
        try :
            bytes_out = sock.write( out_msg )
            pass
        except socket.error as e :
            log( 'do_newlimitorder_request_response send error: ' + repr(e) )
            raise
        response_received = None
        reject_received = None
        try :
            while not (response_received or reject_received):
                data_in = sock.read(4096)
                if not data_in :
                    log("socket closed by remote side")
                    break
                for i in split_fix_msgs(data_in) :
                    log( "recv: [" + i.replace('\x01',' ') + ']' )
                    if re.search('\x0135=[3j]\x01',i) :
                        reject_received = True
                        pass
                    if re.search('\x0135=8\x01.*\x0139=8\x01',i) :
                        reject_received = True
                        pass
                    elif re.search('\x0135=8\x01',i) :
                        response_received = True
                        pass
        except socket.timeout :
            log("no response to request")
        except socket.error as e :
            log( 'error: socket error: ' + repr(e) )
            raise

        if response_received :
            log("Execution Report received")
        elif reject_received :
            log("order reject received")
            raise
        else :
            log("NO RESPONSE RECEIVED")

        pass

    except :
        return False

    return True


def do_general_request_response( sock, msg_template, msgseqnum, message ) :

    out_msg = gen_general_msg( msg_template, msgseqnum, message )
    try :
        log( "send: [" + out_msg.replace('\x01',' ') + ']' )
        try :
            bytes_out = sock.write( out_msg )
            pass
        except socket.error as e :
            log( 'do_general_request_response send error: ' + repr(e) )
            raise
        response_received = None
        try :
            while not response_received :
                data_in = sock.read(4096)
                if not data_in :
                    log("socket closed by remote side")
                    break
                for i in split_fix_msgs(data_in) :
                    log( "recv: [" + i.replace('\x01',' ') + ']' )
                    response_received = True
                    pass
        except socket.timeout :
            log("no response to request")
        except socket.error as e :
            log( 'error: socket error: ' + repr(e) )
            #raise
            #cannot raise exception here, in case no response expected...

        if response_received :
            log("response received")
        else :
            log("NO RESPONSE RECEIVED")

        pass

    except :
        return False

    return True

#
# logout utility method
#
def gen_logout_msg( msg_template, msgseqnum ) :
    _BODY_FIELDS = ' '

    out_msg = msg_template \
        .replace( ' 35=MSGTYPE ',   ' 35=5 '                       ) \
        .replace( ' 34=MSGSEQNUM ', ' 34=' + repr(msgseqnum) + ' ' ) \
        .replace( ' BODY_FIELDS ',  _BODY_FIELDS                   )

    return format_fix_msg( out_msg.replace(' ','\x01') )

#
# logout processing
#
def do_logout_sequence( sock, msg_template, msgseqnum ) :

    out_msg = gen_logout_msg( msg_template, msgseqnum )

    try :
        log( "send: [" + out_msg.replace('\x01',' ') + ']' )

        try :
            bytes_out = sock.write( out_msg )
            pass
        except socket.error as e :
            log( 'do_logout_sequence send error: ' + repr(e) )
            raise

        logout_received = None

        try :
            while not logout_received :
                data_in = sock.read(4096)
                if not data_in :
                    log("socket closed by remote side")
                    break

                for i in split_fix_msgs( data_in ) :
                    log( "recv: [" + i.replace('\x01',' ') + ']' )
                    if re.search('\x0135=5\x01', i) :
                        log( "logout received" )
                        logout_received = True
                        pass
        except socket.timeout :
            log("timeout encountered")
        except socket.error as e :
            log( 'do_logout_sequence error: socket error: ' + repr(e) )
            raise

        if logout_received :
            log( 'logout successful' )
        else :
            log( 'no logout response received' )
            return False
        pass

    except :
        return False

    return True


if len( sys.argv ) == 1 :
    print 'Usage: fixs2servercheck.py -u username -p password -H host -P port'
    print '        [-l] [-Z] [-S] [-C cipher] [-B BeginString] [-T TargetSubID]'
    print '        [-I HeartBtInt] [-U]'
    print '        [[mode-options]]'
    print '    mode-options:'
    print '        [-s symbols] [-r nummsgs] [-R MDReqID]'
    print '        [-o orderSide] [-a account]'
    print '        [-m fix-message-body]'
    print '  -l check for login only'
    print '  -Z specifies zabbix mode (no logging, \'0\'/\'1\' output)'
    print '  -S indicates use SSL socket'
    print '  -C defaults to "HIGH+SHA+AES" for fixs2 (-S required)'
    print '  -B defaults to "FIX.4.2"'
    print '  -I defaults to 300 (seconds)'
    print '  -U requests microsecond UTC timestamp on log lines'
    print '  -s symbols to request market data snapshot on'
    print '  -r incremental refresh mode, number of 35=X messages to wait for'
    print '      (default 1000, requires -s)'
    print '  -R MDReqID to use for 35=V'
    print '  -o 1 for a buy, 2 for sell. Generates 35=D (NewOrder) message'
    print '  -a Account to use for 35=D'
    print '  -m requests a general freeform FIX message (must include 35=? in front)'
    sys.exit(0)
    pass

opt_error = False

try :
    opts, args = getopt.getopt( sys.argv[1:], "u:p:H:P:lZSC:B:T:I:Us:r:R:o:a:L:m:" )

    for o, a in opts :
        if o == "-l" :
            opt_logincheck = True
            pass
        if o == "-u" :
            opt_username = a
            pass
        if o == "-p" :
            opt_password = a
            pass
        if o == "-H" :
            opt_host = a
            pass
        if o == "-P" :
            try :
                opt_port = int(a)
            except ValueError as e :
                print 'invalid port value'
                opt_error = True
                pass
            pass
        if o == "-Z" :
            opt_zabbix_mode = True
            pass
        if o == '-S' :
            opt_ssl = True
            pass
        if o == '-C' :
            opt_cipher = a
            pass
        if o == '-B' :
            opt_beginstring = a
            pass
        if o == '-T' :
            opt_targetsubid = a
            pass
        if o == '-I' :
            try :
                opt_heartbtint = int(a)
            except ValueError as e :
                print 'invalid heart beat interval value'
                opt_error = True
                pass
            if opt_heartbtint <= 0 :
                print 'invalid heart beat interval value'
                opt_error = True
                pass
            pass
        if o == "-U" :
            opt_utctimestamp = True
            pass
        if o == "-s" :
            opt_symbol = a
            pass
        if o == "-r" :
            try :
                opt_refresh = int(a)
            except ValueError as e :
                print 'invalid refresh message count'
                opt_error = True
                pass
            if opt_refresh <= 0 :
                print 'invalid refresh message count'
                opt_error = True
                pass
            pass
        if o == "-R" :
            opt_mdreqid = a
            pass
        if o == "-o" :
            opt_side = a
            random.seed()
            pass
        if o == "-a" :
            opt_account = a
            pass
        if o == "-L" :
            opt_limit = a
            pass
        if o == "-m" :
            opt_message = a
            pass

        pass #for

    if not opt_username :
        print 'username required'
        opt_error = True
        pass
    if not opt_password :
        print 'password required'
        opt_error = True
        pass
    if not opt_host :
        print 'hostname required'
        opt_error = True
        pass
    if opt_port == 0 :
        print 'port number required'
        opt_error = True
        pass
    if opt_cipher and not opt_ssl :
        print 'use of -C cipher requires -S'
        opt_error = True
        pass
    if opt_refresh and not opt_symbol :
        print 'use of -r refresh mode requires -s'
        opt_error = True
        pass
    if opt_symbol :
        opt_symbol_parsed = opt_symbol.translate(SYMBOL_SPLIT_TRANS).split()
        if 0 == len(opt_symbol_parsed) :
            print 'invalid -s symbols'
            opt_error = True
            pass
        pass
    if opt_error :
        sys.exit(1)
        pass

except getopt.GetoptError as e :
    print e
    sys.exit(1)

if opt_ssl and not opt_cipher :
    opt_cipher = 'HIGH+SHA+AES'
    pass


try :

    msg_outseqnum = 1

    msg_template = gen_message_template( opt_beginstring, opt_username, opt_targetsubid )
    #log( 'message template: ' + msg_template )

    sock = do_sock_create_connect( opt_host, opt_port, opt_ssl, opt_cipher )

    if not do_logon_news_sequence( sock, msg_template, opt_password, opt_heartbtint ) :
        log( 'logon failed' )
        zabbixcode(-1)
        sys.exit(1)
        pass
    msg_outseqnum += 1

    for test_run in range (0, opt_refresh):

        limit_orderid = 'test_limit_' + str(random.randint(10000, 99999))
        change_orderid = 'test_change_' + str(random.randint(10000, 99999))
        cancel_orderid = 'test_cancel_' + str(random.randint(10000, 99999))
        open_orderid = 'test_open_' + str(random.randint(10000, 99999))
        close_orderid = 'test_close_' + str(random.randint(10000, 99999))

        #place order that will not fill
#        if not do_newlimitorder_request_response( sock, msg_template, msg_outseqnum, opt_symbol_parsed, opt_side, opt_account, opt_limit, limit_orderid ) :
#            # New order is expected to execute.  Anything else is considered a failure.
#            log( 'neworder message failed' )
#            zabbixcode(0)
#            sys.exit(1)
#            pass
#        msg_outseqnum += 1

        #change order
#        if not do_changeorder_request_response( sock, msg_template, msg_outseqnum, opt_symbol_parsed, opt_side, opt_account, opt_limit, limit_orderid, change_orderid ) :
#            # New order is expected to execute.  Anything else is considered a failure.
#            log( 'neworder message failed' )
#            zabbixcode(0)
#            sys.exit(1)
#            pass
#        msg_outseqnum += 1

        #cancel order
#        if not do_cancelorder_request_response( sock, msg_template, msg_outseqnum, opt_symbol_parsed, opt_side, opt_account, change_orderid, cancel_orderid ) :
#            # New order is expected to execute.  Anything else is considered a failure.
#            log( 'neworder message failed' )
#            zabbixcode(0)
#            sys.exit(1)
#            pass
#        msg_outseqnum += 1

        #place order that will trade
        if not do_neworder_request_response( sock, msg_template, msg_outseqnum, opt_symbol_parsed, 1, opt_account, open_orderid ) :
            # New order is expected to execute.  Anything else is considered a failure.
            log( 'neworder message failed' )
            zabbixcode(0)
            sys.exit(1)
            pass
        msg_outseqnum += 1

        #get status of order
        if not do_status_request_response( sock, msg_template, msg_outseqnum, opt_symbol_parsed, 1, open_orderid ) :
            # New order is expected to execute.  Anything else is considered a failure.
            log( 'neworder message failed' )
            zabbixcode(0)
            sys.exit(1)
            pass
        msg_outseqnum += 1

        #offset previous fill
        if not do_neworder_request_response( sock, msg_template, msg_outseqnum, opt_symbol_parsed, 2, opt_account, close_orderid ) :
            # New order is expected to execute.  Anything else is considered a failure.
            log( 'neworder message failed' )
            zabbixcode(0)
            sys.exit(1)
            pass
        msg_outseqnum += 1

        #get snapshot
        try :
            sent_message_count = do_snapshot_request_response( sock, msg_template, msg_outseqnum, opt_symbol_parsed, opt_mdreqid )
            msg_outseqnum += sent_message_count
            pass
        except Exception as e :
            log( repr(e) )
            zabbixcode(0)
            sys.exit(1)
            pass

    if not do_logout_sequence( sock, msg_template, msg_outseqnum ) :
        log( 'logout failed (non-fatal)' )
        pass

except Exception as e:
    log( 'exception: ' + repr(e) )
    zabbixcode(0)
    sys.exit(1)

zabbixcode(1)
sys.exit(0)
