import random

class App:
    def __init__(self):
        self.memory = [0] * 4096
        self.stack = [0] * 16
        self.pc = 0x200
        self.sp = 0x00
        self.v = [0] * 16
        self.i = 0x000
        self.dt = 0
        self.st = 0
        self.draw_flag = False
        self.key_pressed = 0
        self.display = [[0] * 64 for _ in range(32)]
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
            '0x0': self._0nnn,
            '0x1': self._1nnn,
            '0x2': self._2nnn,
            '0x3': self._3xkk,
            '0x4': self._4xkk,
            '0x5': self._5xy0,
            '0x6': self._6xkk,
            '0x7': self._7xkk,
            '0x8': self._8xyn,
            '0x9': self._9xy0,
            '0xa': self._annn,
            '0xb': self._bnnn,
            '0xc': self._cxkk,
            '0xd': self._dxyn,
            '0xe': self._exnn,
            '0xf': self._fxnn
        }

        self.logical_lookup = {
            '0x0': self._8xy0,
            '0x1': self._8xy1,
            '0x2': self._8xy2,
            '0x3': self._8xy3,
            '0x4': self._8xy4,
            '0x5': self._8xy5,
            '0x6': self._8xy6,
            '0x7': self._8xy7,
            '0xe': self._8xye
        }

        self.misc_lookup = {
            '0x07': self._fx07,
            '0x0a': self._fx0a,
            '0x15': self._fx15,
            '0x18': self._fx18,
            '0x1e': self._fx1e,
            '0x29': self._fx29,
            '0x33': self._fx33,
            '0x55': self._fx55,
            '0x65': self._fx65
        }

    def run(self):
        self.load_rom()
        while True:
            self.fetch_opcode()
            self.execute_opcode()
            self.draw()

    def load_rom(self):
        rom = open("ibm.rom", 'rb')
        hexdata = rom.read().hex()
        mem_counter = 512
        for i in range(0, len(hexdata), 2):
            self.memory[mem_counter] = int(hexdata[i:i+2], 16)
            mem_counter += 1

    def draw(self):
        if self.draw_flag:
            print("Drawing graphics:")
            for r in range(32):
                for c in range(64):
                    if self.display[r][c] == 1:
                        print("x", end = "")
                    else:
                        print("0", end = "")
                print()
        self.draw_flag = False

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

    def _0nnn(self, opcode):
        if opcode & 0x000f == 0x0:
            self._00e0()
        elif opcode & 0x000f == 0xe:
            self._00ee()

    def _00e0(self):
        self.draw_flag = True
        self.display = [[0] * 64 for _ in range(32)]

    def _00ee(self):
        self.pc = self.stack[self.sp]
        self.sp -= 1

    def _1nnn(self, opcode):
        self.pc = opcode & 0x0fff

    def _2nnn(self, opcode):
        self.sp += 1
        self.stack[self.sp] = self.pc
        self.pc = opcode & 0x0fff

    def _3xkk(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        value = opcode & 0x00ff
        if (self.v[reg_index] == value):
            self.pc += 4

    def _4xkk(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        value = opcode & 0x00ff
        if (self.v[reg_index] != value):
            self.pc += 4

    def _5xy0(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        if (self.v[reg_index_1] == self.v[reg_index_2]):
            self.pc += 4

    def _6xkk(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        value = opcode & 0x00ff
        self.v[reg_index] = value

    def _7xkk(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        value = opcode & 0x00ff
        self.v[reg_index] = (self.v[reg_index] + value) % 256

    def _8xyn(self, opcode):
        self.logical_lookup[hex(opcode & 0x000f)](opcode)

    def _8xy0(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        self.v[reg_index_1] = self.v[reg_index_2]

    def _8xy1(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        self.v[reg_index_1] = (self.v[reg_index_1] | self.v[reg_index_2])

    def _8xy2(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        self.v[reg_index_1] = (self.v[reg_index_1] & self.v[reg_index_2])

    def _8xy3(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        self.v[reg_index_1] = (self.v[reg_index_1] ^ self.v[reg_index_2])

    def _8xy4(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        sum = self.v[reg_index_1] + self.v[reg_index_2]
        if sum > 255:
            self.v[0xf] = 1
        else:
            self.v[0xf] = 0
        self.v[reg_index_1] = sum % 256

    def _8xy5(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        if self.v[reg_index_1] >= self.v[reg_index_2]:
            self.v[0xf] = 1
        else:
            self.v[0xf] = 0
        self.v[reg_index_1] = abs(self.v[reg_index_1] - self.v[reg_index_2])

    def _8xy6(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        self.v[0xf] = self.v[reg_index_1] % 2
        self.v[reg_index_1] >>= 1

    def _8xy7(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        if self.v[reg_index_2] >= self.v[reg_index_1]:
            self.v[0xf] = 1
        else:
            self.v[0xf] = 0
        self.v[reg_index_1] = abs(self.v[reg_index_1] - self.v[reg_index_2])

    def _8xye(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        self.v[0xf] = self.v[reg_index_1] // 128
        self.v[reg_index_1] <<= 1

    def _9xy0(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        if self.v[reg_index_1] != self.v[reg_index_2]:
            self.pc += 4

    def _annn(self, opcode):
        self.i = opcode & 0x0fff

    def _bnnn(self, opcode):
        self.pc = self.v[0x0] + (opcode & 0x0fff)

    def _cxkk(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        rand = random.randint(0, 255)
        value = opcode & 0x00ff
        self.v[reg_index_1] = (rand & value)

    def _dxyn(self, opcode):
        reg_index_1 = (opcode & 0x0f00) >> 8
        reg_index_2 = (opcode & 0x00f0) >> 4
        height = opcode & 0x000f
        x = self.v[reg_index_1]
        y = self.v[reg_index_2]
        self.draw_flag = True
        self.draw_sprite(x, y, height)

    def _exnn(self, opcode):
        if opcode & 0x00f0 == 0x90:
            self._ex9e(opcode)
        elif opcode & 0x00f0 == 0xa0:
            self._exa1(opcode)

    def _ex9e(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        if self.v[reg_index] == self.key_pressed:
            self.pc += 4

    def _exa1(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        if self.v[reg_index] != self.key_pressed:
            self.pc += 4

    def _fxnn(self, opcode):
        self.misc_lookup[hex(opcode & 0x00ff)](opcode)

    def _fx07(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        self.v[reg_index] = self.dt

    def _fx0a(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        while True:
            key = self.get_input()
            if key != None:
                self.v[reg_index] = key
                break

    def _fx15(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        self.dt = self.v[reg_index]

    def _fx18(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        self.st = self.v[reg_index]

    def _fx1e(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        self.i += self.v[reg_index]

    def _fx29(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        character = self.v[reg_index]
        self.i = self.get_sprite_address(character)

    def _fx33(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        val = self.v[reg_index]
        self.memory[self.i] = val // 100
        self.memory[self.i + 1] = (val % 100) // 10
        self.memory[self.i + 2] = val % 10

    def _fx55(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        for i in range(0, reg_index + 1):
            self.memory[self.i + i] = self.v[i]

    def _fx65(self, opcode):
        reg_index = (opcode & 0x0f00) >> 8
        for i in range(0, reg_index + 1):
            self.v[i] = self.memory[self.i + i]

    

if __name__ == "__main__":
    app = App()
    app.run()