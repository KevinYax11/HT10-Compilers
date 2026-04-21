.data
    newline: .asciiz "\n"

.text
.globl main

main:
    li   $s0, 10
    li   $s1, 20
    li   $t0, 2
    mul  $t1, $s1, $t0
    add  $s2, $s0, $t1
    li   $t2, 30
    ble  $s2, $t2, L1

    li   $v0, 1
    move $a0, $s2
    syscall
    li   $v0, 4
    la   $a0, newline
    syscall

    li   $t3, 10
    sub  $s3, $s2, $t3

L1:
    li   $v0, 1
    move $a0, $s3
    syscall
    li   $v0, 4
    la   $a0, newline
    syscall

    li   $v0, 10
    syscall