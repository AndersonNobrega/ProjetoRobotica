#!/usr/bin/env python3

from ev3dev.ev3 import MediumMotor, LargeMotor, ColorSensor, Button
from Classes.Motores import *
import csv
from time import time, sleep
from os import system, remove
system('setfont Lat15-TerminusBold14')

# Motores
M_PORTA = MediumMotor('outC')
M_ESQUERDO = LargeMotor("outA")
M_DIREITO = LargeMotor("outB")

# Sensores de Cor
CL1 = ColorSensor("in1")
CL2 = ColorSensor("in2")
CL1.mode = "RGB-RAW"
CL2.mode = "RGB-RAW"

velocidade_dir = 350
velocidade_esq = 360
CL1_VERDE = []
CL2_VERDE = []

sensor1_r = []
sensor1_g = []
sensor1_b = []
sensor2_r = []
sensor2_g = []
sensor2_b = []

funcao_motores = Motores(M_ESQUERDO, M_DIREITO, M_PORTA)


def salvar(arquivo, sensor):
    try:
        remove(arquivo)
    except OSError:
        pass

    with open(arquivo, 'a+') as valores:
        tabela = csv.writer(valores)
        tabela.writerow([sensor[0][0], sensor[0][1], sensor[0][2], sensor[0][3], sensor[0][4], sensor[0][5]])
        tabela.writerow([sensor[1][0], sensor[1][1], sensor[1][2], sensor[1][3], sensor[1][4], sensor[1][5]])


def calibrar(arquivo):
    inicio = time()
    while True:
        funcao_motores.acelerar_ajustando(velocidade_dir, velocidade_esq)

        sensor1_r.append(CL1.value(0))
        sensor1_g.append(CL1.value(1))
        sensor1_b.append(CL1.value(2))

        sensor2_r.append(CL2.value(0))
        sensor2_g.append(CL2.value(1))
        sensor2_b.append(CL2.value(2))

        fim = time()
        if fim - inicio >= 2:
            sensor = [[min(sensor1_r), min(sensor1_g), min(sensor1_b), max(sensor1_r), max(sensor1_g),
                       max(sensor1_b)], [min(sensor2_r), min(sensor2_g), min(sensor2_b), max(sensor2_r), max(sensor2_g),
                                         max(sensor2_b)]]
            funcao_motores.acelerar(0, 300)
            salvar(arquivo, sensor)

            sensor1_r.clear()
            sensor1_g.clear()
            sensor1_b.clear()
            sensor2_r.clear()
            sensor2_g.clear()
            sensor2_b.clear()

            return


def main():
    botao = Button()

    print("---VERDE---")
    while True:
        if botao.enter:
            calibrar("verde.csv")
            break
    sleep(1)
    system("clear")

    print("---VERMELHO---")
    while True:
        if botao.enter:
            calibrar("vermelho.csv")
            break
    sleep(1)
    system("clear")

    print("---AZUL---")
    while True:
        if botao.enter:
            calibrar("azul.csv")
            break
    sleep(1)
    system("clear")

    print("---PRETO---")
    while True:
        if botao.enter:
            calibrar("preto.csv")
            break
    sleep(1)
    system("clear")

    print("---BRANCO---")
    while True:
        if botao.enter:
            calibrar("branco.csv")
            break


main()
