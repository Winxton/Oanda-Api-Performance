import socket
import sys
import calendar
import pytz
import csv

from datetime import datetime

TCP_IP = "fxserver02.oanda.com"
TCP_PORT = 9600
BUFFER_SIZE = 1024
TIMEOUT = 60
PIPS = 5

def connect_to_compact_stream():
    tick_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tick_socket.connect((TCP_IP,TCP_PORT))
    except Exception as e:
        print "Caught exception when connecting to compact stream\n" + str(e)
    tick_socket.settimeout(TIMEOUT)

    # Skip header
    tick_socket.recv(BUFFER_SIZE)
    return tick_socket

# Decode ticks (protobuf binary)
def decode_streaming_data(streaming_data):
    # Heartbeat
    if len(streaming_data) == 9:
        return "heartbeat"
    # Heartbeat + Tick
    elif len(streaming_data) == 19:
        return decode_streaming_data(streaming_data[0:10])
    # Tick
    else:
        # The data is in binary format and stored in little-endian byte order
        # To decode it, first convert it into hex
        # E.g. 09211978831058ff2600
        streaming_data_in_hex_endian = streaming_data.encode('hex')
        # Group each byte(two hex digit) togerther and form a list
        # Reverse the list to get rid of little-endian byte order
        # E.g. 00 26 ff 58 10 83 78 19 21 09
        streaming_data_in_hex = reversed([streaming_data_in_hex_endian[i:i+2] for i in range(0, len(streaming_data_in_hex_endian), 2)])
        # Convert each byte(two hex digit) into binary, and fill the leading zeros to get 8 bits for each byte
        # E.g. 00 -> 00000000; 26 -> 00100110
        # Merge the list back to a string
        streaming_data_in_binary = ''.join(bin(eight_bits)[2:].zfill(8) for eight_bits in (int(byte_in_hex, 16) for byte_in_hex in (streaming_data_in_hex)))

        return streaming_data_in_binary

def fetch(binary):
    sec_binary = binary[11:22]
    # Get the current server time(UTC), convert into binary, and remove the last 11 bits
    # Concat with the sec_binary above
    server_ts_utc = calendar.timegm(datetime.utcnow().utctimetuple())
    timestamp = int(bin(server_ts_utc)[2:-11] + sec_binary, 2)
    millisec = int(binary[22:32], 2)
    timestamp += millisec/1000.0

    bid = int(binary[32:53], 2)
    # bid * 10^(-pips) to get the actual bid(with decimal)
    bid = float(bid * pow(10, - PIPS))

    spread = int(binary[53:63], 2)
    # spread * 10^(-pips) to get the actual spread(with decimal)
    spread = float(spread * pow(10, - PIPS))

    # Calculate ask
    ask = bid + spread
    return timestamp, millisec, bid, ask

def latency_test(tick_count):
    open('CompactStream_Performance_Report.csv', 'w').close()
    counter = 0
    tick_socket = connect_to_compact_stream()
    # EUR_USD
    tick_socket.send("+1\r\n")
    # First tick is always a heartbeat
    streaming_data = tick_socket.recv(BUFFER_SIZE)

    with open('streamresults/CompactStream_Performance_Report.csv', 'a') as csvfile:
        reportwriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        reportwriter.writerow(["Compact Stream Performance Test"])
        reportwriter.writerow(["Timestamp on Tick", "Latency After Decode", "Bid", "Ask"])
        while float(tick_count) > counter:
            tick_socket.send("h\r\n");
            streaming_data = tick_socket.recv(BUFFER_SIZE)
            if not streaming_data:
                continue
            decoded_binary_data = decode_streaming_data(streaming_data)
            after_decode = float(datetime.now(pytz.utc).strftime("%f"))/1000

            if not "heartbeat" == decoded_binary_data:
                tick_ts, tick_millisec, tick_bid, tick_ask = fetch(decoded_binary_data)
                diff_after_decode = after_decode - tick_millisec if after_decode > tick_millisec else 1000 + after_decode - tick_millisec
                counter += 1
                print "%.3f" % tick_ts
                print "%.3f" % diff_after_decode
                reportwriter.writerow(["%0.3f" % tick_ts, "%0.3f" % diff_after_decode, tick_bid, tick_ask])

def main():
    if 2 < len(sys.argv):
        sys.exit("incorrect number of arguments")
    tick_count = sys.argv[1] if 2 == len(sys.argv) else float("inf")
    if tick_count <= 0:
        sys.exit("invalid value of number of ticks")
    else:
        latency_test(tick_count)
    sys.exit("Work Complete")

if __name__ == '__main__':
    main()