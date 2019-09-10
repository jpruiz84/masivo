#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import numpy as np
import pyopencl as cl
import time
import pyopencl.array as cl_array
import sys
sys.path.append('../..')
import globalConstants
import random

STOPS_NUM = 300
PASS_PER_STOP = 10000
SIM_TIME = 2000

stop_type = np.dtype((globalConstants.PASS_TYPE, (PASS_PER_STOP)))
stops_list_np = np.zeros(STOPS_NUM, dtype = stop_type)
stops_list_out_np  = np.zeros(STOPS_NUM, dtype = stop_type)
stops_list_out_py  = np.zeros(STOPS_NUM, dtype = stop_type)

print(stops_list_np.nbytes)

# Fill stops_list_np with pass unique id
stop_num = 0
pass_id = 0
for i in range(0, stops_list_np.shape[0]):
  for j in range(0, stops_list_np.shape[1]):
    stops_list_np[i][j]['pass_id'] = pass_id
    stops_list_np[i][j]['orig_stop'] = stop_num
    stops_list_np[i][j]['dest_stop'] = STOPS_NUM - 1
    stops_list_np[i][j]['arrival_time'] = random.randint(0, globalConstants.PASS_TOTAL_ARRIVAL_TIME)
    stops_list_np[i][j]['status'] = globalConstants.PASS_STATUS_TO_ARRIVE

    pass_id += 1
  stop_num += 1

for i in range(len(stops_list_np)):
  stops_list_np[i] = np.sort(stops_list_np[i], order='arrival_time')


print(stops_list_np)

print('load program from cl source file')
f = open('kernels.cl', 'r', encoding='utf-8')
kernels = ''.join(f.readlines())
f.close()


ocl_platforms = (platform.name
                 for platform in cl.get_platforms())
print("\n".join(ocl_platforms))

nvidia_platform = [platform
                   for platform in cl.get_platforms()
                   if platform.name == "NVIDIA CUDA"][0]

nvidia_devices = nvidia_platform.get_devices()

ctx = cl.Context(devices=nvidia_devices)
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags


prg = cl.Program(ctx, kernels).build()

startTime = time.time()
stops_list_g = cl_array.to_device(queue, stops_list_np)

np_stops_num = np.uint32(STOPS_NUM)
np_pass_per_stop = np.uint32(PASS_PER_STOP)
np_sim_time = np.uint32(SIM_TIME)

evt = prg.move_pass2(queue, (np_stops_num,), None,
                    stops_list_g.data, np_stops_num, np_pass_per_stop, np_sim_time)

evt.wait()
endTime = time.time()

print(stops_list_g)

print("\nPyopencl process time: %s ms\n\n" % ((endTime - startTime)*1000))

stops_list_py = np.copy(stops_list_np)
startTime = time.time()
for i in range(len(stops_list_py)):
  for j in range(len(stops_list_py[i])):
    if stops_list_py[i][j]['arrival_time'] > SIM_TIME:
      stops_list_py[i][j]['status'] = 1
endTime = time.time()

print(stops_list_py)
print("\nPython process time: %s ms" % ((endTime - startTime)*1000))


