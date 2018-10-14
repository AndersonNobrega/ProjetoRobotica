#!/usr/bin/env python3

from ev3dev.ev3 import MediumMotor, LargeMotor, ColorSensor, InfraredSensor
from Classes.Motores import *
from Classes.PID import *
from csv import reader

# Motores
M_PORTA = MediumMotor('outC')
M_ESQUERDO = LargeMotor("outA")
M_DIREITO = LargeMotor("outB")

# Sensores de Cor
CL1 = ColorSensor("in1")
CL2 = ColorSensor("in2")
CL1.mode = "RGB-RAW"
CL2.mode = "RGB-RAW"

# Sensores infravermelhos
PROX1 = InfraredSensor("in4")
PROX2 = InfraredSensor("in3")
PROX1.mode = "IR-PROX"
PROX2.mode = "IR-PROX"

# Variaveis usadas durante o programa
TEMPO_CURVA_90 = 1600
TEMPO_CURVA_180 = 3200
DISTANCIA_BONECOS = 14
VELOCIDADE_CURVA = 400
VELOCIDADE_ATUAL = 350
KP = 2
KD = 0
KI = 0.3
R = 0
G = 1
B = 2
quant_bonecos = 0
lista_valores = [0, 0, 0]  # indice 0 - VERMELHO, indice 1 - VERDE, indice 2 - AZUL
cor_caminho = ["", ""]
cores = ["VERMELHO", "AZUL", "VERDE"]
relacao_cores = {"VERMELHO": "", "VERDE": "", "AZUL": ""}
flag_parar = False
final = False
CONSTANTE_DEUS = 9

# Valores RGB para usar nos sensores
VALORES_RGB = {"VERMELHO": [], "VERDE": [], "AZUL": [], "PRETO": [], "BRANCO": []}
MIN_CL1 = 0
MAX_CL1 = 1
MIN_CL2 = 2
MAX_CL2 = 3

funcao_motores = Motores(M_ESQUERDO, M_DIREITO, M_PORTA)
pid = PID(KP, KI, KD)


def ler_valores_rgb(arquivo):
    """
    Faz a leitura do arquivo csv e retorna os valores contidos

    :param arquivo: Nome do arquivo
    :return: Valores RGB que estavam guardados no arquivo

    """

    cont = 0
    with open(arquivo, 'r') as valores:
        tabela = reader(valores)
        for linha in tabela:
            if cont == 0:
                sensor1_min = linha[0:3]
                sensor1_max = linha[3:6]
            elif cont == 1:
                sensor2_min = linha[0:3]
                sensor2_max = linha[3:6]
            cont += 1

        return [sensor1_min, sensor1_max, sensor2_min, sensor2_max]


def guardar_valores():
    """
    Ler os valores RGB guardados na calibragem e coloca eles em um dict

    """

    VALORES_RGB["VERDE"] = ler_valores_rgb("verde.csv")
    VALORES_RGB["VERMELHO"] = ler_valores_rgb("vermelho.csv")
    VALORES_RGB["AZUL"] = ler_valores_rgb("azul.csv")
    VALORES_RGB["PRETO"] = ler_valores_rgb("preto.csv")
    VALORES_RGB["BRANCO"] = ler_valores_rgb("branco.csv")


def eh_cor(lista_rgb_min, lista_rgb_max, sensor):
    """
    Verifica se o sensor esta lendo alguma cor no momento

    :param lista_rgb_min: Valores minimos do RGB achados na calibragem
    :param lista_rgb_max: Valores maximos do RGB achados na calibragem
    :param sensor: Sensor que esta lendo (CL1 ou CL2)
    :return: Se o valor do sensor se encontra no intervalo da cor que se procura

    """

    return ((int(lista_rgb_min[R]) <= sensor.value(R) <= int(lista_rgb_max[R])) and
            (int(lista_rgb_min[G]) <= sensor.value(G) <= int(lista_rgb_max[G])) and
            (int(lista_rgb_min[B]) <= sensor.value(B) <= int(lista_rgb_max[B])))


def controle_proporcional(valor1, valor2, offset):
    """
    Faz o calculo do PID e retorna os valores de velocidade para os motores

    :param valor1: Leitura da distancia do sensor infravermelho da direita
    :param valor2: Leitura da distancia do sensor infravermelho da esquerda
    :param offset: Diferença entre sensor infravermelho da direita e da esquerda no inicio do codigo
    :return: Novos valores de velocidades para o motor direito e esquerdo

    """

    erro = (valor1 - valor2) - offset
    pid.update(erro)
    correcao = pid.output

    velocidade_nova_dir = VELOCIDADE_ATUAL - correcao
    velocidade_nova_esq = (VELOCIDADE_ATUAL + correcao) + CONSTANTE_DEUS

    return velocidade_nova_esq, velocidade_nova_dir


def retornar_cor(cor):
    """
    Atualiza a lista com a ultima cor que o robo encontrou e a penultima cor

    Cor anterior = indice 0
    Cor atual = indice 1

    :param cor: Cor que o robo encontrou

    """

    if cor_caminho[1] != "":
        cor_caminho[0] = cor_caminho[1]
        cor_caminho[1] = cor
    elif cor_caminho[0] == "":
        cor_caminho[1] = cor


def parar_motor():
    """
    Para o motor do robo

    """

    M_ESQUERDO.stop()
    M_DIREITO.stop()


def define_direcao(cor):
    """
    Procura a cor no dict e guarda qual a direcao dela

    :param cor: Cor que o robo encontrou

    """

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
    """
    Verifica para que lado o robo deve seguir

    :param sentido: O sentido que o robo deve seguir

    """

    if sentido == "DIREITA":
        direita(TEMPO_CURVA_90)
    elif sentido == "ESQUERDA":
        esquerda(TEMPO_CURVA_90)


def esquerda(tempo):
    """
    Faz curva para a esquerda

    :param tempo: Tempo que deve levar fazendo a curva

    """

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1200)
    funcao_motores.fazer_curva_esq_esteira(VELOCIDADE_CURVA, tempo)


def direita(tempo):
    """
    Faz curva para a direita

    :param tempo: Tempo que deve levar fazendo a curva

    """

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1200)
    funcao_motores.fazer_curva_dir_esteira(VELOCIDADE_CURVA, tempo)


def ajustar_na_cor(cor):
    """
    Ajuda o robo para ficar reto quando encontra uma cor e quando sai de uma cor

    :param cor: Cor em que o robo se encontra

    """

    while True:
        if eh_cor(VALORES_RGB[cor][MIN_CL1], VALORES_RGB[cor][MAX_CL1], CL1):
            funcao_motores.acelerar_dir(-1 * (VELOCIDADE_ATUAL - 175))
        else:
            funcao_motores.acelerar_dir(0)

        if eh_cor(VALORES_RGB[cor][MIN_CL2], VALORES_RGB[cor][MAX_CL2], CL2):
            funcao_motores.acelerar_esq(-1 * (VELOCIDADE_ATUAL - 175))
        else:
            funcao_motores.acelerar_esq(0)

        if not eh_cor(VALORES_RGB[cor][MIN_CL1], VALORES_RGB[cor][MAX_CL1], CL1) and \
                not eh_cor(VALORES_RGB[cor][MIN_CL2], VALORES_RGB[cor][MAX_CL2], CL2):
            return


def aprender_caminho():
    """
    Verifica se ele achou uma cor diferente da anterior que nao seja preto

    Cor anterior = indice 0
    Cor atual = indice 1

    """

    if cor_caminho[0] != "" and cor_caminho[1] in cores and \
            cor_caminho[0] != "PRETO" and relacao_cores[cor_caminho[0]] == "":
        return True


def achou_cor(cor, indice_cor=None):
    """
    Quando achar uma cor, verifique se nao foi so um bug no sensor e faz a curva

    :param cor: Cor em que o robo se encontra
    :param indice_cor: Indice da cor na lista

    """

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 300)
    funcao_motores.acelerar(0, 600)

    if not eh_cor(VALORES_RGB[cor][MIN_CL1], VALORES_RGB[cor][MAX_CL1], CL1) and \
            not eh_cor(VALORES_RGB[cor][MIN_CL2], VALORES_RGB[cor][MAX_CL2], CL2):
        funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 600)
        funcao_motores.acelerar(0, 500)
        return

    ajustar_na_cor(cor)
    funcao_motores.acelerar(0, 600)
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1200)

    retornar_cor(cor)

    if cor == "PRETO":
        funcao_motores.acelerar(VELOCIDADE_ATUAL, 100)
        direita(TEMPO_CURVA_180)
    else:
        if aprender_caminho():
            define_direcao(cor_caminho[0])
        else:
            sem_direcao(cor, indice_cor)

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1200)

    ajustar_na_cor("BRANCO")
    funcao_motores.acelerar(0, 500)

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 300)


def sem_direcao(cor, indice_cor):
    """
    Verifica se a cor ja tem um sentido definido ou nao, e faz a curva

    :param cor: Cor em que o robo se encontra
    :param indice_cor: Indice da cor na lista

    """

    if relacao_cores[cor] == "":
        lista_valores[indice_cor] += 1
        direita(TEMPO_CURVA_90)
    else:
        curva(relacao_cores[cor])


def pega_bonecos_dir():
    """
    Funcao para pegar os bonecos na plataforma da direita

    """

    funcao_motores.acelerar_porta(-1 * VELOCIDADE_ATUAL, 5000)
    funcao_motores.fazer_curva_dir_esteira(VELOCIDADE_CURVA, 900)
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 2000)
    funcao_motores.acelerar_porta(VELOCIDADE_ATUAL, 700)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 2050)
    funcao_motores.fazer_curva_esq_esteira(VELOCIDADE_CURVA, 900)
    funcao_motores.acelerar_porta(-100, 100)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 400)


def pega_bonecos_esq():
    """
    Funcao para pegar os bonecos na plataforma da esquerda

    """

    funcao_motores.acelerar_porta(-1 * VELOCIDADE_ATUAL, 5000)
    funcao_motores.fazer_curva_esq_esteira(VELOCIDADE_CURVA, 900)
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 2000)
    funcao_motores.acelerar_porta(VELOCIDADE_ATUAL, 700)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 2050)
    funcao_motores.fazer_curva_dir_esteira(VELOCIDADE_CURVA, 900)
    funcao_motores.acelerar_porta(-100, 100)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 400)


def percurso(offset):
    """
    Funcao principal do robo, onde ele vai se ajustando de acordo com os valores do PID e verifica se encontrou alguma
    cor

    :param offset: Diferença entre sensor infravermelho da direita e da esquerda no inicio do codigo

    """

    while True:
        velocidade_esq, velocidade_dir = controle_proporcional(PROX1.value(), PROX2.value(), offset)
        funcao_motores.acelerar_ajustando(velocidade_dir, velocidade_esq)

        if eh_cor(VALORES_RGB["VERDE"][MIN_CL1], VALORES_RGB["VERDE"][MAX_CL1], CL1) and \
                eh_cor(VALORES_RGB["VERDE"][MIN_CL2], VALORES_RGB["VERDE"][MAX_CL2], CL2):

            achou_cor("VERDE", 1)
        elif eh_cor(VALORES_RGB["VERMELHO"][MIN_CL1], VALORES_RGB["VERMELHO"][MAX_CL1], CL1) and \
                eh_cor(VALORES_RGB["VERMELHO"][MIN_CL2], VALORES_RGB["VERMELHO"][MAX_CL2], CL2):

            achou_cor("VERMELHO", 0)
        elif eh_cor(VALORES_RGB["AZUL"][MIN_CL1], VALORES_RGB["AZUL"][MAX_CL1], CL1) and \
                eh_cor(VALORES_RGB["AZUL"][MIN_CL2], VALORES_RGB["AZUL"][MAX_CL2], CL2):

            achou_cor("AZUL", 2)
        elif eh_cor(VALORES_RGB["PRETO"][MIN_CL1], VALORES_RGB["PRETO"][MAX_CL1], CL1) and \
                eh_cor(VALORES_RGB["PRETO"][MIN_CL2], VALORES_RGB["PRETO"][MAX_CL2], CL2):

            achou_cor("PRETO")


def main():
    guardar_valores()
    funcao_motores.acelerar(0, 300)
    offset = PROX1.value() - PROX2.value()
    while True:
        percurso(offset)


if __name__ == '__main__':
    main()
