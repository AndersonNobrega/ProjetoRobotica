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
VELOCIDADE_ATUAL = velocidade_dir = velocidade_esq = 350
KP = 2
KD = 0
KI = 0.3
PRETO = 1
AZUL = 2
VERDE = 3
AMARELO = 4
VERMELHO = 5
BRANCO = 6
R = 0
G = 1
B = 2
quant_bonecos = 0
lista_valores = [0, 0, 0]  # indice 0 - VERMELHO, indice 1 - VERDE, indice 2 - AMARELO
cor_caminho = ["", ""]
cores = ["VERMELHO", "AZUL", "VERDE"]
relacao_cores = {"VERMELHO": "", "VERDE": "", "AZUL": ""}
flag_parar = False
final = False
OFFSET = 0
CONSTANTE_DEUS = 9

# Valores RGB para usar nos sensores
VERDE_CL1_RGB_MIN = []
VERDE_CL1_RGB_MAX = []
VERDE_CL2_RGB_MIN = []
VERDE_CL2_RGB_MAX = []
VERMELHO_CL1_RGB_MIN = []
VERMELHO_CL1_RGB_MAX = []
VERMELHO_CL2_RGB_MIN = []
VERMELHO_CL2_RGB_MAX = []
AZUL_CL1_RGB_MIN = []
AZUL_CL1_RGB_MAX = []
AZUL_CL2_RGB_MIN = []
AZUL_CL2_RGB_MAX = []
PRETO_CL1_RGB_MIN = []
PRETO_CL1_RGB_MAX = []
PRETO_CL2_RGB_MIN = []
PRETO_CL2_RGB_MAX = []
BRANCO_CL1_RGB_MIN = []
BRANCO_CL1_RGB_MAX = []
BRANCO_CL2_RGB_MIN = []
BRANCO_CL2_RGB_MAX = []

funcao_motores = Motores(M_ESQUERDO, M_DIREITO, M_PORTA)
pid = PID(KP, KI, KD)
pid.SetPoint = 0


def salvar(texto):
    with open('leitura_cl.txt', 'a+', encoding='ISO-8859-1') as arquivo:
        for linha in texto:
            arquivo.write(linha)


def ler_valores_rgb(arquivo):
    cont = 0
    with open(arquivo, 'r', encoding='ISO-8859-1') as valores:
        tabela = reader(valores)
        for linha in tabela:
            if cont == 0:
                sensor1_min = linha[0:3]
                sensor1_max = linha[3:6]
            elif cont == 1:
                sensor2_min = linha[0:3]
                sensor2_max = linha[3:6]
            cont += 1

        return sensor1_min, sensor1_max, sensor2_min, sensor2_max


def guardar_valores():
    global VERDE_CL1_RGB_MIN, VERDE_CL1_RGB_MAX, VERDE_CL2_RGB_MIN, VERDE_CL2_RGB_MAX, VERMELHO_CL1_RGB_MIN, \
        VERMELHO_CL1_RGB_MAX, VERMELHO_CL2_RGB_MIN, VERMELHO_CL2_RGB_MAX, AZUL_CL1_RGB_MIN, AZUL_CL1_RGB_MAX, \
        AZUL_CL2_RGB_MIN, AZUL_CL2_RGB_MAX, PRETO_CL1_RGB_MIN, PRETO_CL1_RGB_MAX, PRETO_CL2_RGB_MIN, PRETO_CL2_RGB_MAX, \
        BRANCO_CL1_RGB_MIN, BRANCO_CL1_RGB_MAX, BRANCO_CL2_RGB_MIN, BRANCO_CL2_RGB_MAX

    VERDE_CL1_RGB_MIN, VERDE_CL1_RGB_MAX, VERDE_CL2_RGB_MIN, VERDE_CL2_RGB_MAX = ler_valores_rgb("verde.csv")
    VERMELHO_CL1_RGB_MIN, VERMELHO_CL1_RGB_MAX, VERMELHO_CL2_RGB_MIN, VERMELHO_CL2_RGB_MAX = ler_valores_rgb(
        "vermelho.csv")
    AZUL_CL1_RGB_MIN, AZUL_CL1_RGB_MAX, AZUL_CL2_RGB_MIN, AZUL_CL2_RGB_MAX = ler_valores_rgb("azul.csv")
    PRETO_CL1_RGB_MIN, PRETO_CL1_RGB_MAX, PRETO_CL2_RGB_MIN, PRETO_CL2_RGB_MAX = ler_valores_rgb("preto.csv")
    BRANCO_CL1_RGB_MIN, BRANCO_CL1_RGB_MAX, BRANCO_CL2_RGB_MIN, BRANCO_CL2_RGB_MAX = ler_valores_rgb("branco.csv")


def eh_cor(lista_rgb_min, lista_rgb_max, sensor):
    return ((int(lista_rgb_min[R]) <= sensor.value(R) <= int(lista_rgb_max[R])) and
            (int(lista_rgb_min[G]) <= sensor.value(G) <= int(lista_rgb_max[G])) and
            (int(lista_rgb_min[B]) <= sensor.value(B) <= int(lista_rgb_max[B])))


def eh_cor_atual_cl1(cor):
    if cor == "VERDE":
        return eh_cor(VERDE_CL1_RGB_MIN, VERDE_CL1_RGB_MAX, CL1)
    elif cor == "VERMELHO":
        return eh_cor(VERMELHO_CL1_RGB_MIN, VERMELHO_CL1_RGB_MAX, CL1)
    elif cor == "AZUL":
        return eh_cor(AZUL_CL1_RGB_MIN, AZUL_CL1_RGB_MAX, CL1)
    elif cor == "PRETO":
        return eh_cor(PRETO_CL1_RGB_MIN, PRETO_CL1_RGB_MAX, CL1)
    elif cor == "BRANCO":
        return eh_cor(BRANCO_CL1_RGB_MIN, BRANCO_CL1_RGB_MAX, CL1)


def eh_cor_atual_cl2(cor):
    if cor == "VERDE":
        return eh_cor(VERDE_CL2_RGB_MIN, VERDE_CL2_RGB_MAX, CL2)
    elif cor == "VERMELHO":
        return eh_cor(VERMELHO_CL2_RGB_MIN, VERMELHO_CL2_RGB_MAX, CL2)
    elif cor == "AZUL":
        return eh_cor(AZUL_CL2_RGB_MIN, AZUL_CL2_RGB_MAX, CL2)
    elif cor == "PRETO":
        return eh_cor(PRETO_CL2_RGB_MIN, PRETO_CL2_RGB_MAX, CL2)
    elif cor == "BRANCO":
        return eh_cor(BRANCO_CL2_RGB_MIN, BRANCO_CL2_RGB_MAX, CL2)


def controle_proporcional(valor1, valor2, offset):
    # Faz correção do percurso de acordo com os valores de distancia dos sensores
    erro = (valor1 - valor2) - offset
    pid.update(erro)
    correcao = pid.output

    velocidade_nova_dir = VELOCIDADE_ATUAL - correcao
    velocidade_nova_esq = (VELOCIDADE_ATUAL + correcao) + CONSTANTE_DEUS

    return velocidade_nova_esq, velocidade_nova_dir


def cor_preto(tempo):
    # Curva quando tiver na cor preta
    ajustar_na_cor("PRETO")
    funcao_motores.acelerar(0, 600)
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 2200)

    funcao_motores.fazer_curva_dir_esteira(VELOCIDADE_CURVA, tempo)

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1100)

    ajustar_na_cor("BRANCO")
    funcao_motores.acelerar(0, 600)

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 500)


def retornar_cor(cor):
    # Cor anterior = indice 0
    # Cor atual = indice 1

    if cor_caminho[1] != "":
        cor_caminho[0] = cor_caminho[1]
        cor_caminho[1] = cor
    elif cor_caminho[0] == "":
        cor_caminho[1] = cor


def parar_motor():
    M_ESQUERDO.stop()
    M_DIREITO.stop()


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
        direita(TEMPO_CURVA_90)
    elif sentido == "ESQUERDA":
        esquerda(TEMPO_CURVA_90)
    else:
        return


def esquerda(tempo):
    # Faz curva de 90 graus para a esquerda
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1200)
    funcao_motores.fazer_curva_esq_esteira(VELOCIDADE_CURVA, tempo)


def direita(tempo):
    # Faz curva de 90 graus para direita
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1200)
    funcao_motores.fazer_curva_dir_esteira(VELOCIDADE_CURVA, tempo)


def ajustar_na_cor(cor):
    while True:
        if eh_cor_atual_cl1(cor):
            funcao_motores.acelerar_dir(-1 * (VELOCIDADE_ATUAL - 175))
        else:
            funcao_motores.acelerar_dir(0)

        if eh_cor_atual_cl2(cor):
            funcao_motores.acelerar_esq(-1 * (VELOCIDADE_ATUAL - 175))
        else:
            funcao_motores.acelerar_esq(0)

        if not eh_cor_atual_cl1(cor) and not eh_cor_atual_cl2(cor):
            return


def aprender_caminho():
    # Verifica se o caminho que ele seguiu n e um dead end
    if cor_caminho[0] != "" and cor_caminho[1] in cores and \
            cor_caminho[0] != "PRETO" and relacao_cores[cor_caminho[0]] == "":
        return True


def achou_cor(cor, indice_cor):
    # Quando achar uma cor(Azul, Vermelho ou Verde), verifique se n foi so um bug no sensor e faca uma curva
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 300)
    funcao_motores.acelerar(0, 600)

    if not eh_cor_atual_cl1(cor) and not eh_cor_atual_cl2(cor):
        funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 600)
        funcao_motores.acelerar(0, 500)
        return

    ajustar_na_cor(cor)
    funcao_motores.acelerar(0, 600)
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1200)

    retornar_cor(cor)
    if aprender_caminho():
        define_direcao(cor_caminho[0])

    sem_direcao(cor, indice_cor)

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1200)

    ajustar_na_cor("BRANCO")
    funcao_motores.acelerar(0, 500)

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 300)


def sem_direcao(cor, indice_cor):
    # Quando nao tem uma direcao definida ainda para a cor
    if relacao_cores[cor] == "":
        lista_valores[indice_cor] += 1
        direita(TEMPO_CURVA_90)
    else:
        curva(relacao_cores[cor])


def pega_bonecos_dir():
    funcao_motores.acelerar_porta(-1 * VELOCIDADE_ATUAL, 5000)
    funcao_motores.fazer_curva_dir_esteira(VELOCIDADE_CURVA, 900)
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 2000)
    funcao_motores.acelerar_porta(VELOCIDADE_ATUAL, 700)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 2050)
    funcao_motores.fazer_curva_esq_esteira(VELOCIDADE_CURVA, 900)
    funcao_motores.acelerar_porta(-100, 100)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 400)


def pega_bonecos_esq():
    funcao_motores.acelerar_porta(-1 * VELOCIDADE_ATUAL, 5000)
    funcao_motores.fazer_curva_esq_esteira(VELOCIDADE_CURVA, 900)
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 2000)
    funcao_motores.acelerar_porta(VELOCIDADE_ATUAL, 700)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 2050)
    funcao_motores.fazer_curva_dir_esteira(VELOCIDADE_CURVA, 900)
    funcao_motores.acelerar_porta(-100, 100)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 400)


def percurso(offset):
    global quant_bonecos

    while True:
        # Depois de fazer a curva, enquanto estiver sobre uma cor apenas va em frente

        velocidade_esq, velocidade_dir = controle_proporcional(PROX1.value(), PROX2.value(), offset)
        funcao_motores.acelerar_ajustando(velocidade_dir, velocidade_esq)

        if eh_cor(VERDE_CL1_RGB_MIN, VERDE_CL1_RGB_MAX, CL1) and eh_cor(VERDE_CL2_RGB_MIN, VERDE_CL2_RGB_MAX, CL2):
            achou_cor("VERDE", 1)
            break

        if eh_cor(VERMELHO_CL1_RGB_MIN, VERMELHO_CL1_RGB_MAX, CL1) and eh_cor(VERMELHO_CL2_RGB_MIN,
                                                                              VERMELHO_CL2_RGB_MAX, CL2):
            achou_cor("VERMELHO", 0)
            break
        elif eh_cor(AZUL_CL1_RGB_MIN, AZUL_CL1_RGB_MAX, CL1) and eh_cor(AZUL_CL2_RGB_MIN, AZUL_CL2_RGB_MAX, CL2):
            achou_cor("AZUL", 2)
            break
        elif eh_cor(PRETO_CL1_RGB_MIN, PRETO_CL1_RGB_MAX, CL1) and eh_cor(PRETO_CL2_RGB_MIN, PRETO_CL2_RGB_MAX, CL2):
            funcao_motores.acelerar(VELOCIDADE_ATUAL, 300)
            funcao_motores.acelerar(0, 600)

            if not eh_cor(PRETO_CL1_RGB_MIN, PRETO_CL1_RGB_MAX, CL1) and not eh_cor(PRETO_CL2_RGB_MIN,
                                                                                    PRETO_CL2_RGB_MAX, CL2):
                funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 600)
                funcao_motores.acelerar(0, 500)
                break
            else:
                retornar_cor("PRETO")
                cor_preto(TEMPO_CURVA_180)


def main():
    global OFFSET

    guardar_valores()
    funcao_motores.acelerar(0, 300)
    OFFSET = PROX1.value() - PROX2.value()
    while True:
        percurso(OFFSET)


if __name__ == '__main__':
    main()
