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

KeeLoq_NLF=0x3A5C742E
offset=0
data_points = 2**22 # ~8 million data points, ~32 MB data
workers = 2**8 # 256 workers, play with this to see performance differences
			   # eg: 2**0 => 1 worker will be non-parallel execution on gpu
			   # data points must be a multiple of workers

key = numpy.arange(offset,data_points+offset,1).astype(numpy.uint64)
ciph = numpy.arange(offset,data_points+offset,1).astype(numpy.uint32)
plain_result = numpy.empty_like(ciph)
temp=ciph
print (ciph)
# Speed in normal CPU usage
time1 = time()
'''
r=0
while r<528:
				temp = (temp<<1)^bit(temp,31)^bit(temp,15)^bit(key,(15-r)&63)^bit(KeeLoq_NLF,g5(temp,0,8,19,25,30))
				r=r+1
			   
plain_result=temp&0xFFFFFFFF
'''
time2 = time()

print (key)
print (plain_result)
print("Execution time of test without OpenCL: ", time2 - time1, "s")


for platform in cl.get_platforms():
	for device in platform.get_devices():
		'''
		print("===============================================================")
		print("Platform name:", platform.name)
		print("Platform profile:", platform.profile)
		print("Platform vendor:", platform.vendor)
		print("Platform version:", platform.version)
		'''
		print("---------------------------------------------------------------")
		print("Device name:", device.name)
		print("Device type:", cl.device_type.to_string(device.type))
		'''
		print("Device memory: ", device.global_mem_size//1024//1024, 'MB')
		print("Device max clock speed:", device.max_clock_frequency, 'MHz')
		print("Device compute units:", device.max_compute_units)
		print("Device max work group size:", device.max_work_group_size)
		print("Device max work item sizes:", device.max_work_item_sizes)
		'''
		# Keeloq speed test
		ctx = cl.Context([device])
		queue = cl.CommandQueue(ctx, 
				properties=cl.command_queue_properties.PROFILING_ENABLE)
		mf = cl.mem_flags
		key_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=key)
		ciph_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=ciph)
		dest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, ciph.nbytes)
		prg = cl.Program(ctx, """
			__kernel void sum(__global const unsigned long *key,
			__global const unsigned int *ciph, __global unsigned int *plain)
			{
						#define KeeLoq_NLF			  0x3A5C742E
						#define bit(x,n)				(((x)>>(n))&1)
						#define g5(x,a,b,c,d,e) (bit(x,a)+bit(x,b)*2+bit(x,c)*4+bit(x,d)*8+bit(x,e)*16)
						
						int gid = get_global_id(0);
						unsigned long key_temp;
						unsigned int ciph_temp;
						unsigned int plain_temp;
						unsigned int r;	  

						key_temp = key[gid]; // my a element (by global ref)
						ciph_temp = ciph[gid]; // my b element (by global ref)
			
						for (r = 0; r < 528; r++)
						{
						ciph_temp = (ciph_temp<<1)^bit(ciph_temp,31)^bit(ciph_temp,15)^bit(key_temp,(15-r)&63)^bit(KeeLoq_NLF,g5(ciph_temp,0,8,19,25,30));
						}
						plain_temp = ciph_temp;
						plain[gid] = plain_temp; // store result in global memory
				}
				""").build()

		global_size=(data_points,)
		local_size=(workers,)
		preferred_multiple = cl.Kernel(prg, 'sum').get_work_group_info( \
			cl.kernel_work_group_info.PREFERRED_WORK_GROUP_SIZE_MULTIPLE, \
			device)
		'''
		print("Data points:", data_points)
		print("Workers:", workers)
		print("Preferred work group size multiple:", preferred_multiple)

		if (workers % preferred_multiple):
			print("Number of workers not a preferred multiple (%d*N)." \
					% (preferred_multiple))
			print("Performance may be reduced.")
		'''

		exec_evt = prg.sum(queue, global_size, local_size, key_buf, ciph_buf, dest_buf)
		exec_evt.wait()
		elapsed = 1e-9*(exec_evt.profile.end - exec_evt.profile.start)

		print("Execution time of test: %g s" % elapsed)

		plain = numpy.empty_like(ciph)
		cl.enqueue_read_buffer(queue, dest_buf, plain).wait()
		equal = numpy.all( plain == plain_result)
		print (plain)
		print (plain_result)
		print (hexarr(plain))
		print (hexarr(plain_result))
		if not equal:
			print("Results doesn't match!!")

		else:
			print("Results OK")
		