#!/usr/bin/env python3

import ev3dev.ev3 as ev3
from ev3dev.ev3 import *
from time import sleep, time

M_ESQUERDO = ev3.LargeMotor('outA')
M_DIREITO = ev3.LargeMotor('outB')
#PORTA = ev3.LargeMotor('outD')

def acelerar(velocidade=0, tempo=0):
    if tempo == 0:
        M_ESQUERDO.run_forever(speed_sp=velocidade, stop_action='brake')
        M_DIREITO.run_forever(speed_sp=velocidade, stop_action='brake')
        M_ESQUERDO.wait_while('running')
        M_DIREITO.wait_while('running')
    else:
        M_ESQUERDO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        M_DIREITO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        M_ESQUERDO.wait_while('running')
        M_DIREITO.wait_while('running')
#acelerar(-500)
#sleep(5)
#M_DIREITO.run_to_rel_pos(position_sp=920, speed_sp=500, stop_action="hold")
#M_DIREITO.wait_while('running')
#PORTA.run_timed(time_sp=2200, speed_sp=-100, stop_action='brake')

acelerar(-500)