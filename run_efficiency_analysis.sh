#!/bin/bash

# Compile the c code
gcc -shared -Wl,-soname, -o c_code/masivo_c.so -fPIC c_code/masivo_c.c

rm -fr results*/

for i in {8..0}
do
   sleep 10
   echo "******** RUNNING LIMITED TO:  $i CU"
   python3 main.py -m $i
   mv results results_$i
done


