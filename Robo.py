import ev3dev.ev3 as ev3
from ev3dev.ev3 import *
from time import sleep, time

class Robo:
    def __init__(self):
        self.M_ESQUERDO = ev3.LargeMotor('outA')
        self.M_DIREITO = ev3.LargeMotor('outB')
        self.M_GARRA = ev3.Motor('outC')

    def acelerar(self, velocidade=0, tempo=0):
        if tempo == 0:
            self.M_ESQUERDO.run_forever(speed_sp=velocidade, stop_action='brake')
            self.M_DIREITO.run_forever(speed_sp=velocidade, stop_action='brake')
            self.M_ESQUERDO.wait_while('running')
            self.M_DIREITO.wait_while('running')
        else:
            self.M_ESQUERDO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
            self.M_DIREITO.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
            self.M_ESQUERDO.wait_while('running')
            self.M_DIREITO.wait_while('running')
       
    def fazer_curva(self, posicao, velocidade, mtr):
       mtr.run_to_rel_pos(position_sp=posicao, speed_sp=velocidade, stop_action="hold")

class Sensores(Robo):

    def verifica_distancia(self, distancia1, distancia2):#passar IR.value() dentro de um loop
        if distancia1 > 4:
            Robo.fazer_curva(self, posicao=90, velocidade=-300, mtr=self.M_DIREITO)
            #verifica lado e faz ajuste no percurso
        elif distancia2 > 4:
            Robo.fazer_curva(self, 90, -300, mtr=self.M_ESQUERDO)
        else:
            Robo.acelerar(self, velocidade=-400, tempo=0)
    #def verificar_cor():