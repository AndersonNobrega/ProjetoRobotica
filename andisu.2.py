#!/usr/bin/env python3

import ev3dev.ev3 as ev3
from ev3dev.ev3 import *
from time import sleep

LIMIAR_DE_COR = 5
TEMPO_IR = 100
TEMPO_CURVA = 1000
TEMPO_FECHAR_GARRA = 700
TEMPO_ABRIR_GARRA = 1400
VELOCIDADE_IR = -500
VELOCIDADE_VOLTAR = 500
INTENSIDADE_DA_CURVA = 1500
VELOCIDADE_ABRIR_GARRA = -500
VELOCIDADE_FECHAR_GARRA = 500

m_esquerdo = ev3.LargeMotor('outA')
m_direito = ev3.LargeMotor('outB')
m_garra = ev3.Motor('outC')
cl = ev3.ColorSensor('in1')
cl.mode='COL-AMBIENT'
tempo_voltar = 0

def acelerar(tempo, direcao):
    m_esquerdo.run_timed(time_sp=tempo, speed_sp=direcao , stop_action='brake')
    m_direito.run_timed(time_sp=tempo, speed_sp=direcao , stop_action='brake')
    m_esquerdo.wait_while('running')
    m_direito.wait_while('running')

def curva_esquerda(tempo, direcao, curva):
    m_esquerdo.run_timed(time_sp=(tempo + curva), speed_sp=direcao, stop_action='brake')
    m_direito.run_timed(time_sp=tempo, speed_sp=direcao , stop_action='brake')
    m_esquerdo.wait_while('running')
    m_direito.wait_while('running')

def curva_direita(tempo, direcao, curva):
    m_esquerdo.run_timed(time_sp=tempo, speed_sp=direcao , stop_action='brake')
    m_direito.run_timed(time_sp=(tempo + curva), speed_sp=direcao , stop_action='brake')
    m_esquerdo.wait_while('running')
    m_direito.wait_while('running')

def garra(tempo, direcao):
    m_garra.run_timed(time_sp=tempo, speed_sp=direcao, stop_action='brake')
    m_garra.wait_while('running')

while True:
    cl.value() > LIMIAR_DE_COR

    acelerar(TEMPO_IR, VELOCIDADE_IR)
    tempo_voltar += TEMPO_IR


garra(TEMPO_FECHAR_GARRA, VELOCIDADE_FECHAR_GARRA)
sleep(1)
cl.mode='COL-COLOR'
sleep(1)

if cl.value() == 6:
    ev3.Sound.beep()
    garra(TEMPO_FECHAR_GARRA, VELOCIDADE_FECHAR_GARRA)
    acelerar(tempo_voltar, VELOCIDADE_VOLTAR)
    garra(TEMPO_ABRIR_GARRA, VELOCIDADE_ABRIR_GARRA)


elif cl.value() == 0 or cl.value() == 1:
    ev3.Sound.speak('Welcome to the E V 3 dev project! EEEEEEEEERRRRROOOOOOUUUUUUUUUUU')
    garra(TEMPO_FECHAR_GARRA, VELOCIDADE_FECHAR_GARRA)
    curva_direita(TEMPO_CURVA, VELOCIDADE_IR, INTENSIDADE_DA_CURVA)
    garra(TEMPO_ABRIR_GARRA, VELOCIDADE_ABRIR_GARRA)
    curva_direita(TEMPO_CURVA, VELOCIDADE_VOLTAR, INTENSIDADE_DA_CURVA)
    acelerar(tempo_voltar, VELOCIDADE_VOLTAR)