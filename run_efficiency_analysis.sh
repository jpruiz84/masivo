#!/bin/bash

# Setting max performance
N_THREADS="$(nproc --all)"
echo "Total threads: $N_THREADS"

for ((i=0; i<=N_THREADS -1; i++)); do
   echo performance > /sys/devices/system/cpu/cpu$i/cpufreq/scaling_governor
done

cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Compile the c code
gcc -shared -Wl,-soname, -o c_code/masivo_c.so -fPIC c_code/masivo_c.c

rm -fr results*/

for ((i=0; i<=N_THREADS; i++)); do
   echo "******** RUNNING LIMITED TO:  $i CU"
   python3 main.py -m $i
   mv results results_$i
done


