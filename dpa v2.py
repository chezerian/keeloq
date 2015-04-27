'''
read file full of ciphertexts
read in all 997 power traces
implement keeloq decryption but with printing out a s[pecific round
use numpy to perform correlation with power trace
'''
import numpy
import numpy.linalg as la
import datetime
import struct
from time import time
KeeLoq_NLF=0x3A5C742E
 
 
def bit(x,n):
				y=(((x)>>(n))&1)
				return y
def g5(x,a,b,c,d,e):
				y=(bit(x,a)+bit(x,b)*2+bit(x,c)*4+bit(x,d)*8+bit(x,e)*16)
				return y
 
#The key starts at bit 15 and then gets left shifted (next bit used is 14)
def decrypt (cipher,device_key):
				r=0
				while r<528:
								cipher = (cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,(15-r)&63)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30))
								r=r+1
				plain=cipher&0xFFFFFFFF
				return plain
 
def partial_decrypt (cipher,device_key,stop):
				r=0
				while r<=stop:
								cipher = (cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,(15-r)&63)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30))
								r=r+1
								if r==stop-1:
									y1=cipher&0xFFFFFFFF
									#print("round "+str(r)+": "+str(hex(y1))+": "+str(bin(y1)[2:]).zfill(32))
								if r==stop:
									y0=cipher&0xFFFFFFFF
									#print("round "+str(r)+": "+str(hex(y0))+": "+str(bin(y0)[2:]).zfill(33))
				power=bin(y1^y0).count('1')
				
				return power
			  
			  
def read_cipher():
				ciphertext=[]
				ciphertextfile=open("PATH/ciphertexts.txt","r")
				for line in ciphertextfile:
					ciphertext.append(int(line,16))
				print ciphertext[888]
				#line889 index starts at0
				ciphertextfile.close()
				return ciphertext
			  
def read_powertrace():
				i=0
				Peak=[]
				while i<997:
					Peak.append(i)
					Peak[i]=[]
					with open("PATH/Peak"+str(i+1)+".dat",mode='rb') as file:
						j=0
						while j<1650:
							byte = file.read(8)
							#print(str(j)+" "+byte
							Peak[i].append(struct.unpack('d',byte)[0])
							j=j+1
						file.close()
					i=i+1
				return Peak
				

#Read in all the files

time1 = time()
 
ciphertext=read_cipher()
 
#line889 index starts at0
 
time2 = time()
Peak=read_powertrace()
 
print("Read ciphertext:", time2 - time1, "s")
 
 
#print Peak[0] all sample of trace 1, need to transpose so that Peak[0] represents the first sample of all 997 traces
time3 = time()
print("Read power trace:", time3 - time2, "s")




numpy_peak=numpy.array(Peak)
transpose_peak=numpy.transpose(numpy_peak)
numpy_cipher=numpy.array(ciphertext)

#print (numpy_cipher[0])

bit_guess=2 #how many bits of the key we want to guess
key_guesses = 2**bit_guess #number of key guesses
#start at 2^15 and go through key guesses decrementing by 1 each time, this is because key loq starts at bit 15
keys = numpy.arange(2**15,2**15-key_guesses,-1)#.astype(numpy.uint64)
 
#print(bit_guess)
#print(key_guesses)
#print(keys)
#print ciphertext[888]
#print(Peak[1])
#print(transpose_peak[1])
 
 
power=[]
correlation_array=[]
 
#print("ciphertext: "+ciphertext[2])
#print("ciphertext base10: "+str(int(ciphertext[2],16)))
#print("Key: "+str(keys[2]))
#print(partial_decrypt(int(ciphertext[2],16),keys[2],4))
#print(decrypt(int(ciphertext[2],16),keys[2]))

#input key, get correlation for each cipher 
for key in range(len(keys)):
	power.append([])
	correlation_array.append([])
	print(power[key])
	for cipher in range(len(numpy_cipher)):
			power[key].append(partial_decrypt(numpy_cipher[cipher],keys[key],bit_guess))
			#print(partial_decrypt(numpy_cipher[cipher],keys[key],bit_guess))
			#print(power[key])
			#power is an array as large as ciphertext i.e 997, this will be correlated with all 997 traces
			#print(range(len(ciphertext)))
	for peak in range(len(transpose_peak[peak])):
		#print(len(transpose_peak[peak]))
		#print(transpose_peak[peak])
		#print(range(len(power[key])))
		correlation_array[key].append(numpy.corrcoef(power[key],transpose_peak[peak],1,1)[0,1])
		print(numpy.corrcoef(power[key],transpose_peak[peak],1,1)[0,1])
		#Peak[i] is an array of the ith sample of all 997 traces
	#zmax_corr.append(max(correlation_array[key])) #get the index of the sample which gave this highest corelation check that is the same for all keys guessed
								#hopefully this corresponds to the trace which represents the 16th decyption round
								#correlation_array will get the correlation of the key guess and the nth power sample
								#this corresponds to figure 4 in "the power of power analysis"
							  
							  
'''
j=0
												while j<100:
																byte = file.read(1)
																print(str(j)+" "+byte)
																j=j+1

'''
