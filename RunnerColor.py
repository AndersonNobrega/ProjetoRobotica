#!/usr/bin/env python3

from ev3dev.ev3 import LargeMotor, ColorSensor, GyroSensor, InfraredSensor, Button
from Classes.Motores import *
from Classes.PID import *
from time import time
from os import system
import paho.mqtt.client as mqtt

# Motores
M_PORTA = LargeMotor("outC")
M_ESQUERDO = LargeMotor("outA")
M_DIREITO = LargeMotor("outB")

# Sensores infravermelhos
PROX1 = InfraredSensor("in4")
PROX2 = InfraredSensor("in3")
PROX1.mode = "IR-PROX"
PROX2.mode = "IR-PROX"

# Giroscopio
GYRO = GyroSensor("in1")
GYRO.mode = "GYRO-ANG"

# Sensor de cor
COLOR = ColorSensor("in2")
COLOR.mode = "COL-COLOR"

# Variaveis usadas durante o programa
# Constantes
TEMPO_CURVA_90 = 1700
TEMPO_CURVA_180 = 3400
ANGULO_CURVA_180 = 180
ANGULO_CURVA_90 = 90
ANGULO_DESVIO = 6
VELOCIDADE_CURVA = 400
VELOCIDADE_ATUAL = 350
KP = 2.5
KI = 0
KD = 1
OFFSET = 0
AJUSTE_MOTOR = 30

# Variaveis
angulo_atual = 0
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
boneco_dir = False
boneco_esq = False
sentido = "INDO"
cor_atual1 = ColorSensor.COLOR_WHITE
cor_atual2 = ColorSensor.COLOR_WHITE

# Objetos
funcao_motores = Motores(M_ESQUERDO, M_DIREITO, M_PORTA)
pid = PID(KP, KI, KD)
client = mqtt.Client()
botao = Button()

# Conectando os dois bricks
client.connect("169.254.96.68", 1883, 60)


def on_connect(client, userdata, flags, rc):
    client.subscribe([("topic/sensor/ultrasonic1", 0), ("topic/sensor/ultrasonic2", 0), ("topic/sensor/color1", 0),
                      ("topic/sensor/color2", 0)])


def on_disconnect(client, userdata, rc=0):
    client.loop_stop()


def on_message(client, userdata, msg):
    global boneco_dir, boneco_esq, cor_atual1, cor_atual2

    if msg.topic == "topic/sensor/ultrasonic1":
        boneco_esq = bool(msg.payload)
    elif msg.topic == "topic/sensor/ultrasonic2":
        boneco_dir = bool(msg.payload)

    if msg.topic == "topic/sensor/color1":
        cor_atual1 = int(msg.payload)
    if msg.topic == "topic/sensor/color2":
        cor_atual2 = int(msg.payload)


def controle_proporcional():
    """
    Faz o calculo do PID e retorna os valores de velocidade para os motores

    :return: Novos valores de velocidades para o motor direito e esquerdo

    """

    distancia_direita = PROX1.value()
    distancia_esquerda = PROX2.value()
    erro = (distancia_direita - distancia_esquerda) - OFFSET
    pid.update(erro)
    correcao = pid.output

    velocidade_nova_dir = VELOCIDADE_ATUAL - correcao
    velocidade_nova_esq = (VELOCIDADE_ATUAL + correcao) + AJUSTE_MOTOR

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

    :param sentido_curva: O sentido que o robo deve seguir

    """

    if sentido_curva == "DIREITA":
        direita_giroscopio(ANGULO_CURVA_90)
    elif sentido_curva == "ESQUERDA":
        esquerda_giroscopio(ANGULO_CURVA_90)
    elif sentido_curva == "MEIO":
        while cor_atual1 != ColorSensor.COLOR_WHITE and cor_atual2 != ColorSensor.COLOR_WHITE:
            funcao_motores.acelerar_ajustando(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR)


def direita_giroscopio(angulo_curva):
    """
    Faz a curva para direita se baseando no valor do giroscopio

    :param angulo_curva: Quanto que o robo deve fazer de giro

    """

    ang_atual = GYRO.value()

    while True:
        funcao_motores.fazer_curva_dir_esteira(VELOCIDADE_ATUAL - 150)
        if ang_atual + angulo_curva <= GYRO.value():
            parar_motor()
            break


def esquerda_giroscopio(angulo_curva):
    """
    Faz a curva para esquerda se baseando no valor do giroscopio

    :param angulo_curva: Quanto que o robo deve fazer de giro

    """

    ang_atual = GYRO.value()

    while True:
        funcao_motores.fazer_curva_esq_esteira(VELOCIDADE_ATUAL - 150)
        if ang_atual - angulo_curva >= GYRO.value():
            parar_motor()
            break


def ajustar_na_cor(valor_cor):
    """
    Ajuda o robo para ficar reto quando encontra uma cor e quando sai de uma cor

    :param valor_cor: Valor da cor no range de 1 a 7

    """

    while True:
        if cor_atual1 == valor_cor:
            funcao_motores.acelerar_dir(-1 * (VELOCIDADE_ATUAL - 175))
        else:
            funcao_motores.acelerar_dir(0)

        if cor_atual2 == valor_cor:
            funcao_motores.acelerar_esq(-1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR - 175))
        else:
            funcao_motores.acelerar_esq(0)

        if not cor_atual1 == valor_cor and not cor_atual2 == valor_cor:
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
    global angulo_atual

    funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 300)
    funcao_motores.acelerar(0, 600)

    if not cor_atual1 == valor_cor and not cor_atual2 == valor_cor:
        funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR), 600)
        funcao_motores.acelerar(0, 500)
        return

    ajustar_na_cor(valor_cor)
    funcao_motores.acelerar(0, 600)
    funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 2200)
    funcao_motores.acelerar(0, 300)

    retornar_cor(cor)

    if cor == "PRETO":
        direita_giroscopio(ANGULO_CURVA_180)
    else:
        if aprender_caminho():
            define_direcao(cor_caminho[0])

        sem_direcao(cor, indice_cor)

    while cor_atual1 == valor_cor and cor_atual2 == valor_cor:
        funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR)

    funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 400)

    ajustar_na_cor(ColorSensor.COLOR_WHITE)
    funcao_motores.acelerar(0, 500)
    angulo_atual = GYRO.value()

    funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 1200)


def sem_direcao(cor, indice_cor):
    """
    Verifica se a cor ja tem um sentido definido ou nao, e faz a curva

    :param cor: Cor em que o robo se encontra
    :param indice_cor: Indice da cor na lista

    """

    if relacao_cores[cor] == "":
        lista_valores[indice_cor] += 1
        direita_giroscopio(ANGULO_CURVA_90)
    else:
        curva(relacao_cores[cor])


def reseta_variaveis():
    """
    Reseta as variaveis do codigo, para caso seja necessario reiniciar o robo

    """

    global quant_bonecos, quant_idas, sentido

    quant_bonecos = 0
    quant_idas = 0
    sentido = "INDO"
    for index in cores_indo:
        cores_indo[index] = 0
        cores_voltando[index] = 0


def pega_bonecos(lado):
    """
    Funcao para pegar os bonecos na plataforma da esquerda ou da direita

    :param lado: Para qual lado o robo deve girar

    """

    funcao_motores.acelerar_porta(-1 * VELOCIDADE_ATUAL)
    funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR), 600)
    funcao_motores.acelerar(0, 300)

    if lado == "DIREITA":
        direita_giroscopio(ANGULO_CURVA_90 - 5)
    else:
        esquerda_giroscopio(ANGULO_CURVA_90 - 5)

    funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 200)

    while cor_atual1 == ColorSensor.COLOR_WHITE and cor_atual2 == ColorSensor.COLOR_WHITE:
        funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR)

    parar_motor()
    funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 300)
    funcao_motores.acelerar_porta(VELOCIDADE_ATUAL)
    funcao_motores.acelerar(0, 1000)

    while COLOR.value() == ColorSensor.COLOR_WHITE:
        funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR))

    funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 700)
    if lado == "DIREITA":
        direita_giroscopio(ANGULO_CURVA_90)
    else:
        esquerda_giroscopio(ANGULO_CURVA_90)

    funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR), 400)
    funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 2000)


def chegou_final():
    """
    O robo deixa os bonecos no circulo no meio da plataforma e faz o caminho de volta para a pista

    """

    global flag_parar, final, quant_idas, sentido, angulo_atual

    funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 1900)
    funcao_motores.acelerar_porta(-1 * VELOCIDADE_ATUAL, 3000)

    while cor_atual1 == ColorSensor.COLOR_BLACK and cor_atual2 == ColorSensor.COLOR_BLACK:
        funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR))

    funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR), 1400)
    parar_motor()
    if quant_idas % 2 == 0:
        direita_giroscopio(ANGULO_CURVA_90)
        funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 8000)
        funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR), 500)

        direita_giroscopio(ANGULO_CURVA_90)
        funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 6000)
        funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR), 500)

        direita_giroscopio(ANGULO_CURVA_90)
        funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR), 1000)

        # Bloco para Testar
        while PROX1.value() <= 10:
            funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR)

        inicio = time()

        while PROX1.value() >= 10:
            funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR)

        fim = time() - inicio
        # Bloco para Testar
        funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR),
                                           (fim / 2) + 100)
        esquerda_giroscopio(ANGULO_CURVA_90)
        parar_motor()
        angulo_atual = GYRO.value()

        funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 9000)

        for nomes in relacao_cores.keys():
            if relacao_cores[nomes] == "DIREITA":
                relacao_cores[nomes] = "ESQUERDA"
            elif relacao_cores[nomes] == "ESQUERDA":
                relacao_cores[nomes] = "DIREITA"
        sentido = "VOLTANDO"
        quant_idas += 1
    final = False


def eh_rampa():
    """
    Verifica se o robo ja esta na rampa

    """

    global quant_bonecos, final, sentido

    funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 100)
    funcao_motores.acelerar(0, 500)

    if not cor_atual1 == ColorSensor.COLOR_BLUE and not cor_atual2 == ColorSensor.COLOR_BLUE:
        funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR), 400)
        funcao_motores.acelerar(0, 300)
        return
    else:
        inicio = time()
        while cor_atual1 != ColorSensor.COLOR_RED and cor_atual2 != ColorSensor.COLOR_RED:
            funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR)
            fim = time()
            if fim - inicio >= 0.8:
                funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR),
                                                   (fim - inicio) * 1000)
                funcao_motores.acelerar(0, 300)
                return

        funcao_motores.acelerar(0, 300)
        inicio = time()
        while cor_atual1 != ColorSensor.COLOR_GREEN and cor_atual2 != ColorSensor.COLOR_GREEN:
            funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR)
            fim = time()
            if fim - inicio >= 0.8:
                funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR),
                                                   (fim - inicio) * 1000)
                funcao_motores.acelerar(0, 300)
                return

        final = True
        funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 5000)
        quant_bonecos = 2
        return


def percurso():
    """
    Funcao principal do robo, onde ele vai se ajustando de acordo com os valores do PID e verifica se encontrou alguma
    cor

    """

    global sentido, quant_idas, quant_bonecos, boneco_esq, boneco_dir

    while True:
        if botao.enter:
            parar_motor()
            reseta_variaveis()
            main()

        if angulo_atual + ANGULO_DESVIO <= GYRO.value():
            funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR), 400)
            esquerda_giroscopio(ANGULO_DESVIO)
            funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 500)
        elif angulo_atual - ANGULO_DESVIO >= GYRO.value():
            funcao_motores.acelerar_individual(-1 * VELOCIDADE_ATUAL, -1 * (VELOCIDADE_ATUAL + AJUSTE_MOTOR), 400)
            direita_giroscopio(ANGULO_DESVIO)
            funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 500)

        if quant_bonecos < 2 and sentido == "INDO":
            if boneco_esq:
                quant_bonecos += 1
                pega_bonecos("ESQUERDA")
                boneco_esq = False
            elif boneco_dir:
                quant_bonecos += 1
                pega_bonecos("DIREITA")
                boneco_dir = False

        if sum(cores_indo) == sum(cores_voltando) and sum(cores_indo) != 0 and sum(cores_voltando) != 0:
            funcao_motores.acelerar_individual(VELOCIDADE_ATUAL, VELOCIDADE_ATUAL + AJUSTE_MOTOR, 1000)
            direita_giroscopio(ANGULO_CURVA_180)
            for nomes in relacao_cores.keys():
                if relacao_cores[nomes] == "DIREITA":
                    relacao_cores[nomes] = "ESQUERDA"
                elif relacao_cores[nomes] == "ESQUERDA":
                    relacao_cores[nomes] = "DIREITA"
            for index in cores_indo:
                cores_indo[index] = 0
                cores_voltando[index] = 0
            quant_idas += 1
            sentido = "INDO"
            quant_bonecos = 0

        velocidade_esq, velocidade_dir = controle_proporcional()
        funcao_motores.acelerar_ajustando(velocidade_dir, velocidade_esq)

        if cor_atual1 == ColorSensor.COLOR_GREEN and cor_atual2 == ColorSensor.COLOR_GREEN:

            achou_cor("VERDE", ColorSensor.COLOR_GREEN, 1)
            if sentido == "INDO":
                cores_indo[1] += 1
            elif sentido == "VOLTANDO":
                cores_voltando[1] += 1
            break
        elif cor_atual1 == ColorSensor.COLOR_RED and cor_atual2 == ColorSensor.COLOR_RED:

            achou_cor("VERMELHO", ColorSensor.COLOR_RED, 0)
            if sentido == "INDO":
                cores_indo[0] += 1
            elif sentido == "VOLTANDO":
                cores_voltando[0] += 1
            break
        elif cor_atual1 == ColorSensor.COLOR_BLUE and cor_atual2 == ColorSensor.COLOR_BLUE:

            eh_rampa()
            achou_cor("AZUL", ColorSensor.COLOR_BLUE, 2)
            if sentido == "INDO":
                cores_indo[2] += 1
            elif sentido == "VOLTANDO":
                cores_voltando[2] += 1
            break
        elif cor_atual1 == ColorSensor.COLOR_BLACK and cor_atual2 == ColorSensor.COLOR_BLACK:

            if final:
                chegou_final()
            else:
                achou_cor("PRETO", ColorSensor.COLOR_BLACK)


def main():
    global OFFSET, angulo_atual

    print("\n\n\n\n\n\n\n\n\n\n   ----- Botao do meio para iniciar -----")
    while True:
        if botao.enter:
            system("clear")
            OFFSET = PROX1.value() - PROX2.value()
            angulo_atual = GYRO.value()
            break

    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()

    while True:
        percurso()


if __name__ == '__main__':
    main()
