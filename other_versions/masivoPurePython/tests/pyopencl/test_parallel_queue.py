#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import numpy as np
import pyopencl as cl
import time
import pyopencl.array as cl_array
STOPS_NUM = 300
PASS_PER_STOP = 1000




pass_np = np.arange(PASS_PER_STOP).astype(np.uint32)
stop_type = np.dtype(('u4', (PASS_PER_STOP)))
stops_list_np  = np.zeros(STOPS_NUM, dtype = stop_type)
stops_list_out_np  = np.zeros(STOPS_NUM, dtype = stop_type)
stops_list_out_py  = np.zeros(STOPS_NUM, dtype = stop_type)

print(stops_list_np.nbytes)


# Fill stops_list_np with pass unique id
stop_num = 0
for i in range(0, stops_list_np.shape[0]):
  pass_num = 0
  for j in range(0, stops_list_np.shape[1]):
    stops_list_np[i][j] = pass_num + stop_num
    pass_num +=1
  stop_num += 1000000

#print(stops_list_np)


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
stops_list_out_g = cl_array.to_device(queue, stops_list_out_np)
np_stops_num = np.int32(STOPS_NUM)
np_pass_per_stop = np.int32(PASS_PER_STOP)

evt = prg.move(queue, (np_stops_num,), None, stops_list_g.data, stops_list_out_g.data, np_stops_num, np_pass_per_stop)

evt.wait()
endTime = time.time()

print(stops_list_out_g)

print("Pyopencl process time: %s ms" % ((endTime - startTime)*1000))



startTime = time.time()
stop_num = 0
for i in range(0, stops_list_np.shape[0]):
  for j in range(0, stops_list_np.shape[1]):
    if(stops_list_np[i][j] % 1000000) > 10:
      stops_list_out_py[i][j] = stops_list_np[i][j]
endTime = time.time()

print(stops_list_out_py)
print("Python process time: %s ms" % ((endTime - startTime)*1000))
