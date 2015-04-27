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
import csv
from time import time
import matplotlib.pyplot as plt
import random
import math
from operator import itemgetter


path="$PATH"
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
								cipher = ((cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,(15-r)&63)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30)))&0xFFFFFFFF
								r=r+1
				plain=cipher&0xFFFFFFFF
				return plain
 
def partial_decrypt (cipher,device_key,stop):
				r=0
				while r<=stop:
								cipher = ((cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,(15-r)&63)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30)))&0xFFFFFFFF
								r=r+1
								if r==stop-1:
									y1=cipher&0xFFFFFFFF
									#print("round "+str(r)+": "+str(hex(y1))+": "+str(bin(y1)[2:]).zfill(32))
								if r==stop:
									y0=cipher&0xFFFFFFFF
									#print("round "+str(r)+": "+str(hex(y0))+": "+str(bin(y0)[2:]).zfill(33))
				return y0

def partial_decrypt_power (cipher,device_key,stop):
				r=0
				#print("key "+str(r)+": "+str(hex(device_key))+": "+str(bin(device_key)[2:]).zfill(64))
				while r<=stop:
								cipher = ((cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,(r)%64)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30)))&0xFFFFFFFF
								r=r+1
								if r==stop-1:
									y1=cipher&0xFFFFFFFF
									#print("round "+str(r)+": "+str(hex(y1))+": "+str(bin(y1)[2:]).zfill(32))
								if r==stop:
									y0=cipher&0xFFFFFFFF
									#print("round "+str(r)+": "+str(hex(y0))+": "+str(bin(y0)[2:]).zfill(33))
				power=bin(y1^y0).count('1')
				#power=bin(y0).count('1')
				
				return power
				
def partial_decrypt_power_array (cipher,device_key,stop):
				r=0
				#print("key "+str(r)+": "+str(hex(device_key))+": "+str(bin(device_key)[2:]).zfill(64))
				prev=cipher
				for r in range(stop):
					cipher = ((cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,(r)%64)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30)))&0xFFFFFFFF
					curr=cipher
					power.append((bin(prev^curr)).count('1'))
					prev=cipher
				#power=bin(y0).count('1')
				
				return power				

def partial_decrypt_numpy_power (cipher,device_key,stop):
		r=0
		#print("key "+str(r)+": "+str(hex(device_key))+": "+str(bin(device_key)[2:]).zfill(64))
		while r<=stop:
						cipher = ((cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,(r)&63)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30)))&0xFFFFFFFF
						r=r+1
						if r==stop-1:
							y1=cipher&0xFFFFFFFF
							#print("round "+str(r)+": "+str(hex(y1))+": "+str(bin(y1)[2:]).zfill(32))
						if r==stop:
							y0=cipher&0xFFFFFFFF
							#print("round "+str(r)+": "+str(hex(y0))+": "+str(bin(y0)[2:]).zfill(33))
		power=(y1^y0)
		
		#power=bin(y0).count('1')
		
		return(power)	
				

def read_cipher():
				ciphertext=[]
				ciphertextfile=open(path+"25C3_HCS301\\ciphertexts.txt","r")
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
					with open(path+"25C3_HCS301\\Peak"+str(i+1)+".dat",mode='rb') as file:
						j=0
						while j<1650:
							byte = file.read(8)
							#print(str(j)+" "+byte
							Peak[i].append(struct.unpack('d',byte)[0])
							j=j+1
						file.close()
					i=i+1
				return Peak

def key_register(key):
	#print(key) #take a base 10 digit convert it into the actually jey in the right format (flipped and left rotated 16 bits)
	key=(bin(key))[2:]#get rid of 0b
	#print(key)
	key=key.zfill(64)#64 chars
	#print(key)
	key=key[::-1]#reverse
	#print(key)
	key=int(key,2)#convert to binary
	#print(key)
	key=(((key>>(64-16))^(key<<(16)))&0xFFFFFFFFFFFF)#rotate 48 bits to right or 16 bits to left
	#print(key)
	return key
	
def bin_rep(int):
	return(bin(int)[2:].zfill(16))


def algorithm1(keys,numpy_cipher,bit_guess,transpose_peak):
	
	power=[]
	test_power=[]
	correlation_array=[]
	max_corr=[]
	bin_key=[]#bin key is a string of the binary representation of the key
	traces=997		

	for key in range(len(keys)):
		bin_key.append(bin(keys[key])[2:].zfill(64)[(64-bit_guess):]) 
		power.append([])
		test_power.append([])
		#cipher_partial.append([])
		correlation_array.append([])
		#print("key: ",(bin(keys[key])[2:]).zfill(64))
		#print("key: ",(bin(keys[key])[50:]).zfill(64))
		#print("key: "+str((bin(keys[key])[50:].count('1'))))
		numpy_power=numpy.empty_like(numpy_cipher)
		numpy_power=partial_decrypt_numpy_power(numpy_cipher,keys[key],bit_guess)
		test_power[key]=numpy_power.tolist()
		test_power[key]=test_power[key][:traces]
		#print(len(power))
		for i in range(len(test_power[key])):
			test_power[key][i]=bin(test_power[key][i]).count('1')

		#this loop should be done using numpy, much faster, currently each complete loop takes .57 seconds, too slow
		#for cipher in range(len(numpy_cipher[:traces])):
		#		power[key].append(partial_decrypt_power(numpy_cipher[cipher],keys[key],bit_guess))
				#cipher_partial[key].append(partial_decrypt(numpy_cipher[cipher],keys[key],bit_guess))
				#print(partial_decrypt(numpy_cipher[cipher],keys[key],bit_guess))	
				#print(power[key])
				#power is an array as large as ciphertext i.e 997, this will be correlated with all 997 traces
				#print(range(len(ciphertext)))
		#print(len(test_power[key]))
		#print(len(power[key]))
		#sleep(5)
		for peak in range(len(transpose_peak))[1502:1600:3]:
			#print(len(transpose_peak[peak]))
			#print(transpose_peak[peak])
			#print(range(len(power[key])))
			correlation_array[key].append(numpy.corrcoef(test_power[key],transpose_peak[peak][:traces],1,1)[0,1])
			#print(numpy.corrcoef(power[key],transpose_peak[peak],1,1)[0,1])
			#Peak[i] is an array of the ith sample of all 997 traces
		corr_numpy=numpy.array(correlation_array)
		max_corr.append((max(corr_numpy[key]),key,bin_key[key]))#get the index of the sample which gave this highest corelation check that is the same for all keys guessed
		#print(max_corr[key])
		
			#hopefully this corresponds to the trace which represents the 16th decyption round
			#correlation_array will get the correlation of the key guess and the nth power sample
			#this corresponds to figure 4 in "the power of power analysis"
	likely_keys=sorted(max_corr, key=itemgetter(0))[:-1*(return_keys+1):-1]	
	return(likely_keys,corr_numpy) #Get the four most likely(4 highest max correlation) key guesses, this is the output				

'''
#Read in all the files

time1 = time()
 
ciphertext=read_cipher()
 
#line889 index starts at0
 

Peak=read_powertrace()
time2 = time() 
print("Read ciphertext:", time2 - time1, "s")
 
 
#print Peak[0] all sample of trace 1, need to transpose so that Peak[0] represents the first sample of all 997 traces
time3 = time()
print("Read power trace:", time3 - time2, "s")
#'''


numpy_peak=numpy.array(Peak)

#for trace in range(len(numpy_peak)):#3 period Moving average of all the peaks
#	for peak in range(len(numpy_peak[trace])-2):
#		numpy_peak[trace][peak]=numpy_peak[trace][peak]+numpy_peak[trace][peak+1]+numpy_peak[trace][peak+2]
transpose_peak=numpy.transpose(numpy_peak)
numpy_cipher=numpy.array(ciphertext)

#print (numpy_cipher[0])

time4 = time()
round=0 #this will increment after guessing a while batch of keys
bit_guess=4	 #how many bits of the key we want to guess
key_guesses = 2**bit_guess #number of key guesses
return_key_bit_guess=4
return_keys=2**return_key_bit_guess #return this most probable keys
round_bit_guess=4 #guess a constant amount of keys per round

#'''
likely_keys=[] #dictionary( of sorts) of hte max correlation, the index and a string of the key
for round in range(int(math.ceil((64-bit_guess)/round_bit_guess))+1):
#for round in range(2):
	timea = time()
	current_bit_guess=bit_guess+round*round_bit_guess #This is the depth of the bit we are guessing
	print (round,"",current_bit_guess)
	if round==0:
		keys=[]
		keys = range(key_guesses)#inital keys is just the first key_guesses # in an array, this needs to be modified after the first round, or needs some clever code to handle the fact when k=0 bits
		#for key in range(key_guesses):
		#	print(bin_rep(key))
	else:
		keys=[]
		for likely_key in range(len(likely_keys)):
			print(str(likely_key).zfill(2)+" best key for round: "+str(round).zfill(2)+" "+likely_keys[likely_key][2]+" correlation: "+str(likely_keys[likely_key][0])[:5])
			for key in range(2**round_bit_guess):
				keys.append(((key<<(current_bit_guess-round_bit_guess))^int(likely_keys[likely_key][2],2)))
				#key_g[key]=((key<<(current_bit_guess-round_bit_guess))^int(likely_keys[likely_key][2],2))
				#print(bin_rep(key<<(current_bit_guess-round_bit_guess)),bin_rep(int(likely_keys[likely_key][2],2)))
				#print(bin_rep(keys[key]),keys[key])
				#print(keys[key])
	output=algorithm1(keys,numpy_cipher,current_bit_guess,transpose_peak)
	corr=output[1]
	likely_keys=output[0]
	timeb = time()
	print("Time taken to process round ",round,"key guesses: ", timeb - timea, "s")
	#plt.close()
	#colormap = plt.cm.gist_ncar
	#plt.gca().set_color_cycle([colormap(i) for i in numpy.linspace(0, 0.9, key_guesses)])
	#fig = plt.gcf()
	#fig.set_size_inches(19.20,10.80)
	#for key in range(len(keys)):
	#	plt.plot(range(len(corr[key])),corr[key])
	#plt.legend(bin_key, loc='best')
	#plt.savefig(path+"traces "+str(50)+" round "+str(round)+" - "+str(bit_guess)+" bit guesses traces DPA plots.png",dpi=400)
	#print(path+"round "+str(round)+" - "+str(dummy_bit_guess)+" bit guesses traces DPA plots.png")
	
for likely_key in range(len(likely_keys)):
			print(str(likely_key).zfill(2)+" best key for round: "+str(round).zfill(2)+" "+likely_keys[likely_key][2]+" correlation: "+str(likely_keys[likely_key][0])[:5])	
#'''


#print(keys)

#keys=int((keys),2)

#print(bit_guess)
#print(key_guesses)
#print(keys)
#print ciphertext[888]
#print(Peak[1])
#print(transpose_peak[1])
 
 
#print("ciphertext: "+ciphertext[2])
#print("ciphertext base10: "+str(int(ciphertext[2],16)))
#print("Key: "+str(keys[2]))
#print(partial_decrypt(int(ciphertext[2],16),keys[2],4))
#print(decrypt(int(ciphertext[2],16),keys[2]))
#print((len(transpose_peak)))

time5 = time()

#input key, get correlation for each cipher 

#print(len(correlation_array[0]))
#print(len(correlation_array))

print("Time taken to preocess stuff ",key_guesses,"key guesses: ", time5 - time4, "s")

'''
j=0
												while j<100:
																byte = file.read(1)
																print(str(j)+" "+byte)
																j=j+1

'''

sleep(5)

plt.close()
colormap = plt.cm.gist_ncar
plt.gca().set_color_cycle([colormap(i) for i in numpy.linspace(0, 0.9, len(keys))])
fig = plt.gcf()
fig.set_size_inches(19.20,10.80)
for key in range(key_guesses):
	plt.plot(range(len(correlation_array[key])),correlation_array[key])
plt.legend(range(key_guesses), loc='best')
plt.savefig(path+str(traces)+" traces DPA plots.png",dpi=400)


time6 = time()
print("Time taken to make picture ",key_guesses,"key guesses: ", time6 - time5, "s")


#myfile = open(path+"DPA.csv", 'wb')
#wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#wr.writerow(correlation_array)
#myfile.close()
numpy.savetxt(path+"DPA corr.csv", correlation_array, delimiter=",")
numpy.savetxt(path+"DPA key.csv", keys, delimiter=",")
numpy.savetxt(path+"DPA power.csv", power, delimiter=",")
numpy.savetxt(path+"DPA cipher.csv", numpy_cipher, delimiter=",")
numpy.savetxt(path+"DPA partial cipher.csv", cipher_partial, delimiter=",")
numpy.savetxt(path+"DPA max correlation.csv", max_corr, delimiter=",")
