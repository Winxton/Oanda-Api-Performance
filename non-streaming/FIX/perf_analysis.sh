#!/bin/bash

cmd=cat
awk=mawk

if [ X$2 == "Xtail" ]; then
  cmd="tail -F"
fi

# 35=D
# arg1 is file to follow
(($cmd $1 | \
 grep "35=D" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=D[^O]*49=\([A-Za-z_0-9]*\).*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*11=\(test_limit_[0-9a-zA-Z\_\-]*\).*60=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*/request \1 \3-\4 \2 \5 \6-\7/g' |grep "^request"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
} 

/^request.*/ {
  print "REQUEST: "$5 " " timesec($2) $1
   
}'); ($cmd $1 | \
 grep "35=8" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=8[^O]*49=OANDA.*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*56=\([A-Za-z_0-9]*\).*11=\(test_limit_[0-9a-zA-Z\_\-]*\).*60=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*/response \1 \2-\3 \4 \5 \6-\7/g' | grep "^response"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
}

/^response.*/ {
  print "RESPONSE: "$5 " " timesec($2) $1
}')) | \
awk 'BEGIN {print "Limit orders:"} \
/REQUEST/ { request[$2]=$3; }
/RESPONSE/{ response[$2]=$3; }
END {for (a in request){ diff=response[a]-request[a];if (diff) printf("Limit,%s,%s\n", a, diff);} }'

# 35=D
# arg1 is file to follow
(($cmd $1 | \
 grep "35=D" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=D[^O]*49=\([A-Za-z_0-9]*\).*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*11=\(test_open_[0-9a-zA-Z\_\-]*\).*60=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*/request \1 \3-\4 \2 \5 \6-\7/g' |grep "^request"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
} 

/^request.*/ {
  print "REQUEST: "$5 " " timesec($2) $1
   
}'); ($cmd $1 | \
 grep "35=8" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=8[^O]*49=OANDA.*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*56=\([A-Za-z_0-9]*\).*11=\(test_open_[0-9a-zA-Z\_\-]*\).*17=T.*60=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*/response \1 \2-\3 \4 \5 \6-\7/g' | grep "^response"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
}

/^response.*/ {
  print "RESPONSE: "$5 " " timesec($2) $1
}')) | \
awk 'BEGIN {print "Open orders:"} \
/REQUEST/ { request[$2]=$3; }
/RESPONSE/{ response[$2]=$3; }
END {for (a in request){ diff=response[a]-request[a];if (diff) printf("Open,%s,%s\n", a, diff);} }'

# 35=D
# arg1 is file to follow
(($cmd $1 | \
 grep "35=D" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=D[^O]*49=\([A-Za-z_0-9]*\).*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*11=\(test_close_[0-9a-zA-Z\_\-]*\).*60=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*/request \1 \3-\4 \2 \5 \6-\7/g' |grep "^request"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
} 

/^request.*/ {
  print "REQUEST: "$5 " " timesec($2) $1
   
}'); ($cmd $1 | \
 grep "35=8" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=8[^O]*49=OANDA.*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*56=\([A-Za-z_0-9]*\).*11=\(test_close_[0-9a-zA-Z\_\-]*\).*60=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*/response \1 \2-\3 \4 \5 \6-\7/g' | grep "^response"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
}

/^response.*/ {
  print "RESPONSE: "$5 " " timesec($2) $1
}')) | \
awk 'BEGIN {print "Close orders:"} \
/REQUEST/ { request[$2]=$3; }
/RESPONSE/{ response[$2]=$3; }
END {for (a in request){ diff=response[a]-request[a];if (diff) printf("Close,%s,%s\n", a, diff);} }'

# 35=G
# arg1 is file to follow
(($cmd $1 | \
 grep "35=G" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=G[^O]*49=\([A-Za-z_0-9]*\).*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*11=\([0-9a-zA-Z\_\-]*\).*60=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*/request \1 \3-\4 \2 \5 \6-\7/g' |grep "^request"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
} 

/^request.*/ {
  print "REQUEST: "$5 " " timesec($2) $1
   
}'); ($cmd $1 | \
 grep "35=8" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=8[^O]*49=OANDA.*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*56=\([A-Za-z_0-9]*\).*11=\([0-9a-zA-Z\_\-]*\).*60=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*/response \1 \2-\3 \4 \5 \6-\7/g' | grep "^response"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
}

/^response.*/ {
  print "RESPONSE: "$5 " " timesec($2) $1
}')) | \
awk 'BEGIN {print "Changed orders:"} \
/REQUEST/ { request[$2]=$3; }
/RESPONSE/{ response[$2]=$3; }
END {for (a in request){ diff=response[a]-request[a];if (diff) printf("Change,%s,%s\n", a, diff);} }'

# 35=F
# arg1 is file to follow
(($cmd $1 | \
 grep "35=F" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=F[^O]*49=\([A-Za-z_0-9]*\).*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*11=\([0-9a-zA-Z\_\-]*\).*60=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*/request \1 \3-\4 \2 \5 \6-\7/g' |grep "^request"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
} 

/^request.*/ {
  print "REQUEST: "$5 " " timesec($2) $1
   
}'); ($cmd $1 | \
 grep "35=8" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=8[^O]*49=OANDA.*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*56=\([A-Za-z_0-9]*\).*11=\([0-9a-zA-Z\_\-]*\).*60=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*/response \1 \2-\3 \4 \5 \6-\7/g' | grep "^response"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
}

/^response.*/ {
  print "RESPONSE: "$5 " " timesec($2) $1
}')) | \
awk 'BEGIN {print "Cancelled orders:"} \
/REQUEST/ { request[$2]=$3; }
/RESPONSE/{ response[$2]=$3; }
END {for (a in request){ diff=response[a]-request[a];if (diff) printf("Cancel,%s,%s\n", a, diff);} }'

# 35=H
# arg1 is file to follow
(($cmd $1 | \
 grep "35=H" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=H[^O]*49=\([A-Za-z_0-9]*\).*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*790=\([0-9a-zA-Z\_\-]*\).*/request \1 \3-\4 \2 \5/g' |grep "^request"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
} 

/^request.*/ {
  print "REQUEST: "$5 " " timesec($2) $1
   
}'); ($cmd $1 | \
 grep "35=8" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=8[^O]*49=OANDA.*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*56=\([A-Za-z_0-9]*\).*790=\([0-9a-zA-Z\_\-]*\).*/response \1 \2-\3 \4 \5/g' | grep "^response"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
}

/^response.*/ {
  print "RESPONSE: "$5 " " timesec($2) $1
}')) | \
awk 'BEGIN {print "Status request:"} \
/REQUEST/ { request[$2]=$3; }
/RESPONSE/{ response[$2]=$3; }
END {for (a in request){ diff=response[a]-request[a];if (diff) printf("Status,%s,%s\n", a, diff);} }'

# 35=V
# arg1 is file to follow
(($cmd $1 | \
 grep "35=V" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=V[^O]*49=\([A-Za-z_0-9]*\).*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*262=\([0-9a-zA-Z\_\-]*\).*/request \1 \3-\4 \2 \5/g' |grep "^request"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
} 

/^request.*/ {
  print "REQUEST: "$5 " " timesec($2) $1
   
}'); ($cmd $1 | \
 grep "35=W" | \
 sed -e 's/^[0-9]*-\([0-9]*:[0-9]*:[0-9]*.[0-9]*\)[^X]*FIX[^X]*35=W[^O]*49=OANDA.*52=\(........\)-\([0-9]*:[0-9]*:[0-9]*\).*56=\([A-Za-z_0-9]*\).*262=\([0-9a-zA-Z\_\-]*\).*/response \1 \2-\3 \4 \5/g' | grep "^response"| \
 $awk 'function timesec(str) {
  split(str,arr1,"."); 
  split(arr1[1],arr2,/:/); 
  sum = 0;
  for (i in arr2) { sum = sum*60 + arr2[i]; }
  sum = arr2[3]*1000000 + arr1[2];
  return sum;
}

/^response.*/ {
  print "RESPONSE: "$5 " " timesec($2) $1
}')) | \
awk 'BEGIN {print "Status request:"} \
/REQUEST/ { request[$2]=$3; }
/RESPONSE/{ response[$2]=$3; }
END {for (a in request){ diff=response[a]-request[a];if (diff) printf("Rate,%s,%s\n", a, diff);} }'
