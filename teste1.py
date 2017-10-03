#!/usr/bin/env python3

import ev3dev.ev3 as ev3

M_ESQUERDO = ev3.LargeMotor('outB')
M_DIREITO = ev3.LargeMotor('outA')
CL = ev3.ColorSensor('in1')
CL.mode = 'COL-COLOR'
PROX1 = ev3.InfraredSensor('in2')  # DIREITA
PROX2 = ev3.InfraredSensor('in3')  # ESQUERDA
PROX1.mode = 'IR-PROX'
PROX2.mode = 'IR-PROX'
GYRO = ev3.GyroSensor('in4')
GYRO.mode = 'TILT-ANG'

VELOCIDADE_CURVA = 300
VELOCIDADE_ATUAL = 400
KP = 1.3
VERDE = 3
VERMELHO = 5
AZUL = 2

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
        M_ESQUERDO.wait_while('running')
        M_DIREITO.wait_while('running')
    else:
        M_ESQUERDO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        M_DIREITO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        M_ESQUERDO.wait_while('running')
        M_DIREITO.wait_while('running')

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

def main():
    while True:
        velocidade_esq, velocidade_dir = corrigir_percurso(PROX1.value(), PROX2.value()) #Novos valores de velocidade
        acelerar_ajustando(velocidade_dir, velocidade_esq) #Vai mudando a velocidade do robo durante o percurso
        if CL.value() == VERDE: #Verde
            acelerar(VELOCIDADE_ATUAL, 400)     #Espera 0.3 segundos antes de fazer curva
            ang_atual = GYRO.value() #Angulo de quando o robo entrou na cor
            while True:
                fazer_curva_esq(VELOCIDADE_CURVA)
                if ang_atual-85 >= GYRO.value():
                    break
            break
        if CL.value() == VERMELHO:  #Vermelho
            acelerar(VELOCIDADE_ATUAL, 400)    #Espera 0.3 segundos antes de fazer curva
            ang_atual = GYRO.value() #Angulo de quando o robo entrou na cor
            while True:
                fazer_curva_dir(VELOCIDADE_CURVA)
                if ang_atual+85 <= GYRO.value():
                    break
            break
        if CL.value() == AZUL: #Azul
            break
    while (CL.value() == VERMELHO) or (CL.value() == VERDE) or (CL.value() == AZUL):
        #Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        velocidade_esq, velocidade_dir = corrigir_percurso(PROX1.value(), PROX2.value())  # Novos valores de velocidade
        acelerar_ajustando(velocidade_dir, velocidade_esq)

while True:
    main()