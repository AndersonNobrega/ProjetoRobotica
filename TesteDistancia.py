#!/usr/bin/env python3

import ev3dev.ev3 as ev3
# from ev3dev.ev3 import *
from time import sleep

M_ESQUERDO = ev3.LargeMotor('outB')
M_DIREITO = ev3.LargeMotor('outC')
CL = ev3.ColorSensor('in1')
CL.mode = 'COL-COLOR'
PROX1 = ev3.InfraredSensor('in2')  # DIREITA
PROX2 = ev3.InfraredSensor('in3')  # ESQUERDA
PROX1.mode = 'IR-PROX'
PROX2.mode = 'IR-PROX'
GYRO = ev3.GyroSensor('in4')
GYRO.mode = 'TILT-ANG'
ang_atual = 0
VELOCIDADE_CURVA = 300
VELOCIDADE_ATUAL = 400
velocidade_nova_dir = 0
velocidade_nova_esq = 0
erro = 0
KP = 1.3

def corrigir_percurso(valor_distancia1, valor_distancia2):
    #Faz correção do percurso de acordo com os valores de distancia dos sensores
    #e retorna velocidade nova pro motor
    distancia_direita = valor_distancia1
    distancia_esquerda = valor_distancia2
    erro = distancia_direita - distancia_esquerda
    s = KP * erro
    velocidade_nova_dir = VELOCIDADE_ATUAL - s
    velocidade_nova_esq = VELOCIDADE_ATUAL + s

    return velocidade_nova_esq, velocidade_nova_dir

def acelerar(velocidade, tempo=0):
    #Se n receber tempo, roda infinitamente
    if tempo == 0:
        M_ESQUERDO.run_forever(speed_sp=velocidade, stop_action='brake')
        M_DIREITO.run_forever(speed_sp=velocidade, stop_action='brake')
    else:
        M_ESQUERDO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        M_DIREITO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')

def acelerar_ajustando(dir, esq):
    #Acelera infinitamente, mas com velocidade diferente em cada motor
    M_ESQUERDO.run_forever(speed_sp=esq)
    M_DIREITO.run_forever(speed_sp=dir)

def fazer_curva_esq(velocidade):
    #Faz curva pra esquerda no proprio eixo do robo
    M_ESQUERDO.run_forever(speed_sp=velocidade*-1)
    M_DIREITO.run_forever(speed_sp=velocidade)

def fazer_curva_dir(velocidade):
    # Faz curva pra direita no proprio eixo do robo
    M_ESQUERDO.run_forever(speed_sp=velocidade)
    M_DIREITO.run_forever(speed_sp=velocidade*-1)

def parar_motor():
    M_ESQUERDO.stop(stop_action="hold")
    M_DIREITO.stop(stop_action="hold")

def esperar():
    #Espera o motor terminar de roda pra fazer proxima acao
    M_ESQUERDO.wait_while('running')
    M_DIREITO.wait_while('running')

def main():
    acelerar(400) #Depois de fazer curva, anda um pouco antes de voltar no loop
    sleep(3) #Espera 3 segundos pra voltar ao loop
    while True:
        esq, dir = corrigir_percurso(PROX1.value(), PROX2.value()) #Novos valores de velocidade
        acelerar_ajustando(dir, esq) #Vai mudando a velocidade do robo durante o percurso
        if CL.value() == 3: #Verde
            sleep(0.4)
            fazer_curva_esq(VELOCIDADE_CURVA)
            break
        if CL.value() == 5:  #Vermelho
            sleep(0.4)
            fazer_curva_dir(VELOCIDADE_CURVA)
            break
        if CL.value() == 2: #Azul
            break
    sleep(1.45) #Faz curva por 1 segundo

while True:
    main()