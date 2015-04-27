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
								cipher = ((cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,(15-r)&63)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30)))&0xFFFFFFFF
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
				power=[]
				#print("key "+str(r)+": "+str(hex(device_key))+": "+str(bin(device_key)[2:]).zfill(64))
				prev=cipher
				for r in range(stop):
					cipher = ((cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,(15-r)&63)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30)))&0xFFFFFFFF
					curr=cipher
					power.append((bin(prev^curr)).count('1')) #hamming distance between this and previous round
					prev=cipher
				power=power[::-1]#reverse the list so that the most recent decryption is first
				#power=bin(y0).count('1')
				
				return power				

def partial_decrypt__rand_power_array (cipher,device_key,stop):
				cipher_array=[]
				power=[]
				cipher_array.append(cipher) #add the initial cipher
				#print("key "+str(r)+": "+str(hex(device_key))+": "+str(bin(device_key)[2:]).zfill(64))
				for r in range(2*stop):
					cipher = ((cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,r%64)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30)))&0xFFFFFFFF
					cipher_array.append(cipher)#this will have length 2*stop+1 
				for r in range(len(cipher_array)-1):#this will have length 2*stop
					#power.append((bin(cipher_array[r]^cipher_array[(r+stop)%(len(cipher_array))])).count('1'))
					#power.append((bin(cipher_array[r]^0)).count('1')) #get the hamming wieght
					phyp=bin(cipher_array[r]^[r+1]).count('1')#theoretical power hypothesis
					power.append(random.gauss(phyp,0.1*phyp)) #hamming distance between this and previous round
					#random guassian noise is added to simulate raelity, although we dont know what kind of noise exists in reality, most likely variance it is proportional to peak power 
					
				#print(power)
				#power=bin(y0).count('1')
				#power=power[:len(cipher_array)-stop]e
				return power
				
def partial_decrypt_array (cipher,device_key,stop):
				cipher_array=[]
				power=[]
				cipher_array.append(cipher) #add the initial cipher
				#print("key "+str(r)+": "+str(hex(device_key))+": "+str(bin(device_key)[2:]).zfill(64))
				for r in range(2*stop):
					cipher = ((cipher<<1)^bit(cipher,31)^bit(cipher,15)^bit(device_key,r%64)^bit(KeeLoq_NLF,g5(cipher,0,8,19,25,30)))&0xFFFFFFFF
					cipher_array.append(cipher)#this will have length 2*stop+1 
				for r in range(len(cipher_array)-1):#this will have length 2*stop
					#power.append((bin(cipher_array[r]^cipher_array[(r+stop)%(len(cipher_array))])).count('1'))
					#power.append((bin(cipher_array[r]^0)).count('1')) #get the hamming wieght
					phyp=bin(cipher_array[r]^[r+1]).count('1')#theoretical power hypothesis
					power.append(phyp) #hamming distance between this and previous round
					#random guassian noise is added to simulate raelity, although we dont know what kind of noise exists in reality, most likely variance it is proportional to peak power 
					
				#print(power)
				#power=bin(y0).count('1')
				#power=power[:len(cipher_array)-stop]e
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
	
def algorithm1(keys,numpy_cipher,dummy_bit_guess,master_power):
	dummy_power=[]#stores the power for a key guess
	dummy_corr=[]#stores the correlation between the master key power and a key guesses power
	max_dummy_corr=[]
	bin_key=[]#bin key is a string of the binary representation of the key
	avg_dummy_corr=[]	#largely useless	
	print(keys)
	for key in range(len(keys)):
		bin_key.append(bin(keys[key])[2:].zfill(64)[(64-dummy_bit_guess):]) 
		#print("key guess "+str(key).zfill(2)+" "+bin_key[key])
		dummy_power.append([])#For each key guess we need to get the hypothetical power so append an array that will contain the power for each cipher
		dummy_corr.append([])#correlate the above with the master key
		key_guess_power=[]#contains the power for a particular key guess
		for cipher in range(len(numpy_cipher)): #for each cipher perform a partial decrypt dummy_bit_guesses deep
			key_guess_power_cipher_array=[]
			key_guess_power_cipher_array=partial_decrypt_array(numpy_cipher[cipher],keys[key],dummy_bit_guess)#array length bit_guess for one cipher 1d
			key_guess_power.append(key_guess_power_cipher_array)#append it to an array for each cipher, array is cipher*bit_guess_round 2d
		#print(numpy.array(key_guess_power).shape)
		#print("Key: ",key,key_guess_power[key])
		key_guess_power=numpy.transpose(key_guess_power)
		dummy_power[key].append(key_guess_power)#transpose so it is now bit_guess_round*cipher and append it to the dummy_power array
		#print("Key: ",key,dummy_power[key][0][0])
		#print(numpy.array(key_guess_power).shape)
		#print(numpy.array(dummy_power).shape)
		#Dummy should be a three dimensional array key_guess*bit_guess_round*cipher
		#print(len(master_power[0]))
		#print(len(key_guess_power))
		#print(len(key_guess_power[0]))
		#print(len(numpy.transpose(key_guess_power)))
		#numpy.savetxt(path+"dummy DPA power.csv", dummy_power[0][0], delimiter=",", fmt="%s")
		#print(len(dummy_power))
		#print(len(dummy_power[0]))
		#print(len(dummy_power[0][0]))
		#print(len(dummy_power[0][0][0]))
		for dummy_bit in range(len(dummy_power[key][0])):
			#print(master_power[dummy_bit][0])
			#print(dummy_power[key][dummy_bit])
			#print(numpy.corrcoef(master_power[dummy_bit],dummy_power[key][dummy_bit],1,1)[0,1])
			#print dummy_bit
			dummy_corr[key].append(numpy.corrcoef(master_power[dummy_bit_guess],dummy_power[key][0][dummy_bit],1,1)[0,1]) #for each key guess correlate it to the master key guess
			#print("sucess "+str(dummy_bit))
		max_dummy_corr.append((max(dummy_corr[key]),key,bin_key[key]))
		print(max_dummy_corr[key])
		#avg_dummy_corr.append(numpy.mean(dummy_corr[key]))
		#print(dummy_corr[key])
		#print("Key "+str(key).zfill(2)+" correlation: "+str(max_dummy_corr[key]))#+" Average corr: "+str(avg_dummy_corr[key]))
	#print(numpy.array(dummy_corr).shape)
	likely_keys=sorted(max_dummy_corr, key=itemgetter(0))[:-1*(return_keys+1):-1]	
	#print(likely_keys)
	return(likely_keys,dummy_corr) #Get the four most likely(4 highest max correlation) key guesses, this is the output
	
'''
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
#'''

ciphertext=[]

for i in range(30):
	ciphertext.append(i)
numpy_cipher=numpy.array(ciphertext)

#print (numpy_cipher[0])

dummy_key="B427983C9A60C0F2"#random key
#dummy_key=key_register(int(dummy_key,16))
print("dummy master key:   "+bin(int(dummy_key,16))[2:].zfill(64)[48:])
master_power=[]
for cipher in range(len(numpy_cipher)):
		master_power.append(partial_decrypt__rand_power_array(numpy_cipher[cipher],int(dummy_key,16),70))
#print(master_power)		
#print(len(master_power[0]))
#print("Master key power: ",master_power[dummy_bit_guess])
master_power=numpy.transpose(master_power)
#numpy.savetxt(path+"dummy DPA master.csv", master_power, delimiter=",", fmt="%s")
		
#dummy_key="0000000000000000"#null key

#make the reverse of this function
#and then test using the canonical C code

time1 = time()

round=0 #this will increment after guessing a while batch of keys
bit_guess=8	 #how many bits of the key we want to guess
key_guesses = 2**bit_guess #number of key guesses
return_key_bit_guess=2
return_keys=2**return_key_bit_guess #return this most probable keys
round_bit_guess=4 #guess a constant amount of keys per round
	
	
#turn this monster into a function that takes m key guesses and returns the n most probable key guesses with k known bits	

likely_keys=[] #dictionary( of sorts) of hte max correlation, the index and a string of the key
for round in range(int(math.ceil((64-bit_guess)/round_bit_guess))+1):
#for round in range(6):
	dummy_bit_guess=bit_guess+round*round_bit_guess #This is the depth of the bit we are guessing
	print (round,"",dummy_bit_guess)
	if round==0:
		key_g=[]
		key_g = range(key_guesses)#inital keys is just the first key_guesses # in an array, this needs to be modified after the first round, or needs some clever code to handle the fact when k=0 bits
		#for key in range(key_guesses):
		#	print(bin_rep(key))
	else:
		key_g=[]
		for likely_key in range(len(likely_keys)):
			for key in range(2**round_bit_guess):
				key_g.append(((key<<(dummy_bit_guess-round_bit_guess))^int(likely_keys[likely_key][2],2)))
				#key_g[key]=((key<<(dummy_bit_guess-round_bit_guess))^int(likely_keys[likely_key][2],2))
				#print(bin_rep(key<<(dummy_bit_guess-round_bit_guess)),bin_rep(int(likely_keys[likely_key][2],2)))
				#print(bin_rep(key_g[key]),key_g[key])
				#print(key_g[key])

				
				
	#print(likely_keys)
	#print(key_g)
	output=algorithm1(key_g,numpy_cipher,dummy_bit_guess,master_power)
	corr=output[1]
	likely_keys=output[0]

	plt.close()
	colormap = plt.cm.gist_ncar
	plt.gca().set_color_cycle([colormap(i) for i in numpy.linspace(0, 0.9, key_guesses)])
	fig = plt.gcf()
	fig.set_size_inches(19.20,10.80)
	for key in range(len(keys)):
		plt.plot(range(len(corr[key])),corr[key])
	#plt.legend(bin_key, loc='best')
	plt.savefig(path+"round "+str(round)+" - "+str(dummy_bit_guess)+" bit guesses traces DPA plots.png",dpi=400)
	#print(path+"round "+str(round)+" - "+str(dummy_bit_guess)+" bit guesses traces DPA plots.png")

time2 = time() 
print("processed stuff:", time2 - time1, "s")


sleep(5)



time6 = time()
print("Time taken to make picture ",dummy_bit_guess,"key guesses: ", time6 - time2, "s")


#myfile = open(path+"DPA.csv", 'wb')
#wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#wr.writerow(correlation_array)
#myfile.close()

dummy_power=numpy.transpose(dummy_power,(1,0,2,3))#swap first and second dimensions/axes 2nd axes is one element containing a 2d array
print(dummy_power.shape)
numpy.savetxt(path+"dummy DPA corr.csv", dummy_corr, delimiter=",")
numpy.savetxt(path+"dummy DPA key.csv", keys, delimiter=",")
numpy.savetxt(path+"dummy DPA power.csv", dummy_power[0], delimiter=",",fmt="%s")
numpy.savetxt(path+"dummy DPA master.csv", master_power, delimiter=",", fmt="%s")
#numpy.savetxt(path+"dummy DPA partial cipher.csv", cipher_partial, delimiter=",")
#numpy.savetxt(path+"dummy DPA max correlation.csv", max_corr, delimiter=",")

