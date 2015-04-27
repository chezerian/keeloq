from __future__ import print_function

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


key = 32766
ciph = 313194730
plain_result = 0

print ("Cipher text: "+str(ciph))
print ("Key text: "+str(key))

temp=ciph

# Speed in normal CPU usage
time1 = time()

r=0
while r<3:
				temp = (temp<<1)^bit(temp,31)^bit(temp,15)^bit(key,(15-r)&63)^bit(KeeLoq_NLF,g5(temp,0,8,19,25,30))
				r=r+1
			   
plain_result=temp&0xFFFFFFFF

print ("Plaintext: "+str(plain_result))