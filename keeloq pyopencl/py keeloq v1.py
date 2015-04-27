# example provided by Roger Pau Monn'e

from __future__ import print_function
import pyopencl as cl
import numpy
import numpy.linalg as la
import datetime
from time import time

def bit(x,n):
				y=(((x)>>(n))&1)
				return y
def g5(x,a,b,c,d,e):
				y=(bit(x,a)+bit(x,b)*2+bit(x,c)*4+bit(x,d)*8+bit(x,e)*16)
				return y
hexarr=numpy.vectorize(hex) 
#2^22 |4.3 2.15344 s 1.07673 s 0.538382 s 0.269213 s 0.134616 s 0.134616 s
#4.52955 s 4.5461 s
KeeLoq_NLF=0x3A5C742E
offset=0
data_points = 2**15 # ~8 million data points, ~32 MB data
workers = 2**8 # 256 workers, play with this to see performance differences
			   # eg: 2**0 => 1 worker will be non-parallel execution on gpu
			   # data points must be a multiple of workers

key = numpy.arange(offset,data_points+offset,1).astype(numpy.uint64)
ciph = numpy.arange(offset,data_points+offset,1).astype(numpy.uint32)
plain_result = numpy.empty_like(ciph)

print (ciph)

temp=ciph

# Speed in normal CPU usage
time1 = time()

r=0
while r<528:
				temp = (temp<<1)^bit(temp,31)^bit(temp,15)^bit(key,(15-r)&63)^bit(KeeLoq_NLF,g5(temp,0,8,19,25,30))
				r=r+1
			   
plain_result=temp&0xFFFFFFFF

time2 = time()

temp=ciph

# Speed in normal CPU usage


r=0
while r<528:
				temp = (temp<<1)
				temp=temp^bit(temp,31)
				temp=temp^bit(temp,15)
				temp=temp^bit(key,(15-r)&63)
				temp=temp^bit(KeeLoq_NLF,g5(temp,0,8,19,25,30))
				r=r+1
			   
plain_result=temp&0xFFFFFFFF

time3 = time()

print (key)
print (plain_result)
print("Execution time of test 1: ", time2 - time1, "s")
print("Execution time of test 1: ", time3 - time2, "s")