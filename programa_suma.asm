.data
    newline: .asciiz "\n"

.text
.globl main

# Función: suma(x, y)
# Parámetros: $a0 = x, $a1 = y
# Retorno: $v0 = x + y
suma:
    addiu $sp, $sp, -8
    sw    $ra, 4($sp)
    sw    $s0, 0($sp)

    add   $s0, $a0, $a1

    move  $v0, $s0

    lw    $ra, 4($sp)
    lw    $s0, 0($sp)
    addiu $sp, $sp, 8
    jr    $ra

main:
    li    $s0, 10
    li    $s1, 20

    move  $a0, $s0
    move  $a1, $s1
    jal   suma
    move  $s2, $v0

    li    $v0, 1
    move  $a0, $s2
    syscall
    li    $v0, 4
    la    $a0, newline
    syscall

    li    $v0, 10
    syscall