class PID:
    KP = 1.9
    velocidade_esq = 350
    velocidade_dir = 350

    @staticmethod
    def controle_proporcional(sensor1, sensor2):
        # Faz correção do percurso de acordo com os valores de distancia dos sensores
        try:
            distancia_direita = sensor1
            distancia_esquerda = sensor2
            erro = distancia_direita - distancia_esquerda
        except ValueError:
            erro = 0
        finally:
            s = PID.KP * erro
            PID.velocidade_dir -= s
            PID.velocidade_esq += s
