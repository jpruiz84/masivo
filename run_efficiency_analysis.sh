#!/bin/bash
rm -fr results*/

for i in {0..8}
do
   echo "******** RUNNING LIMITED TO:  $i CU"
   python3 main.py -m $i
   mv results results_$i
done


