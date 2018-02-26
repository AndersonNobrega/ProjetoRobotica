#!/usr/bin/env python3

from ev3dev.ev3 import MediumMotor, LargeMotor, UltrasonicSensor, ColorSensor

from Classes.Motores import *
from Classes.PID import *

# Motores
M_PORTA = MediumMotor('outB')
M_DIREITO = LargeMotor("outD")
M_ESQUERDO = LargeMotor("outC")

# Sensores de Cor
CL1 = ColorSensor("in1")
CL2 = ColorSensor("in2")
CL1.mode = "COL-COLOR"
CL2.mode = "COL-COLOR"

# Sensores ultrasonicos
PROX1 = UltrasonicSensor("in3")  # Direita
PROX2 = UltrasonicSensor("in4")  # Esquerda
PROX1.mode = "US-DIST-CM"
PROX2.mode = "US-DIST-CM"

# Variaveis usadas durante o programa
DISTANCIA_BONECOS = 18
VELOCIDADE_CURVA = 300
VELOCIDADE_ATUAL = 350
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

funcao_motores = Motores(M_DIREITO, M_ESQUERDO, M_PORTA)


def cor_preto(tempo):
    # Curva quando tiver na cor preta
    funcao_motores.fazer_curva_dir_roda(VELOCIDADE_CURVA, tempo)
    while CL1.value() == PRETO:
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        velocidade_esq, velocidade_dir = PID.controle_proporcional(CL1.value(),
                                                                   CL2.value())  # Novos valores de velocidade
        funcao_motores.acelerar_ajustando(velocidade_dir, velocidade_esq)


def retornar_cor(cor):
    # Cor anterior = indice 0
    # Cor atual = indice 1

    if cor_caminho[1] != "":
        cor_caminho[0] = cor_caminho[1]
        cor_caminho[1] = cor
    elif cor_caminho[0] == "":
        cor_caminho[1] = cor


def parar_motor():
    M_DIREITO.stop()
    M_ESQUERDO.stop()


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
    # Verifica se o caminho que ele seguiu n e um dead end
    if cor_caminho[0] != "" and cor_caminho[1] in cores and \
                    cor_caminho[0] != "PRETO" and relacao_cores[cor_caminho[0]] == "":
        return True


def achou_cor(cor, constante_cor, indice_cor):
    # Quando achar uma cor(Azul, Vermelho ou Verde), verifique se n foi so um bug no sensor e faca uma curva
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 900)
    if not CL1.value() == constante_cor:
        funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 900)
        while (CL1.value() == VERMELHO) or (CL1.value() == VERDE) or (CL1.value() == AMARELO):
            funcao_motores.acelerar_ajustando(-1 * VELOCIDADE_ATUAL, -1 * VELOCIDADE_ATUAL)
            funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 500)
        return
    retornar_cor(cor)
    if aprender_caminho():
        define_direcao(cor_caminho[0])

    sem_direcao(cor, indice_cor)


def sem_direcao(cor, indice_cor):
    # Quando nao tem uma direcao definida ainda para a cor
    if relacao_cores[cor] == "":
        lista_valores[indice_cor] += 1
        direita(1000)
    else:
        curva(relacao_cores[cor])


def percurso():
    while True:
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        PID.controle_proporcional(PROX1.value() / 10, PROX2.value() / 10)
        funcao_motores.acelerar_ajustando(PID.velocidade_dir, PID.velocidade_esq)

        if CL1.value() == VERDE:
            achou_cor("VERDE", VERDE, 1)
            break
        elif CL1.value() == VERMELHO:
            achou_cor("VERMELHO", VERMELHO, 0)
            break
        elif CL1.value() == AMARELO:
            achou_cor("AMARELO", AMARELO, 2)
            break
        elif CL1.value() == PRETO:
            funcao_motores.acelerar(VELOCIDADE_ATUAL, 900)
            if not CL1.value() == PRETO:
                break
            else:
                retornar_cor("PRETO")
                cor_preto(2000)
    while (CL1.value() == VERMELHO) or (CL1.value() == VERDE) or (CL1.value() == AMARELO):
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        funcao_motores.acelerar(VELOCIDADE_ATUAL, 300)
        velocidade_esq, velocidade_dir = PID.controle_proporcional(PROX1.value() / 10, PROX2.value() / 10)
        funcao_motores.acelerar_ajustando(velocidade_dir, velocidade_esq)


def main():
    while True:
        percurso()


if __name__ == '__main__':
    main()
