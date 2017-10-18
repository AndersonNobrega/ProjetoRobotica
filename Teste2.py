#!/usr/bin/env python3

import ev3dev.ev3 as ev3

M_ESQUERDO = ev3.LargeMotor('outD')
M_DIREITO = ev3.LargeMotor('outC')
CL = ev3.ColorSensor('in1')
CL.mode = 'COL-COLOR'
PROX1 = ev3.InfraredSensor('in3')  # DIREITA
PROX2 = ev3.InfraredSensor('in2')  # ESQUERDA
PROX1.mode = 'IR-PROX'
PROX2.mode = 'IR-PROX'
GYRO = ev3.GyroSensor('in4')
GYRO.mode = 'TILT-ANG'

VELOCIDADE_CURVA = 300
VELOCIDADE_ATUAL = 350
KP = 1.5
VERDE = 3
VERMELHO = 5
AZUL = 2
PRETO = 1
lista_valores = [0, 0, 0]  # indice 0 - VERMELHO, indice 1 - VERDE, indice 2 - AZUL
cor_caminho = ["", ""]
cores = ["VERMELHO", "AZUL", "VERDE"]
relacao_cores = {"VERMELHO": "", "VERDE": "", "AZUL": ""}


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


def fazer_curva_dir(velocidade):
    # Faz curva pra esquerda no proprio eixo do robo
    M_ESQUERDO.run_forever(speed_sp=velocidade * -1)
    M_DIREITO.run_forever(speed_sp=velocidade)


def fazer_curva_esq(velocidade):
    # Faz curva pra direita no proprio eixo do robo
    M_ESQUERDO.run_forever(speed_sp=velocidade)
    M_DIREITO.run_forever(speed_sp=velocidade * -1)


def cor_preto():
    acelerar(VELOCIDADE_ATUAL, 600)
    ang_atual = GYRO.value()
    while True:
        fazer_curva_dir(VELOCIDADE_CURVA)
        if ang_atual - 175 >= GYRO.value():
            break
    while (CL.value() == PRETO):
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
    if cor == "VERMELHO":
        index = 0
    elif cor == "VERDE":
        index = 1
    else:
        index = 2

    if lista_valores[index] == 1 and "DIREITA" not in relacao_cores.values():
        relacao_cores[cor] = "DIREITA"
    else:
        if lista_valores[index] == 2 or ("ESQUERDA" in relacao_cores.values() and "DIREITA" in relacao_cores.values()):
            relacao_cores[cor] = "MEIO"
        elif lista_valores[index] == 3 or "ESQUERDA" not in relacao_cores.values():
            relacao_cores[cor] = "ESQUERDA"


def curva(sentido):
    # Verifica o caminho que deve seguir
    if sentido == "DIREITA":
        direita()
    elif sentido == "ESQUERDA":
        esquerda()


def esquerda():
    # Faz curva de 90 graus para a esquerda
    acelerar(VELOCIDADE_ATUAL, 700)
    ang_atual = GYRO.value()
    while True:
        fazer_curva_esq(VELOCIDADE_CURVA)
        if ang_atual + 85 <= GYRO.value():
            return


def direita():
    # Faz curva de 90 graus para direita
    acelerar(VELOCIDADE_ATUAL, 700)
    ang_atual = GYRO.value()
    while True:
        fazer_curva_dir(VELOCIDADE_CURVA)
        if ang_atual - 85 >= GYRO.value():
            return


def aprender_caminho():
    if cor_caminho[0] != "" and cor_caminho[1] in cores and cor_caminho[0] != cor_caminho[1]:
        return True

    if "DIREITA" not in relacao_cores.values():
        direita()
    elif "ESQUERDA" not in relacao_cores.values():
        esquerda()
    return False


def percurso():
    while True:
        velocidade_esq, velocidade_dir = corrigir_percurso(PROX1.value(), PROX2.value())  # Novos valores de velocidade
        acelerar_ajustando(velocidade_dir, velocidade_esq)  # Vai mudando a velocidade do robo durante o percurso
        if CL.value() == VERDE:  # Verde
            retornar_cor("VERDE")
            if relacao_cores["VERDE"] == "":
                lista_valores[1] += 1
                condicao = aprender_caminho()
                if condicao:
                    define_direcao(cor_caminho[0])
            else:
                curva(relacao_cores["VERDE"])
            break
        if CL.value() == VERMELHO:  # Vermelho
            retornar_cor("VERMELHO")
            if relacao_cores["VERMELHO"] == "":
                lista_valores[1] += 1
                condicao = aprender_caminho()
                if condicao:
                    define_direcao(cor_caminho[0])
            else:
                curva(relacao_cores["VERMELHO"])
            break
        if CL.value() == AZUL:  # Azul
            retornar_cor("AZUL")
            if relacao_cores["AZUL"] == "":
                lista_valores[2] += 1
                if aprender_caminho():
                    define_direcao(cor_caminho[0])
            else:
                curva(relacao_cores["AZUL"])
            break
        if CL.value() == PRETO:
            cor_preto()
    while (CL.value() == VERMELHO) or (CL.value() == VERDE) or (CL.value() == AZUL):
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente
        velocidade_esq, velocidade_dir = corrigir_percurso(PROX1.value(), PROX2.value())  # Novos valores de velocidade
        acelerar_ajustando(velocidade_dir, velocidade_esq)


while True:
    percurso()