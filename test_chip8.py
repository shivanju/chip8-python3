import pytest
import random

from cpu import CPU

@pytest.fixture
def cpu():
    return CPU()

def test_00e0(cpu):
    cpu.display[0][0] = 1
    cpu.i_00e0()
    assert sum([sum(x) for x in cpu.display]) == 0
    assert cpu.draw_flag == True

def test_00ee(cpu):
    cpu.sp = 0x1
    cpu.stack[cpu.sp] = 0x220
    cpu.i_00ee()
    assert cpu.sp == 0x0
    assert cpu.pc == 0x220

def test_1nnn(cpu):
    cpu.i_1nnn(0x1345)
    assert cpu.pc == 0x345

def test_2nnn(cpu):
    cpu.i_2nnn(0x2456)
    assert cpu.sp == 1
    assert cpu.stack[cpu.sp] == 0x200
    assert cpu.pc == 0x456

def test_3xkk(cpu):
    cpu.v[1] = 0x1d
    cpu.i_3xkk(0x311d)
    assert cpu.pc == 0x202
    cpu.i_3xkk(0x311e)
    assert cpu.pc == 0x202

def test_4xkk(cpu):
    cpu.v[1] = 0x1d
    cpu.pc = 0x200
    cpu.i_4xkk(0x311e)
    assert cpu.pc == 0x202
    cpu.i_4xkk(0x311d)
    assert cpu.pc == 0x202

def test_6xkk(cpu):
    cpu.i_6xkk(0x61ab)
    assert cpu.v[0x1] == 0xab

def test_7xkk(cpu):
    cpu.i_7xkk(0x7112)
    assert cpu.v[0x1] == 0x12
    cpu.i_7xkk(0x71ff)
    assert cpu.v[0x1] == 0x11

def test_8xy0(cpu):
    cpu.v[0x1] = 0xab
    cpu.i_8xy0(0x8010)
    assert cpu.v[0x0] == 0xab

def test_annn(cpu):
    cpu.i_annn(0xa21e)
    assert cpu.i == 0x21e

