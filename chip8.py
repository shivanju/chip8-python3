import random
import pyxel

class Chip8:
    def __init__(self):
        pyxel.init(64, 32, caption = "Chip-8", fps = 900, scale = 10)
        self.key_map = {
            pyxel.KEY_0: 0x0,
            pyxel.KEY_1: 0x1,
            pyxel.KEY_2: 0x2,
            pyxel.KEY_3: 0x3,
            pyxel.KEY_4: 0x4,
            pyxel.KEY_5: 0x5,
            pyxel.KEY_6: 0x6,
            pyxel.KEY_7: 0x7,
            pyxel.KEY_8: 0x8,
            pyxel.KEY_9: 0x9,
            pyxel.KEY_A: 0xa,
            pyxel.KEY_B: 0xb,
            pyxel.KEY_C: 0xc,
            pyxel.KEY_D: 0xd,
            pyxel.KEY_E: 0xe,
            pyxel.KEY_F: 0xf
        }
        self.fontset = {
            '0': [0xF0, 0x90, 0x90, 0x90, 0xF0],
            '1': [0x20, 0x60, 0x20, 0x20, 0x70],
            '2': [0xF0, 0x10, 0xF0, 0x80, 0xF0],
            '3': [0xF0, 0x10, 0xF0, 0x10, 0xF0],
            '4': [0x90, 0x90, 0xF0, 0x10, 0x10],
            '5': [0xF0, 0x80, 0xF0, 0x10, 0xF0],
            '6': [0xF0, 0x80, 0xF0, 0x90, 0xF0],
            '7': [0xF0, 0x10, 0x20, 0x40, 0x40],
            '8': [0xF0, 0x90, 0xF0, 0x90, 0xF0],
            '9': [0xF0, 0x90, 0xF0, 0x10, 0xF0],
            'A': [0xF0, 0x90, 0xF0, 0x90, 0x90],
            'B': [0xE0, 0x90, 0xE0, 0x90, 0xE0],
            'C': [0xF0, 0x80, 0x80, 0x80, 0xF0],
            'D': [0xE0, 0x90, 0x90, 0x90, 0xE0],
            'E': [0xF0, 0x80, 0xF0, 0x80, 0xF0],
            'F': [0xF0, 0x80, 0xF0, 0x80, 0x80]
        }
        self.operation_lookup = {
            '0x0': self.i_0nnn,
            '0x1': self.i_1nnn,
            '0x2': self.i_2nnn,
            '0x3': self.i_3xkk,
            '0x4': self.i_4xkk,
            '0x5': self.i_5xy0,
            '0x6': self.i_6xkk,
            '0x7': self.i_7xkk,
            '0x8': self.i_8xyn,
            '0x9': self.i_9xy0,
            '0xa': self.i_annn,
            '0xb': self.i_bnnn,
            '0xc': self.i_cxkk,
            '0xd': self.i_dxyn,
            '0xe': self.i_exnn,
            '0xf': self.i_fxnn
        }

        self.logical_lookup = {
            '0x0': self.i_8xy0,
            '0x1': self.i_8xy1,
            '0x2': self.i_8xy2,
            '0x3': self.i_8xy3,
            '0x4': self.i_8xy4,
            '0x5': self.i_8xy5,
            '0x6': self.i_8xy6,
            '0x7': self.i_8xy7,
            '0xe': self.i_8xye
        }

        self.misc_lookup = {
            '0x7': self.i_fx07,
            '0xa': self.i_fx0a,
            '0x15': self.i_fx15,
            '0x18': self.i_fx18,
            '0x1e': self.i_fx1e,
            '0x29': self.i_fx29,
            '0x33': self.i_fx33,
            '0x55': self.i_fx55,
            '0x65': self.i_fx65
        }
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.memory = [0] * 4096
        self.stack = [0] * 16
        self.pc = 0x200
        self.sp = 0x00
        self.v = [0] * 16
        self.i = 0x000
        self.dt = 0
        self.st = 0
        self.draw_flag = False
        self.display = [[0] * 64 for _ in range(32)]
        self.load_rom()
        self.load_font_set()

    def update(self):
        self.fetch_opcode()
        self.execute_opcode()
        if self.dt > 0:
            self.dt -= 1
        if self.st > 0:
            self.st -= 1

    def draw(self):
        if self.draw_flag:
            pyxel.cls(0)
            display_buffer = self.display
            for r in range(32):
                for c in range(64):
                    if display_buffer[r][c] == 1:
                        pyxel.pix(c, r, 7)
        self.draw_flag = False

    def get_input(self):
        for key in self.key_map:
            if(pyxel.btn(key)):
                return self.key_map[key]

    def load_rom(self):
        rom = open("PONG2.rom", 'rb')
        hexdata = rom.read().hex()
        mem_counter = 512
        for i in range(0, len(hexdata), 2):
            self.memory[mem_counter] = int(hexdata[i:i+2], 16)
            mem_counter += 1

    def load_font_set(self):
        for digit in self.fontset:
            loc = int(digit, 16) * 5
            for byte in self.fontset[digit]:
                self.memory[loc] = byte
                loc += 1

    def fetch_opcode(self):
        self.opcode = (self.memory[self.pc] << 8) + self.memory[self.pc + 1]
        self.pc += 2


    def execute_opcode(self):
        self.operation_lookup[hex((self.opcode & 0xf000) >> 12)](self.opcode)

    def draw_sprite(self, x, y, height):
        for r in range(height):
            sprite = self.memory[self.i + r]
            sprite = [int(z) for z in format(sprite, '08b')]
            for c in range(8):
                current_val = self.display[(r + y) % 32][(c + x) % 64]
                new_val = current_val ^ sprite[c]
                if new_val != current_val:
                    self.v[0xf] = 1
                    self.display[(r + y) % 32][(c + x) % 64] = new_val

    def i_0nnn(self, opcode):
        if opcode & 0x000f == 0x0:
            self.i_00e0()
        elif opcode & 0x000f == 0xe:
            self.i_00ee()

    def i_00e0(self):
        self.draw_flag = True
        self.display = [[0] * 64 for _ in range(32)]

    def i_00ee(self):
        self.pc = self.stack[self.sp]
        self.sp -= 1

    def i_1nnn(self, opcode):
        self.pc = opcode & 0x0fff

    def i_2nnn(self, opcode):
        self.sp += 1
        self.stack[self.sp] = self.pc
        self.pc = opcode & 0x0fff

    def i_3xkk(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        value = opcode & 0x00ff
        if (self.v[reg_index] == value):
            self.pc += 2

    def i_4xkk(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        value = opcode & 0x00ff
        if (self.v[reg_index] != value):
            self.pc += 2

    def i_5xy0(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        if (self.v[reg_index_1] == self.v[reg_index_2]):
            self.pc += 2

    def i_6xkk(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        value = opcode & 0x00ff
        self.v[reg_index] = value

    def i_7xkk(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        value = opcode & 0x00ff
        self.v[reg_index] = (self.v[reg_index] + value) % 256

    def i_8xyn(self, opcode):
        self.logical_lookup[hex(opcode & 0x000f)](opcode)

    def i_8xy0(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        self.v[reg_index_1] = self.v[reg_index_2]

    def i_8xy1(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        self.v[reg_index_1] = (self.v[reg_index_1] | self.v[reg_index_2])

    def i_8xy2(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        self.v[reg_index_1] = (self.v[reg_index_1] & self.v[reg_index_2])

    def i_8xy3(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        self.v[reg_index_1] = (self.v[reg_index_1] ^ self.v[reg_index_2])

    def i_8xy4(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        sum = self.v[reg_index_1] + self.v[reg_index_2]
        if sum > 255:
            self.v[0xf] = 1
        else:
            self.v[0xf] = 0
        self.v[reg_index_1] = sum % 256

    def i_8xy5(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        if self.v[reg_index_1] >= self.v[reg_index_2]:
            self.v[0xf] = 1
        else:
            self.v[0xf] = 0
        self.v[reg_index_1] = abs(self.v[reg_index_1] - self.v[reg_index_2])

    def i_8xy6(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        self.v[0xf] = self.v[reg_index_1] % 2
        self.v[reg_index_1] >>= 1

    def i_8xy7(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        if self.v[reg_index_2] >= self.v[reg_index_1]:
            self.v[0xf] = 1
        else:
            self.v[0xf] = 0
        self.v[reg_index_1] = abs(self.v[reg_index_1] - self.v[reg_index_2])

    def i_8xye(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        self.v[0xf] = self.v[reg_index_1] // 128
        self.v[reg_index_1] <<= 1

    def i_9xy0(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        if self.v[reg_index_1] != self.v[reg_index_2]:
            self.pc += 2

    def i_annn(self, opcode):
        self.i = opcode & 0x0fff

    def i_bnnn(self, opcode):
        self.pc = self.v[0x0] + (opcode & 0x0fff)

    def i_cxkk(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        rand = random.randint(0, 255)
        value = opcode & 0x00ff
        self.v[reg_index_1] = (rand & value)

    def i_dxyn(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        height = opcode & 0x000f
        x = self.v[reg_index_1]
        y = self.v[reg_index_2]
        self.draw_flag = True
        self.draw_sprite(x, y, height)

    def i_exnn(self, opcode):
        if opcode & 0x00f0 == 0x90:
            self.i_ex9e(opcode)
        elif opcode & 0x00f0 == 0xa0:
            self.i_exa1(opcode)

    def i_ex9e(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        if self.v[reg_index] == self.get_input():
            self.pc += 2

    def i_exa1(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        if self.v[reg_index] != self.get_input():
            self.pc += 2

    def i_fxnn(self, opcode):
        self.misc_lookup[hex(opcode & 0x00ff)](opcode)

    def i_fx07(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        self.v[reg_index] = self.dt

    def i_fx0a(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        while True:
            key = self.get_input()
            if key != None:
                self.v[reg_index] = key
                break

    def i_fx15(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        self.dt = self.v[reg_index]

    def i_fx18(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        self.st = self.v[reg_index]

    def i_fx1e(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        self.i += self.v[reg_index]

    def i_fx29(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        digit = self.v[reg_index]
        self.i = digit * 5

    def i_fx33(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        val = self.v[reg_index]
        self.memory[self.i] = val // 100
        self.memory[self.i + 1] = (val % 100) // 10
        self.memory[self.i + 2] = val % 10

    def i_fx55(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        for i in range(0, reg_index + 1):
            self.memory[self.i + i] = self.v[i]

    def i_fx65(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        for i in range(0, reg_index + 1):
            self.v[i] = self.memory[self.i + i]

    

if __name__ == "__main__":
    Chip8()