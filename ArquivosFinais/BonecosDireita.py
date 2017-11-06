#!/usr/bin/env python3

import ev3dev.ev3 as ev3
from time import time

# Variaveis dos sensores e motores, e os modos dos sensores
M_PORTA = ev3.LargeMotor('outB')
M_DIREITO = ev3.LargeMotor("outC")
M_ESQUERDO = ev3.LargeMotor("outD")
CL = ev3.ColorSensor("in1")
CL.mode = "COL-COLOR"
PROX1 = ev3.InfraredSensor("in2")  # Direita
PROX2 = ev3.InfraredSensor("in3")  # Esquerda
PROX3 = ev3.UltrasonicSensor("in4")
PROX1.mode = "IR-PROX"
PROX2.mode = "IR-PROX"
PROX3.mode = "US-DIST-CM"

# Variaveis usadas durante o programa
DISTANCIA_BONECOS = 20
VELOCIDADE_CURVA = 300
VELOCIDADE_ATUAL = 400
KP = 1.7
VERDE = 3
VERMELHO = 5
AZUL = 2
PRETO = 1
lista_valores = [0, 0, 0]  # indice 0 - VERMELHO, indice 1 - VERDE, indice 2 - AZUL
cor_caminho = ["", ""]
cores = ["VERMELHO", "AZUL", "VERDE"]
relacao_cores = {"VERMELHO": "", "VERDE": "", "AZUL": ""}
flag_parar = False


def corrigir_percurso():
    # Faz correção do percurso de acordo com os valores de distancia dos sensores
    # e retorna velocidade nova pro motor
    try:
        distancia_direita = PROX1.value()
        distancia_esquerda = PROX2.value()
        erro = distancia_direita - distancia_esquerda
    except ValueError:
        erro = 0
    finally:
        s = KP * erro
        velocidade_nova_dir = VELOCIDADE_ATUAL - s
        velocidade_nova_esq = VELOCIDADE_ATUAL + s

    return velocidade_nova_esq, velocidade_nova_dir


def acelerar(velocidade, tempo=0):
    # Se n receber tempo, roda infinitamente
    if tempo == 0:
        M_DIREITO.run_forever(speed_sp=velocidade, stop_action='brake')
        M_ESQUERDO.run_forever(speed_sp=velocidade, stop_action='brake')
        M_DIREITO.wait_while('running')
        M_ESQUERDO.wait_while('running')
    else:
        M_DIREITO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        M_ESQUERDO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        M_DIREITO.wait_while('running')
        M_ESQUERDO.wait_while('running')


def acelerar_ajustando(velocidade_direita, velocidade_esquerda):
    # Acelera infinitamente, mas com velocidade diferente em cada motor
    M_DIREITO.run_forever(speed_sp=velocidade_esquerda)
    M_ESQUERDO.run_forever(speed_sp=velocidade_direita)


def fazer_curva_dir(velocidade, tempo):
    # Faz curva pra esquerda no proprio eixo do robo
    M_DIREITO.run_timed(time_sp=tempo, speed_sp=velocidade * -1, stop_action='brake')
    M_ESQUERDO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
    M_DIREITO.wait_while('running')
    M_ESQUERDO.wait_while('running')


def fazer_curva_esq(velocidade, tempo):
    # Faz curva pra direita no proprio eixo do robo
    M_DIREITO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
    M_ESQUERDO.run_timed(time_sp=tempo, speed_sp=velocidade * -1, stop_action='brake')
    M_DIREITO.wait_while('running')
    M_ESQUERDO.wait_while('running')


def acelerar_porta(velocidade, tempo=0):
    if tempo == 0:
        M_PORTA.run_forever(speed_sp=velocidade, stop_action='brake')
    else:
        M_PORTA.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')


def cor_preto(tempo):
    # Curva quando tiver na cor preta
    fazer_curva_dir(VELOCIDADE_CURVA, tempo)
    while CL.value() == PRETO:
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        velocidade_esq, velocidade_dir = corrigir_percurso()  # Novos valores de velocidade
        acelerar_ajustando(velocidade_dir, velocidade_esq)


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
    acelerar(VELOCIDADE_ATUAL, 1800)
    fazer_curva_esq(VELOCIDADE_CURVA, tempo)


def direita(tempo):
    # Faz curva de 90 graus para direita
    acelerar(VELOCIDADE_ATUAL, 1800)
    fazer_curva_dir(VELOCIDADE_CURVA, tempo)


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
        direita(1000)
    else:
        curva(relacao_cores[cor])


def pega_bonecos_dir():
    acelerar(VELOCIDADE_ATUAL, 200)
    fazer_curva_dir(VELOCIDADE_CURVA, 1050)
    acelerar(VELOCIDADE_ATUAL, 1400)
    acelerar_porta(VELOCIDADE_ATUAL, 550)
    acelerar(-1 * VELOCIDADE_ATUAL, 1400)
    fazer_curva_esq(VELOCIDADE_CURVA, 1050)
    return


def chegou_rampa():
    global flag_parar

    acelerar(VELOCIDADE_ATUAL, 500)
    valor_direita = PROX3.value() / 10
    fazer_curva_esq(VELOCIDADE_ATUAL, 2000)
    valor_esquerda = PROX3.value() / 10
    if valor_direita >= valor_esquerda:
        fazer_curva_dir(VELOCIDADE_ATUAL, 1000)
        # acelera ate a parede
        acelerar(-1 * VELOCIDADE_ATUAL, 300)
        fazer_curva_dir(VELOCIDADE_ATUAL, 1500)
    else:
        fazer_curva_esq(VELOCIDADE_ATUAL, 1000)
        # acelera ate a parede
        acelerar(-1 * VELOCIDADE_ATUAL, 300)
        fazer_curva_esq(VELOCIDADE_ATUAL, 1500)
    acelerar_ajustando(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL)
    if CL.value() == PRETO:
        # soltar boneco
        acelerar(VELOCIDADE_ATUAL, 1500)
        # solta boneco
        while CL.value() == PRETO:
            acelerar_ajustando(-1 * VELOCIDADE_ATUAL, -1 * VELOCIDADE_ATUAL)
        flag_parar = True


def percurso():
    # Funcao principal do programa com a estrutura que o robo deve seguir do codigo
    while True:
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        velocidade_esq, velocidade_dir = corrigir_percurso()  # Novos valores de velocidade
        acelerar_ajustando(velocidade_dir, velocidade_esq)
        if PROX3.value() < DISTANCIA_BONECOS:
            pega_bonecos_dir()
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
            cor_preto(2000)
    while (CL.value() == VERMELHO) or (CL.value() == VERDE) or (CL.value() == AZUL):
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        acelerar(VELOCIDADE_ATUAL, 300)
        velocidade_esq, velocidade_dir = corrigir_percurso()  # Novos valores de velocidade
        acelerar_ajustando(velocidade_dir, velocidade_esq)


def main():
    while True:
        percurso()
        if flag_parar == True:
            parar_motor()
            break


if __name__ == '__main__':
    main()
