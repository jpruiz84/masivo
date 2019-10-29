#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import numpy as np
import pyopencl as cl
import time

#COUNTER_MAX = 33554432
COUNTER_MAX = 1000000
COUNTER_NUM = 100



#counter_np = np.zeros(COUNTER_NUM).astype(np.uint32)
counter_np = np.arange(COUNTER_NUM).astype(np.uint32)

print(counter_np)


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
counter_g = cl.Buffer(ctx, mf.WRITE_ONLY | mf.COPY_HOST_PTR, hostbuf=counter_np)
prg.sum(queue, counter_np.shape, None, counter_g, np.uint32(COUNTER_MAX), np.uint32(COUNTER_NUM))
cl.enqueue_copy(queue, counter_np, counter_g)
endTime = time.time()



print(counter_np)
print("Pyopencl process time: %s ms" % ((endTime - startTime)*1000))

exit()



# Init the counters array
counter_py = np.arange(COUNTER_NUM)

startTime = time.time()
for i in range(0, len(counter_py)):
  for j in range(0, COUNTER_MAX):
    counter_py[i] += 1
endTime = time.time()
print("Python process time: %s ms" % ((endTime - startTime)*1000))
print(counter_py)