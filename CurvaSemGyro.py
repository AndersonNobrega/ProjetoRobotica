#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import logging

# Script usando tempo definido pra fazer curva e assumindo que as 3 cores podem ter msm direcao

# Variaveis dos sensores e motores, e os modos dos sensores
M_ESQUERDO = ev3.LargeMotor("outC")
M_DIREITO = ev3.LargeMotor("outD")
CL = ev3.ColorSensor("in1")
CL.mode = "COL-COLOR"
PROX1 = ev3.InfraredSensor("in2")
PROX2 = ev3.InfraredSensor("in3")
PROX3 = ev3.InfraredSensor("in4")
PROX1.mode = "IR-PROX"
PROX2.mode = "IR-PROX"
PROX3.mode = "IR-PROX"

# Variaveis usadas durante o programa
FORMATO_LOG = "%(asctime)s - %(funcName) -> %(message)s"
VELOCIDADE_CURVA = 300
VELOCIDADE_ATUAL = 400
KP = 1.5
VERDE = 3
VERMELHO = 5
AZUL = 2
PRETO = 1
lista_valores = [0, 0, 0]  # indice 0 - VERMELHO, indice 1 - VERDE, indice 2 - AZUL
cor_caminho = ["", ""]
cores = ["VERMELHO", "AZUL", "VERDE"]
relacao_cores = {"VERMELHO": "", "VERDE": "", "AZUL": ""}

# Criacao de um arquivo .log
logging.basicConfig(filename="Robo.log", level=logging.DEBUG, format=FORMATO_LOG, datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger()


def corrigir_percurso(valor_distancia1, valor_distancia2):
    # Faz correção do percurso de acordo com os valores de distancia dos sensores
    # e retorna velocidade nova pro motor
    distancia_direita = valor_distancia1
    distancia_esquerda = valor_distancia2
    erro = distancia_direita - distancia_esquerda
    s = KP * erro
    velocidade_nova_dir = VELOCIDADE_ATUAL - s
    velocidade_nova_esq = VELOCIDADE_ATUAL + s

    return velocidade_nova_esq, velocidade_nova_dir


def acelerar(velocidade, tempo=0):
    # Se n receber tempo, roda infinitamente
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


def acelerar_ajustando(velocidade_direita, velocidade_esquerda):
    # Acelera infinitamente, mas com velocidade diferente em cada motor
    M_ESQUERDO.run_forever(speed_sp=velocidade_esquerda)
    M_DIREITO.run_forever(speed_sp=velocidade_direita)


def fazer_curva_dir(velocidade, tempo):
    # Faz curva pra esquerda no proprio eixo do robo
    M_ESQUERDO.run_timed(time_sp=tempo, speed_sp=velocidade * -1, stop_action='brake')
    M_DIREITO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
    M_ESQUERDO.wait_while('running')
    M_DIREITO.wait_while('running')


def fazer_curva_esq(velocidade, tempo):
    # Faz curva pra direita no proprio eixo do robo
    M_ESQUERDO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
    M_DIREITO.run_timed(time_sp=tempo, speed_sp=velocidade * -1, stop_action='brake')
    M_ESQUERDO.wait_while('running')
    M_DIREITO.wait_while('running')


def cor_preto():
    # Curva quando tiver na cor preta
    fazer_curva_dir(VELOCIDADE_CURVA, 3000)
    while CL.value() == PRETO:
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        velocidade_esq, velocidade_dir = corrigir_percurso(PROX1.value(),
                                                           PROX2.value())  # Novos valores de velocidade
        acelerar_ajustando(velocidade_dir, velocidade_esq)


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
        direita()
    elif sentido == "ESQUERDA":
        esquerda()
    else:
        return


def esquerda():
    # Faz curva de 90 graus para a esquerda
    acelerar(VELOCIDADE_ATUAL, 1900)
    fazer_curva_esq(VELOCIDADE_CURVA, 1500)


def direita():
    # Faz curva de 90 graus para direita
    acelerar(VELOCIDADE_ATUAL, 1900)
    fazer_curva_dir(VELOCIDADE_CURVA, 1500)


def aprender_caminho():
    # Verifica se o caminho que ele seguiu n e um dead end
    if cor_caminho[0] != "" and cor_caminho[1] in cores and \
                    cor_caminho[0] != "PRETO" and relacao_cores[cor_caminho[0]] == "":
        return True


def achou_cor(cor, constante_cor, indice_cor):
    # Quando achar uma cor(Azul, Vermelho ou Verde), verifique se n foi so um bug no sensor e faca uma curva
    acelerar(VELOCIDADE_ATUAL, 300)
    if not CL.value() == constante_cor:
        return
    retornar_cor(cor)
    if aprender_caminho():
        define_direcao(cor_caminho[0])

    sem_direcao(cor, indice_cor)


def sem_direcao(cor, indice_cor):
    # Quando nao tem uma direcao definida ainda para a cor
    if relacao_cores[cor] == "":
        lista_valores[indice_cor] += 1
        direita()
    else:
        curva(relacao_cores[cor])


def percurso():
    # Funcao principal do programa com a estrutura que o robo deve seguir do codigo
    logger.info("%s : %s - %s : %s - %s : %s" % ("VERMELHO", relacao_cores["VERMELHO"], "VERDE",
                                                 relacao_cores["VERDE"], "AZUL", relacao_cores["AZUL"]))
    while True:
        velocidade_esq, velocidade_dir = corrigir_percurso(PROX1.value(), PROX2.value())  # Novos valores de velocidade
        acelerar_ajustando(velocidade_dir, velocidade_esq)  # Vai mudando a velocidade do robo durante o percurso
        if CL.value() == VERDE:
            achou_cor("VERDE", VERDE, 1)
            break
        elif CL.value() == VERMELHO:
            achou_cor("VERMELHO", VERMELHO, 0)
            break
        elif CL.value() == AZUL:
            achou_cor("AZUL", AZUL, 2)
            break
        elif CL.value() == PRETO:
            acelerar(VELOCIDADE_ATUAL, 300)
            if not CL.value() == PRETO:
                break
            retornar_cor("PRETO")
            cor_preto()
    while (CL.value() == VERMELHO) or (CL.value() == VERDE) or (CL.value() == AZUL):
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        velocidade_esq, velocidade_dir = corrigir_percurso(PROX1.value(), PROX2.value())  # Novos valores de velocidade
        acelerar_ajustando(velocidade_dir, velocidade_esq)


while True:
    percurso()
