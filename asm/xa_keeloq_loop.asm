;breakpoints 
; 000c init routines done
; loop 2 location
; 000f LDA _l0 

; the order of the bytes doesnt matter but ive "reversed" them so they look like theyre in order
;plaintext
_p0=$1103
_p1=$1102
_p2=$1101
_p3=$1100

;key
_k0=$1117
_k1=$1116
_k2=$1115
_k3=$1114
_k4=$1113
_k5=$1112
_k6=$1111
_k7=$1110

;loop
_l0=$1121
_l1=$1120

; NLF magic number 
_n0=$1130
_n1=$1131
_n2=$1132
_n3=$1133

;$0200 store final bit to be appended when shifting
;$0201 NLF magic number offset
;$0202 first two bits of $0201, sue to select NLG magic number byte
;$0203 last three bits of $0201
;set_zero=and#$0

;9    9    5    5    3    3    1    1   
;1001 1001 0101 0101 0011 0011 0001 0001
; right shift
;0100 1100 1010 1010 1001 1001 1000 1000
;4    c    a    a    9    9    8    8

;NLF offset 31 26 20  9  1
;            1  0  1  1  0

;init routines
jsr load_plain
jsr load_key
jsr load_nlf
jsr load_loop
inc _l1 ; shouldnt need this but the loop doesnt run 256 times enough
;
loop2:	jsr encrypt ; loop 2 is the inner loop
	dec _l0
	bne loop2 ; if mem is not zero then branch to loop 2
	dec _l1;  otherwise decrement higher byte
	bne loop1 ; if mem is not zero keep looping;
brk ; otherwise break ie end of program
 

loop1:	jsr encrypt ; need to run this when _l0 goes to 0
	lda #$FF
	sta _l0
	clv ; unlike the example i found, i dont want to set the low byte to FF the 1st time
	bvc loop2


encrypt:
;inside loop
jsr bit0
jsr bit16
jsr key0
jsr NLF_encrypt_bit
jsr rotate_right_plain
jsr rotate_right_key
rts

load_plain:
;load plaintext
lda #$99 ; MSB
sta _p3 ; 
lda #$55
sta _p2
lda #$33
sta _p1
lda #$11
sta _p0
rts


;load NLF magic number
;load key
load_key:
lda #$FE 
sta _k7 ; 
lda #$DC 
sta _k6 ; 
lda #$BA 
sta _k5 ; 
lda #$98 
sta _k4 ; 
lda #$76 
sta _k3 ; 
lda #$54 
sta _k2 ; 
lda #$32 
sta _k1 ; 
lda #$10 
sta _k0 ; 
rts

;load loop
load_loop:
lda #$02 ; 512
sta _l1
lda #$10 ; 16, might need to be 0F
sta _l0
rts

;load NLF magic number note that n0 is actually the MSB of the NLF number, this is to get the
;correct byte when using the  register to offset the address
load_nlf;
lda #$3A
sta _n3
lda #$5C
sta _n2
lda #$74
sta _n1
lda #$2E
sta _n0
rts


bit0:
lda _p0
and #$01 ; keep only bit 0 
sta $0200
rts

bit16:
lda _p2
and #$01 ; keep only bit 16 (bit 0 of byte 2)
eor $0200 ; XOR with bit 0 
sta $0200
rts

key0:
lda _k0
and #$01 ; keep only bit 0 of key
eor $0200 ; XOR with WIP 
sta $0200
rts;

NLF_encrypt_bit:
;NLF function offset 31 26 20 9 1 
lda #$00 ; clear mem then store NLf offset
sta $0201

lda _p3 ; bit 31 is MSb of byte 3
rol ; bit 31 in carry flag
rol $0201 ; bit 31 is now LSb in NLF offset

rol ;30
rol ;29
rol ;28
rol ;27
rol ; bit 26 now in carry flag
rol $0201

ldy $0201 ; store the first two bits in X register, used to select the NLF magic number byte
sty $0202 ; probs not needed, only if y reg is changed

lda _p2
rol ; 23 
rol ; 22
rol ; 21
rol ; 20
rol $0201

lda _p1
ror ; 8
ror ; 9
rol $0201

lda _p0
ror ; 0 
ror ; 1
rol $0201

;5 bit offset should be in $0201 now 

lda $0201
and #%00000111
tax ; load bit offset into X, will be used as loop decrement

lda _n0,Y ; load the correct NLF byte into A

jsr right_NLF
; carry flag now has result of NLF

; not happening INVESTIGATION  
eor $0200 ;  $0200 now has the result of XORing bits 0, 16, key and NLF
sta $0200
rts


right_NLF:

cpx #$00 ; if X==0 dont branch loop until the right NLF bit is in the LSbit of Acc 
bne rotate_right_NLF ;
;execution after branch/loop
and #$01 ; keep last bit of NLF byte
rts

rotate_right_NLF:

ror ; rotate acc, contains NLF byte
dex ; decrement X
clv ; oVerflow not useful in this program, clear it to branch
bvc right_NLF; jsr not working problems when returning
;jsr right_NLF;this causes problems, not returning to the right place 

rotate_right_plain:

;make sure the carry bit contains the result ($0200)
ror ; put results of XOR into carry, then thisft into plaintext
ror _p3
ror _p2
ror _p1
ror _p0

rts

rotate_right_key:

clc ;clear carry INVESTIGATION
lda _k0
ror ;move bit 0 of key into carry
ror _k7 ; rotate bit0 into byte 7 (bit 63)
ror _k6
ror _k5
ror _k4
ror _k3
ror _k2
ror _k1
ror _k0

rts


