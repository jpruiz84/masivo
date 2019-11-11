#!/bin/bash

# Setting max performance
N_THREADS="$(nproc --all)"
echo "Total threads: $N_THREADS"

for ((i=0; i<=N_THREADS -1; i++)); do
   echo performance > /sys/devices/system/cpu/cpu$i/cpufreq/scaling_governor
done

cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
