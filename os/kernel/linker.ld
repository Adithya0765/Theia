/* Homestead K0 linker — 1MB load, Limine .requests preserved. */
ENTRY(_start)

SECTIONS {
    . = 0x100000;

    .requests : {
        KEEP(*(.requests .requests_start_marker .requests_end_marker))
    }

    .text : {
        *(.text*)
    }

    .rodata : {
        *(.rodata*)
    }

    .data : {
        *(.data*)
    }

    .bss : {
        *(COMMON)
        *(.bss*)
    }
}
