; Homestead K0 entry — Limine jumps to _start in 64-bit mode.
global _start
extern kmain

section .text
_start:
    call kmain
.hang:
    hlt
    jmp .hang
