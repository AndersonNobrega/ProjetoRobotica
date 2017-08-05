# !/usr/bin/env python3

"""
Coisas pra fazer:
Colocar as classes em outro arquivo; -> falta verificar se importou corretamente os metodos
Fazer um algoritmo so pra aprender as cores;
Ler essas cores no script principal e fazer a relação correta;
"""
import ev3dev.ev3 as ev3
from ev3dev.ev3 import *
from time import sleep, time
from Robo import Robo, Sensores

"""
M_ESQUERDO = ev3.LargeMotor('outA')
M_DIREITO = ev3.LargeMotor('outB')
M_GARRA = ev3.Motor('outC')
"""
IR1 = ev3.InfraredSensor() #colocar porta do sensor
IR1.mode = 'IR-PROX'
IR2 = ev3.InfraredSensor() #colocar porta do sensor
IR2.mode = 'IR-PROX'

def main():
    robo1 = Robo()
    sensores1 = Sensores()

    Sensores.verifica_distancia(IR1.value(), IR2.value())
    #chamar função curva tanto pra reajustar posição do robo
    #quanto pra fazer curva na cor com sleep(2.5 ou 3) pra fazer curva certa
    
main()