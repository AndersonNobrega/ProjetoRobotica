class Motores:
    def __init__(self, motor_esquerdo, motor_direito, porta):
        self.m_esquerdo = motor_esquerdo
        self.m_direito = motor_direito
        self.porta = porta

    def acelerar(self, velocidade, tempo=0):
        # Se n receber tempo, roda infinitamente
        if tempo == 0:
            self.m_direito.run_forever(speed_sp=velocidade, stop_action='brake')
            self.m_esquerdo.run_forever(speed_sp=velocidade, stop_action='brake')
        else:
            self.m_direito.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
            self.m_esquerdo.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
            self.m_direito.wait_while('running')
            self.m_esquerdo.wait_while('running')

    def acelerar_esq(self, velocidade, tempo=0):

        if tempo == 0:
            self.m_esquerdo.run_forever(speed_sp=velocidade, stop_action='brake')
        else:
            self.m_esquerdo.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')

    def acelerar_dir(self, velocidade, tempo=0):
        if tempo == 0:
            self.m_direito.run_forever(speed_sp=velocidade, stop_action='brake')
        else:
            self.m_direito.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')

    def acelerar_ajustando(self, velocidade_direita, velocidade_esquerda):
        # Acelera infinitamente, mas com velocidade diferente em cada motor
        self.m_direito.run_forever(speed_sp=velocidade_direita)
        self.m_esquerdo.run_forever(speed_sp=velocidade_esquerda)

    def fazer_curva_dir_esteira(self, velocidade, tempo):
        # Faz curva pra esquerda no proprio eixo do robo
        self.m_direito.run_timed(time_sp=tempo, speed_sp=velocidade * -1, stop_action='brake')
        self.m_esquerdo.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        self.m_direito.wait_while('running')
        self.m_esquerdo.wait_while('running')

    def fazer_curva_esq_esteira(self, velocidade, tempo):
        # Faz curva pra direita no proprio eixo do robo
        self.m_direito.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        self.m_esquerdo.run_timed(time_sp=tempo, speed_sp=velocidade * -1, stop_action='brake')
        self.m_direito.wait_while('running')
        self.m_esquerdo.wait_while('running')

    def fazer_curva_dir_roda(self, velocidade, tempo):
        # Faz curva pra esquerda no proprio eixo do robo
        self.m_direito.run_timed(time_sp=tempo, speed_sp=0, stop_action='brake')
        self.m_esquerdo.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        self.m_direito.wait_while('running')
        self.m_esquerdo.wait_while('running')

    def fazer_curva_esq_roda(self, velocidade, tempo):
        # Faz curva pra esquerda no proprio eixo do robo
        self.m_direito.run_timed(time_sp=tempo, speed_sp=velocidade, stop_action='brake')
        self.m_esquerdo.run_timed(time_sp=tempo, speed_sp=0, stop_action='brake')
        self.m_direito.wait_while('running')
        self.m_esquerdo.wait_while('running')

    def acelerar_porta(self, velocidade, tempo=0):
        if tempo == 0:
            self.porta.run_forever(speed_sp=velocidade)
        else:
            self.porta.run_timed(time_sp=tempo, speed_sp=velocidade)
