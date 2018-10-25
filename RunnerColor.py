#!/usr/bin/env python3

from ev3dev.ev3 import LargeMotor, ColorSensor, GyroSensor
from Classes.Motores import *
from time import time
import paho.mqtt.client as mqtt

# Motores
M_PORTA = LargeMotor('outC')
M_ESQUERDO = LargeMotor("outA")
M_DIREITO = LargeMotor("outB")

# Sensores de Cor
CL1 = ColorSensor("in1")
CL2 = ColorSensor("in2")
CL1.mode = "COL-COLOR"
CL2.mode = "COL-COLOR"

# Giroscopio
GYRO = GyroSensor("in3")
GYRO.mode = "GYRO-ANG"

# Variaveis usadas durante o programa
TEMPO_CURVA_90 = 1700
TEMPO_CURVA_180 = 3400
ANGULO_CURVA_180 = 180
ANGULO_CURVA_90 = 90
VELOCIDADE_CURVA = 400
VELOCIDADE_ATUAL = 350
DISTANCIA_BONECOS = 30
quant_bonecos = 0
quant_idas = 0
lista_valores = [0, 0, 0]  # indice 0 - VERMELHO, indice 1 - VERDE, indice 2 - AZUL
cores_voltando = [0, 0, 0]  # Quant de cores na volta
cores_indo = [0, 0, 0]  # Quant de cores na ida
cor_caminho = ["", ""]
cores = ["VERMELHO", "AZUL", "VERDE"]
relacao_cores = {"VERMELHO": "", "VERDE": "", "AZUL": ""}
flag_parar = False
final = False
boneco_dir = 1000
boneco_esq = 1000
sentido = "INDO"
CONSTANTE_DEUS = 9
correcao = 0

funcao_motores = Motores(M_ESQUERDO, M_DIREITO, M_PORTA)
client = mqtt.Client()
client.connect("169.254.96.68", 1883, 60)


def on_connect(client, userdata, flags, rc):
    client.subscribe([("topic/sensor/ultrasonic1", 0), ("topic/sensor/ultrasonic2", 0), ("topic/sensor/pid", 0)])


def on_disconnect(client, userdata, rc=0):
    client.loop_stop()


def on_message(client, userdata, msg):
    global boneco_dir, boneco_esq, correcao

    if msg.topic == "topic/sensor/ultrasonic1":
        boneco_dir = float(msg.payload.decode())

    if msg.topic == "topic/sensor/ultrasonic2":
        boneco_esq = float(msg.payload.decode())

    if msg.topic == "topic/sensor/pid":
        correcao = float(msg.payload.decode())


def controle_proporcional():
    """
    Faz o calculo do PID e retorna os valores de velocidade para os motores

    :param valor1: Leitura da distancia do sensor infravermelho da direita
    :param valor2: Leitura da distancia do sensor infravermelho da esquerda
    :param offset: Diferença entre sensor infravermelho da direita e da esquerda no inicio do codigo
    :return: Novos valores de velocidades para o motor direito e esquerdo

    """

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


def curva(sentido_curva):
    """
    Verifica para que lado o robo deve seguir

    :param sentido: O sentido que o robo deve seguir

    """

    if sentido_curva == "DIREITA":
        direita_giroscopio(ANGULO_CURVA_90)
    elif sentido_curva == "ESQUERDA":
        esquerda_giroscopio(ANGULO_CURVA_90)
    elif sentido_curva == "MEIO":
        while CL1.value() != ColorSensor.COLOR_WHITE and CL2.value() != ColorSensor.COLOR_WHITE:
            funcao_motores.acelerar_ajustando(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL)


def direita_giroscopio(angulo_curva):
    ang_atual = GYRO.value()

    while True:
        funcao_motores.fazer_curva_dir_esteira(VELOCIDADE_ATUAL - 150)
        if ang_atual + angulo_curva <= GYRO.value():
            parar_motor()
            break


def esquerda_giroscopio(angulo_curva):
    ang_atual = GYRO.value()

    while True:
        funcao_motores.fazer_curva_esq_esteira(VELOCIDADE_ATUAL - 150)
        if ang_atual - angulo_curva <= GYRO.value():
            parar_motor()
            break


def ajustar_na_cor(valor_cor):
    """
    Ajuda o robo para ficar reto quando encontra uma cor e quando sai de uma cor

    :param valor_cor: Valor da cor no range de 1 a 7

    """

    while True:
        if CL1.value() == valor_cor:
            funcao_motores.acelerar_dir(-1 * (VELOCIDADE_ATUAL - 175))
        else:
            funcao_motores.acelerar_dir(0)

        if CL2.value() == valor_cor:
            funcao_motores.acelerar_esq(-1 * (VELOCIDADE_ATUAL - 175))
        else:
            funcao_motores.acelerar_esq(0)

        if not CL1.value() == valor_cor and not CL2.value() == valor_cor:
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


def achou_cor(cor, valor_cor, indice_cor=None):
    """
    Quando achar uma cor, verifique se nao foi so um bug no sensor e faz a curva

    :param cor: Cor em que o robo se encontra
    :param valor_cor: Valor da cor no range de 1 a 7
    :param indice_cor: Indice da cor na lista

    """

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 300)
    funcao_motores.acelerar(0, 600)

    if not CL1.value() == valor_cor and not CL2.value() == valor_cor:
        funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 600)
        funcao_motores.acelerar(0, 500)
        return

    ajustar_na_cor(valor_cor)
    funcao_motores.acelerar(0, 600)
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 2200)
    funcao_motores.acelerar(0, 300)

    retornar_cor(cor)

    if cor == "PRETO":
        direita_giroscopio(ANGULO_CURVA_180)
    else:
        if aprender_caminho():
            define_direcao(cor_caminho[0])

        sem_direcao(cor, indice_cor)

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 600)

    ajustar_na_cor(ColorSensor.COLOR_WHITE)
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
        direita_giroscopio(90)
    else:
        curva(relacao_cores[cor])


def pega_bonecos_dir():
    """
    Funcao para pegar os bonecos na plataforma da direita

    """

    funcao_motores.acelerar_porta(-1 * VELOCIDADE_ATUAL, 5000)
    esquerda_giroscopio(ANGULO_CURVA_90)
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 2000)
    funcao_motores.acelerar_porta(VELOCIDADE_ATUAL, 700)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 2050)
    direita_giroscopio(ANGULO_CURVA_90)
    funcao_motores.acelerar_porta(-100, 100)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 400)


def pega_bonecos_esq():
    """
    Funcao para pegar os bonecos na plataforma da esquerda

    """

    funcao_motores.acelerar_porta(-1 * VELOCIDADE_ATUAL, 5000)
    direita_giroscopio(ANGULO_CURVA_90)
    funcao_motores.acelerar(VELOCIDADE_ATUAL, 2000)
    funcao_motores.acelerar_porta(VELOCIDADE_ATUAL, 700)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 2050)
    esquerda_giroscopio(ANGULO_CURVA_90)
    funcao_motores.acelerar_porta(-100, 100)
    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 400)


def chegou_final():
    global flag_parar, final, quant_bonecos, quant_idas, sentido

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 1400)
    funcao_motores.acelerar_porta(-1 * VELOCIDADE_ATUAL, 3000)

    while CL1.value() == ColorSensor.COLOR_BLACK and CL2.value() == ColorSensor.COLOR_BLACK:
        funcao_motores.acelerar_ajustando(-1 * VELOCIDADE_ATUAL, -1 * VELOCIDADE_ATUAL)

    funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 2000)
    if quant_idas == 0:
        funcao_motores.fazer_curva_dir_esteira(VELOCIDADE_ATUAL, TEMPO_CURVA_180)
        funcao_motores.acelerar(VELOCIDADE_ATUAL, 4500)
        for nomes in relacao_cores.keys():
            if relacao_cores[nomes] == "DIREITA":
                relacao_cores[nomes] = "ESQUERDA"
            elif relacao_cores[nomes] == "ESQUERDA":
                relacao_cores[nomes] = "DIREITA"
        sentido = "VOLTANDO"
        quant_idas = 1
    quant_bonecos = 0
    final = False


def eh_rampa():
    global quant_bonecos, final, sentido

    funcao_motores.acelerar(VELOCIDADE_ATUAL, 100)
    funcao_motores.acelerar(0, 500)

    if not CL1.value() == ColorSensor.COLOR_BLUE and not CL2.value() == ColorSensor.COLOR_BLUE:
        funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, 400)
        funcao_motores.acelerar(0, 300)
        return
    else:
        inicio = time()
        while CL1.value() != ColorSensor.COLOR_RED and CL2.value() != ColorSensor.COLOR_RED:
            funcao_motores.acelerar_ajustando(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL)
            fim = time()
            if fim - inicio >= 0.8:
                funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, (fim - inicio) * 1000)
                funcao_motores.acelerar(0, 300)
                return

        funcao_motores.acelerar(0, 300)
        inicio = time()
        while CL1.value() != ColorSensor.COLOR_GREEN and CL2.value() != ColorSensor.COLOR_GREEN:
            funcao_motores.acelerar_ajustando(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL)
            fim = time()
            if fim - inicio >= 0.8:
                funcao_motores.acelerar(-1 * VELOCIDADE_ATUAL, (fim - inicio) * 1000)
                funcao_motores.acelerar(0, 300)
                return

        final = True
        funcao_motores.acelerar(VELOCIDADE_ATUAL, 5000)
        quant_bonecos = 0
        return


def percurso():
    """
    Funcao principal do robo, onde ele vai se ajustando de acordo com os valores do PID e verifica se encontrou alguma
    cor

    :param offset: Diferença entre sensor infravermelho da direita e da esquerda no inicio do codigo

    """

    global sentido, quant_idas, quant_bonecos, boneco_dir, boneco_esq

    while True:
        if quant_bonecos < 2:
            if boneco_dir <= DISTANCIA_BONECOS:
                quant_bonecos += 1
                pega_bonecos_dir()
            elif boneco_esq <= DISTANCIA_BONECOS:
                quant_bonecos += 1
                pega_bonecos_esq()

        if sum(cores_indo) == sum(cores_voltando) and sum(cores_indo) != 0 and sum(cores_voltando) != 0:
            direita_giroscopio(ANGULO_CURVA_180)
            for nomes in relacao_cores.keys():
                if relacao_cores[nomes] == "DIREITA":
                    relacao_cores[nomes] = "ESQUERDA"
                elif relacao_cores[nomes] == "ESQUERDA":
                    relacao_cores[nomes] = "DIREITA"
            for index in cores_indo:
                cores_indo[index] = 0
                cores_voltando[index] = 0
            quant_idas = 0
            sentido = "INDO"

        velocidade_esq, velocidade_dir = controle_proporcional()
        funcao_motores.acelerar_ajustando(velocidade_dir, velocidade_esq)

        if CL1.value() == ColorSensor.COLOR_GREEN and CL2.value() == ColorSensor.COLOR_GREEN:

            achou_cor("VERDE", ColorSensor.COLOR_GREEN, 1)
            if sentido == "INDO":
                cores_indo[1] += 1
            elif sentido == "VOLTANDO":
                cores_voltando[1] += 1
            break
        elif CL1.value() == ColorSensor.COLOR_RED and CL2.value() == ColorSensor.COLOR_RED:

            achou_cor("VERMELHO", ColorSensor.COLOR_RED, 0)
            if sentido == "INDO":
                cores_indo[0] += 1
            elif sentido == "VOLTANDO":
                cores_voltando[0] += 1
            break
        elif CL1.value() == ColorSensor.COLOR_BLUE and CL2.value() == ColorSensor.COLOR_BLUE:

            eh_rampa()
            achou_cor("AZUL", ColorSensor.COLOR_BLUE, 2)
            if sentido == "INDO":
                cores_indo[2] += 1
            elif sentido == "VOLTANDO":
                cores_voltando[2] += 1
            break
        elif CL1.value() == ColorSensor.COLOR_BLACK and CL2.value() == ColorSensor.COLOR_BLACK:

            if final:
                chegou_final()
            else:
                achou_cor("PRETO", ColorSensor.COLOR_BLACK)


def main():
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()

    while True:
        percurso()


if __name__ == '__main__':
    main()
