#!/usr/bin/env python3

from ev3dev.ev3 import *

from Classes.Motores import *
from Classes.PID import *


# Motores
M_PORTA = LargeMotor("outB")
M_DIREITO = LargeMotor("outC")
M_ESQUERDO = LargeMotor("outD")

# Sensores de Cor
CL1 = ColorSensor("in1")
CL2 = ColorSensor("in2")
CL1.mode = "COL-COLOR"
CL2.mode = "COL-COLOR"

# Sensores ultrasonicos
'''PROX1 = UltrasonicSensor("in1")  # Direita
PROX2 = UltrasonicSensor("in4")  # Esquerda
PROX1.mode = "US-DIST-CM"
PROX2.mode = "US-DIST-CM"
'''

# Sensores infravermelho
INFRA1= InfraredSensor("in3")
INFRA2 = InfraredSensor("in4")
INFRA1.mode = "IR-PROX"
INFRA2.mode = "IR-PROX"


# Variaveis usadas durante o programa
DISTANCIA_BONECOS = 18
VELOCIDADE_CURVA = 300
VELOCIDADE_ATUAL = velocidade_dir = velocidade_esq = 350
KP = 1.9
PRETO = 1
AZUL = 2
VERDE = 3
AMARELO = 4
VERMELHO = 5
BRANCO = 6
quant_bonecos = 0
lista_valores = [0, 0, 0]  # indice 0 - VERMELHO, indice 1 - VERDE, indice 2 - AMARELO
cor_caminho = ["", ""]
cores = ["VERMELHO", "AMARELO", "VERDE"]
relacao_cores = {"VERMELHO": "", "VERDE": "", "AMARELO": ""}
flag_parar = False
final = False

funcao_motores = Motores(M_ESQUERDO, M_DIREITO, M_PORTA)


def controle_proporcional(sensor1, sensor2):
    # Faz correção do percurso de acordo com os valores de distancia dos sensores
    KP = 1.7
    try:
        distancia_direita = sensor1
        distancia_esquerda = sensor2
        erro = distancia_direita - distancia_esquerda
    except ValueError:
        erro = 0
    finally:
        s = KP * erro
        velocidade_nova_dir = VELOCIDADE_ATUAL - s
        velocidade_nova_esq = VELOCIDADE_ATUAL + s

    return velocidade_nova_esq, velocidade_nova_dir
def controle_proporcional(sensor1, sensor2):
    KP = 1.9
    # Faz correção do percurso de acordo com os valores de distancia dos sensores
    try:
        distancia_direita = sensor1
        distancia_esquerda = sensor2
        erro = distancia_direita - distancia_esquerda
    except ValueError:
        erro = 0
    finally:
        s = KP * erro
        velocidade_dir -= s
        velocidade_esq += s

def cor_preto(tempo):
    global velocidade_dir, velocidade_esq
    # Curva quando tiver na cor preta
    funcao_motores.fazer_curva_dir_roda(VELOCIDADE_CURVA, tempo)
    while CL1.value() == PRETO and CL2.value() == PRETO:
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        PID.controle_proporcional(CL1.value(), CL2.value())  # Novos valores de velocidade
        funcao_motores.acelerar_ajustando(velocidade_dir, velocidade_esq)



def retornar_cor(cor):
    # Cor anterior = indice 0
    # Cor atual = indice 1

    if cor_caminho[1] != "":
        cor_caminho[0] = cor_caminho[1]
        cor_caminho[1] = cor
    elif cor_caminho[0] == "":
        cor_caminho[1] = cor


def define_direcao(cor):
    # Procura achar a direcao da cor
    if cor == "VERMELHO":
        index = 0
    elif cor == "VERDE":
        index = 1
    else:
        index = 2

    if lista_valores[index] == 1:
        relacao_cores[cor] = "DIREITA"
    elif lista_valores[index] == 2:
        relacao_cores[cor] = "MEIO"
    elif lista_valores[index] == 3:
        relacao_cores[cor] = "ESQUERDA"


def curva(sentido):
    # Verifica o caminho que deve seguir
    if sentido == "DIREITA":
        direita(1000)
    elif sentido == "ESQUERDA":
        esquerda(1000)
    else:
        return


def esquerda(tempo):
    # Faz curva de 90 graus para a esquerda
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1900)
    funcao_motores.fazer_curva_esq_roda(VELOCIDADE_CURVA, tempo)


def direita(tempo):
    # Faz curva de 90 graus para direita
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1900)
    funcao_motores.fazer_curva_dir_roda(VELOCIDADE_CURVA, tempo)


def aprender_caminho():
    # Verifica se o caminho qu
    # e ele seguiu n e um dead end
    if cor_caminho[0] != "" and cor_caminho[1] in cores and \
                    cor_caminho[0] != "PRETO" and relacao_cores[cor_caminho[0]] == "":
        return True

def sem_direcao(cor, indice_cor):
    # Quando nao tem uma direcao definida ainda para a cor
    if relacao_cores[cor] == "":
        lista_valores[indice_cor] += 1
        direita(1000)
    else:
        curva(relacao_cores[cor])

def ajustar_na_cor(constante_cor):
    while True:
        funcao_motores.acelerar_esq(-1 * VELOCIDADE_ATUAL)
        funcao_motores.acelerar_dir(-1 * VELOCIDADE_ATUAL)

        if CL1.value() != constante_cor:
            funcao_motores.acelerar(VELOCIDADE_ATUAL*(-1), 1100)
            funcao_motores.fazer_curva_esq_roda(VELOCIDADE_ATUAL, 600)
        if CL2.value() != constante_cor:
            funcao_motores.acelerar(VELOCIDADE_ATUAL*(-1), 1100)
            funcao_motores.fazer_curva_dir_roda(VELOCIDADE_ATUAL, 600)


def verifica_cor(cor, constante_cor, indice_cor):

    temp1 = CL1.value()
    temp2 = CL2.value()
    if temp1 != temp2:
        funcao_motores.acelerar_dir(VELOCIDADE_ATUAL * (-1), 500)
        funcao_motores.acelerar_esq(VELOCIDADE_ATUAL * (-1), 500)
        ajustar_na_cor(constante_cor)
    if aprender_caminho():
        define_direcao(cor_caminho[0])

    sem_direcao(cor, indice_cor)


def main():
    global velocidade_dir, velocidade_esq

    while True:
        velocidade_dir, velocidade_esq = controle_proporcional(INFRA1.value(), INFRA2.value())
        funcao_motores.acelerar_ajustando(velocidade_dir,velocidade_esq)
        if CL1.value() == VERDE and CL2.value() == VERDE:
            verifica_cor("VERDE", VERDE, 1)
            break
        elif CL1.value() == VERMELHO and CL2.value() == VERMELHO:
            verifica_cor("VERMELHO", VERMELHO, 0)
            break
        elif CL1.value() == AMARELO and CL2.value() == AMARELO:
            verifica_cor("AMARELO", AMARELO, 2)
            break
        elif CL1.value() == PRETO and CL2.value() == PRETO:
            funcao_motores.acelerar(VELOCIDADE_ATUAL, 100)
            funcao_motores.acelerar(0, 400)

            if not CL1.value() == PRETO and not CL2.value() == PRETO:
                funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 500)
                break
            else:
                retornar_cor("PRETO")
                cor_preto(2300)


while True:
    main()
