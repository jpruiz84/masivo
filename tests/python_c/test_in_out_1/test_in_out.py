from __future__ import absolute_import, print_function
import numpy as np
import pyopencl as cl
import time
import pyopencl.array as cl_array
import sys
sys.path.append('../../..')
import globalConstants
import random
import ctypes

STOPS_NUM = 30
STOP_MAX_PASS = 10000
SIM_TIME = 600
PRINT_LIST = False

USE_PYTHON = 0
USE_PYOPENCL = 1
USE_PYTHON_C = 0


SPL_TYPE = np.dtype((globalConstants.PASS_TYPE, (STOP_MAX_PASS)))
SPSL_TYPE = np.dtype([('stop_num', 'u2'), ('total', 'u4'), ('last_empty', 'u4'), ('w_index', 'u4'), ('spl', SPL_TYPE)])

pass_list = np.zeros(STOPS_NUM, SPSL_TYPE)
pass_arrival_list = np.zeros(STOPS_NUM, SPSL_TYPE)

# Fill stops_list_np with pass unique id
stop_num = 0
pass_id = 0
for i in range(STOPS_NUM):
  print("Generating stop: %d" % i)
  for j in range(STOP_MAX_PASS):
    pass_arrival_list[i]['spl'][j]['pass_id'] = pass_id
    pass_arrival_list[i]['spl'][j]['orig_stop'] = stop_num
    pass_arrival_list[i]['spl'][j]['dest_stop'] = STOPS_NUM - 1
    pass_arrival_list[i]['spl'][j]['arrival_time'] = random.randint(0, globalConstants.PASS_TOTAL_ARRIVAL_TIME)
    pass_arrival_list[i]['spl'][j]['status'] = globalConstants.PASS_STATUS_TO_ARRIVE
    pass_arrival_list[i]['total'] += 1
    pass_arrival_list[i]['last_empty'] += 1
    pass_id += 1
  stop_num += 1

for i in range(len(pass_arrival_list)):
  pass_arrival_list[i]['spl'].sort(order='arrival_time')

pass_list_py = np.copy(pass_list)
pass_arrival_list_py = np.copy(pass_arrival_list)

if PRINT_LIST:
  print("\n Original pass_arrival_list")
  print(pass_arrival_list)
  print("\n Original pass_list")
  print(pass_list)


if USE_PYOPENCL:
  print('load program from cl source file')
  f = open('kernels_struct.c', 'r', encoding='utf-8')
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

  pass_list_g = cl_array.to_device(queue, pass_list)
  pass_arrival_list_g = cl_array.to_device(queue, pass_arrival_list)
  np_stops_num = np.uint32(STOPS_NUM)

  total_start_time = time.time()
  for sim_time in range(0, SIM_TIME):
    np_sim_time = np.uint32(sim_time)
    evt = prg.move_pass(queue, (np_stops_num, ), (np_stops_num, ), pass_list_g.data,
                        pass_arrival_list_g.data, np_stops_num, np_sim_time)
    evt.wait()

  total_end_time = time.time()

  if PRINT_LIST:
    print("\npass_arrival_list_g:")
    print(pass_arrival_list_g)
    print("\npass_list_g:")
    print(pass_list_g)

  print('\n\nFinal pass list')
  for i in range(STOPS_NUM):
    print("Total pass list(%d): %d" % (i, np.array(pass_list_g[i].get(), dtype=SPSL_TYPE)['total']))

  print("\nPyopencl process time: %s ms\n\n" % ((total_end_time - total_start_time)*1000))


if USE_PYTHON:

  startTime = time.time()

  for sim_time in range(0, SIM_TIME):
    for i in range(STOPS_NUM):
      if pass_arrival_list[i]['total'] > 0:
        while True:
          if pass_arrival_list[i]['w_index'] >= len(pass_arrival_list[i]['spl']):
            break

          # Check pass status
          if pass_arrival_list[i]['spl'][pass_arrival_list[i]['w_index']]['status'] \
              != globalConstants.PASS_STATUS_TO_ARRIVE:
            break

          if sim_time < pass_arrival_list[i]['spl'][pass_arrival_list[i]['w_index']]['arrival_time']:
            break

          pass_list[i]['spl'][pass_list[i]['last_empty']] = \
            np.copy(pass_arrival_list[i]['spl'][pass_arrival_list[i]['w_index']])
          pass_list[i]['spl'][pass_list[i]['last_empty']]['status'] = globalConstants.PASS_STATUS_ARRIVED
          pass_list[i]['last_empty'] += 1
          pass_list[i]['total'] += 1

          pass_arrival_list[i]['spl'][pass_arrival_list[i]['w_index']]['status'] = \
            globalConstants.PASS_STATUS_EMPTY

          pass_arrival_list[i]['last_empty'] -= 1
          pass_arrival_list[i]['total'] -= 1
          pass_arrival_list[i]['w_index'] += 1

  endTime = time.time()

  if PRINT_LIST:
    print("\npass_arrival_list:")
    print(pass_arrival_list)
    print("\npass_list:")
    print(pass_list)


  print('\n\nFinal pass list')
  for i in range(STOPS_NUM):
    print("Total pass list(%d): %d" % (i, pass_list[i]['total']))

  print("\nPython process time: %s ms" % ((endTime - startTime)*1000))


if USE_PYTHON_C:

  # Compile the C code with: gcc -shared -Wl,-soname,move_pass -o move_pass.so -fPIC move_pass.c

  # load the shared object file
  move_pass = ctypes.CDLL('./move_pass.so')
  move_pass.move_pass.argtypes = (np.ctypeslib.ndpointer(dtype=SPSL_TYPE), np.ctypeslib.ndpointer(), ctypes.c_uint32, ctypes.c_uint32)


  startTime = time.time()
  for sim_time in range(0, SIM_TIME):
    move_pass.move_pass(pass_list, pass_arrival_list, STOPS_NUM, sim_time)
  endTime = time.time()

  if PRINT_LIST:
    print("\nPost pass_arrival_list:")
    print(pass_arrival_list)
    print("\nPost pass_list:")
    print(pass_list)

  print('\n\nFinal pass list')
  for i in range(STOPS_NUM):
    print("Total pass list(%d): %d" % (i, pass_list[i]['total']))

  print("\nPythonC process time: %s ms" % ((endTime - startTime)*1000))