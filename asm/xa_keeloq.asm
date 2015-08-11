;key
_k0=$1110
_k1=$1111
_k2=$1112
_k3=$1113
_k4=$1114
_k5=$1115
_k6=$1116
_k7=$1117

;plaintext
_p0=$1100
_p1=$1101
_p2=$1102
_p3=$1103

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

jsr load_plain
jsr load_key
jsr load_nlf
jsr bit0
jsr bit16
jsr key0
jsr rotate_right_key
jsr NLF_encrypt_bit
jsr rotate_right_plain
brk

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
sta _k0 ; 
lda #$DC 
sta _k1 ; 
lda #$BA 
sta _k2 ; 
lda #$98 
sta _k3 ; 
lda #$76 
sta _k4 ; 
lda #$54 
sta _k5 ; 
lda #$32 
sta _k6 ; 
lda #$10 
sta _k7 ; 
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
;need subtourintes to shift left(decrypt) and right(encrypt) 32 bits(plain cipher NLF number) and 64 bits (key)
rts;

NLF_encrypt_bit:
;NLF function offset 31 26 20 9 1 
lda #$00
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

ldx $0201 ; store the first two bits in X register, used to select the NLF magic number byte
stx $0202 ; probs not needed

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
sta $0203 ; store last three bits in $0203

lda _n0,X ; load the correct NLF byte into A

ldx $0203 ; last three bits into X, going to be loop variable 
jsr right_NLF
; carry flag now has result of NLF

lda #$00
rol ; move carry flag into A
eor $0200 ;  $0200 now has the result of XORing bits 0, 16, key and NLF

rts


right_NLF:

cpx #$00 ; if X==0 then the carry flag will be set 
bne rotate_right_NLF ;
;execution after branch/loop
ror ; one rotation is needed in order to store in carry flag
rts

rotate_right_NLF:

ror ; rotate acc, contains NLF byte
dex ; decrement X
jsr right_NLF; 


rotate_right_plain:

;make sure the carry bit contains the result ($0200)
ror _p3
ror _p2
ror _p1
ror _p0

rts

rotate_right_key:

clc ;clear carry
sta _k0
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


