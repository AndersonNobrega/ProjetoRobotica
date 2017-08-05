#!/usr/bin/env python3

import ev3dev.ev3 as ev3
from ev3dev.ev3 import *
from time import sleep

mtrEsquerdo = ev3.LargeMotor('outA')
mtrDireito = ev3.LargeMotor('outB')
m_garra = ev3.Motor('outC')
cl = ev3.ColorSensor('in1')
cl.mode='COL-AMBIENT'

def acelerar():
    
    mtrEsquerdo.run_timed(time_sp=500, speed_sp=-500, stop_action='brake')
    mtrDireito.run_timed(time_sp=500, speed_sp=-500, stop_action='brake')
    mtrEsquerdo.wait_while('running')
    mtrDireito.wait_while('running')

while True:
    acelerar()