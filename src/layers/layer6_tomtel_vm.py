"""
Layer 6: Tomtel Core i69 VM.

Fetch–decode–execute loop over bytecode. Memory = bytecode; output is
collected via OUT and returned when HALT. All values unsigned.
"""
from helpers import read_u8, read_u32_le, write_u8


def run_tomtel_vm(bytecode: bytes) -> bytes:
    """
    Run Tomtel Core i69 bytecode. Returns the output stream as bytes.
    """
    mem = bytearray(bytecode)
    n = len(mem)

    # 8‑bit: a,b,c,d,e,f. Index 0 unused; 1..6 = a..f; 7 = (ptr+c) pseudo-reg.
    r8 = [0] * 7
    # 32‑bit: la, lb, lc, ld, ptr, pc. Index 0 unused; 1..6 = la..pc.
    r32 = [0] * 7

    out: list[int] = []

    def pc() -> int:
        return r32[6]

    def set_pc(v: int) -> None:
        r32[6] = v & 0xFFFFFFFF

    def ptr() -> int:
        return r32[5]

    def cursor_addr() -> int:
        return (ptr() + r8[3]) & 0xFFFFFFFF  # ptr + c

    def read8(reg: int) -> int:
        if 1 <= reg <= 6:
            return r8[reg]
        if reg == 7:
            return read_u8(mem, cursor_addr())
        return 0

    def write8(reg: int, v: int) -> None:
        v = v & 0xFF
        if 1 <= reg <= 6:
            r8[reg] = v
        elif reg == 7:
            write_u8(mem, cursor_addr(), v)

    def read32(reg: int) -> int:
        if 1 <= reg <= 6:
            return r32[reg]
        return 0

    def write32(reg: int, v: int) -> None:
        v = v & 0xFFFFFFFF
        if 1 <= reg <= 6:
            r32[reg] = v

    while True:
        addr = pc()
        if addr < 0 or addr >= n:
            break
        op = mem[addr]

        if op == 0x01:  # HALT
            break
        if op == 0x02:  # OUT a
            out.append(r8[1])
            set_pc(addr + 1)
            continue
        if op == 0xC1:  # CMP: f = 0 if a==b else 0x01
            r8[6] = 0x01 if r8[1] != r8[2] else 0x00
            set_pc(addr + 1)
            continue
        if op == 0xC2:  # ADD a <- b
            r8[1] = (r8[1] + r8[2]) & 0xFF
            set_pc(addr + 1)
            continue
        if op == 0xC3:  # SUB a <- b (mod 256)
            r8[1] = (r8[1] - r8[2]) & 0xFF
            set_pc(addr + 1)
            continue
        if op == 0xC4:  # XOR a <- b
            r8[1] ^= r8[2]
            set_pc(addr + 1)
            continue
        if op == 0xE1:  # APTR imm8: ptr += imm8
            if addr + 2 > n:
                break
            imm8 = mem[addr + 1]
            r32[5] = (r32[5] + imm8) & 0xFFFFFFFF
            set_pc(addr + 2)
            continue
        if op == 0x21:  # JEZ imm32: jump if f==0, else advance past 5-byte insn
            if addr + 5 > n:
                break
            imm32 = read_u32_le(mem, addr + 1)
            if r8[6] == 0:
                set_pc(imm32)
            else:
                set_pc(addr + 5)
            continue
        if op == 0x22:  # JNZ imm32: jump if f!=0, else advance
            if addr + 5 > n:
                break
            imm32 = read_u32_le(mem, addr + 1)
            if r8[6] != 0:
                set_pc(imm32)
            else:
                set_pc(addr + 5)
            continue
        if (op >> 6) == 0b01:  # MV / MVI (src==0 => MVI, 2 bytes)
            dest = (op >> 3) & 7
            src = op & 7
            if src == 0:
                if addr + 2 > n:
                    break
                imm8 = mem[addr + 1]
                write8(dest, imm8)
                set_pc(addr + 2)
            else:
                write8(dest, read8(src))
                set_pc(addr + 1)
            continue
        if (op >> 6) == 0b10:  # MV32 / MVI32 (src==0 => MVI32, 5 bytes)
            dest = (op >> 3) & 7
            src = op & 7
            if src == 0:
                if addr + 5 > n:
                    break
                imm32 = read_u32_le(mem, addr + 1)
                write32(dest, imm32)
                # Gotcha: when dest is pc (6), we just set pc to target. Do *not*
                # advance pc (addr+5), or we overwrite the jump and fall through
                # into data — e.g. "Unknown opcode 0x0F" when landing in non-instruction bytes.
                if dest != 6:
                    set_pc(addr + 5)
            else:
                write32(dest, read32(src))
                if dest != 6:
                    set_pc(addr + 1)
            continue

        raise RuntimeError("Unknown opcode 0x{:02X} at pc=0x{:X}".format(op, addr))

    return bytes(out)
