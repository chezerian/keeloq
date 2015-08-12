/*\
 *  Corrected KeeLoq Encryption and Decryption functions by Ruptor.
 *  Use at your own risk! This source is not copyrighted.
 *  Encoder encrypts an all-0 block, decoder decrypts it.
 *  KeeLoq cipher encrypts 32-bit blocks with 64-bit keys.
 *  Key is XORed with a 32-bit IV incremented on each use.
 *  See http://www.keeloq.boom.ru/decryption.pdf for more details.
 *  KeeLoq algorithm itself is not patented.
\*/

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#define KeeLoq_NLF		0x3A5C742E
#define bit(x,n)		(((x)>>(n))&1)
#define g5(x,a,b,c,d,e)	(bit(x,a)+bit(x,b)*2+bit(x,c)*4+bit(x,d)*8+bit(x,e)*16)

//assumes little endian
void printBits(size_t const size, void const * const ptr)
{
    unsigned char *b = (unsigned char*) ptr;
    unsigned char byte;
    int i, j;

    for (i=size-1;i>=0;i--)
    {
        for (j=7;j>=0;j--)
        {
            byte = b[i] & (1<<j);
            byte >>= j;
            printf("%u", byte);
        }
    }
    puts("");
}

int main()
{
	uint32_t	data=0x99553311;
	uint32_t	r;
	uint64_t	key=0xFEDCBA9876543210;
	uint32_t	x = data;
	char		bit0;
	uint32_t	result;
	char		bit16;
	char		key0;
	char		nlf_offset;
	char		nlf_byte_offset;
	char		nlf_bit_offset;
	char		nlf_result;
	
	printf("\n key: \t\t  %X ",key>>32) ;
	printf("%X \n",key) ;
	printBits(sizeof(key), &key);
	printf(" x data \t\t %X \n",x) ;
	printBits(sizeof(x), &x);

	//for (r = 0; r < 528; r++)
	for (r = 0; r < 1; r++)
	{
		bit0=bit(x,0);
		result=bit0;
		printf("\n bit0 \t\t %X", bit0) ;
		printf("\n result  bit0 %X", result ) ;

		bit16=bit(x,16);
		result^=bit16 ; // result=result^bit16
		printf("\n bit16 \t\t %X", bit16) ;
		printf("\n result bit16 %X", result ) ;

		key0=bit(key,0);
		result^=key0; // result=result^key0
		printf("\n key \t\t %X", key0) ;
		printf("\n result key %X", result ) ;

		nlf_offset=(bit(x,31)<<4)+(bit(x,26)<<3)+(bit(x,20)<<2)+(bit(x,9)<<1)+bit(x,1) ;
		nlf_byte_offset=nlf_offset>>3;
		nlf_bit_offset=nlf_offset&0x07 ;
		nlf_result=bit(KeeLoq_NLF,nlf_offset);
		result^=nlf_result;
		printf("\n nlf offset\t %X \n", nlf_offset) ;
		printBits(sizeof(nlf_offset), &nlf_offset);
		printf(" nlf byte offset \t %X \n", nlf_byte_offset) ;
		printBits(sizeof(nlf_byte_offset), &nlf_byte_offset);
		printf(" nlf bit offset \t %X \n", nlf_bit_offset) ;
		printBits(sizeof(nlf_bit_offset), &nlf_bit_offset);
		printf(" nlf result \t  %X", nlf_result) ;
		printf("\n result  nlfresult \t %X", result ) ;

		x = (x>>1)^(result<<31); //shif data and attach result to 
	//x = (x>>1)^((bit(x,0)^bit(x,16)^(uint32_t)bit(key,r&63)^bit(KeeLoq_NLF,g5(x,1,9,20,26,31)))<<31);
		key=(key>>1)^(key<<63) ; // rotate key 
		
		printf("\n key: \t  %X ",key>>32) ;
		printf("%X \n",key) ;
		printBits(sizeof(key), &key);
		printf(" x data \t %X \n",x) ;
		printBits(sizeof(x), &x);
	}
}

/*
uint32_t	KeeLoq_Decrypt (const uint32_t data, const uint64_t key)
{
	uint32_t	x = data, r;

	for (r = 0; r < 528; r++)
	{
		x = (x<<1)^bit(x,31)^bit(x,15)^(uint32_t)bit(key,(15-r)&63)^bit(KeeLoq_NLF,g5(x,0,8,19,25,30));
	}
	return x;
}
*/
