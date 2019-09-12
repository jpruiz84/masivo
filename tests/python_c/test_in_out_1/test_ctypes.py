import ctypes
import numpy as np

# Compile the C code with: gcc -shared -Wl,-soname,test_ctypes -o test_ctypes.so -fPIC test_ctypes.c

# load the shared object file
move_pass = ctypes.CDLL('./test_ctypes.so')
move_pass.sum.argtypes = (ctypes.c_int, np.ctypeslib.ndpointer(dtype=np.int32))

numbers = np.arange(0, 10, 1, np.int32)
print(numbers)

num_numbers = len(numbers)

result = move_pass.sum(len(numbers), numbers)

print("resutl %d" % result)
print(numbers)