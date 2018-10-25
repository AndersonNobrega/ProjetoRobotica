#!/usr/bin/env python3

from ev3dev.ev3 import UltrasonicSensor, InfraredSensor
from Classes.PID import *
import paho.mqtt.client as mqtt

# Sensores ultrasonicos
ULTRA1 = UltrasonicSensor("in1")
ULTRA2 = UltrasonicSensor("in2")
ULTRA1.mode = "US-DIST-CM"
ULTRA2.mode = "US-DIST-CM"

# Sensores infravermelhos
PROX1 = InfraredSensor("in4")
PROX2 = InfraredSensor("in3")
PROX1.mode = "IR-PROX"
PROX2.mode = "IR-PROX"

KP = 3
KI = 0
KD = 0
pid = PID(KP, KI, KD)
client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()


def on_disconnect(client, userdata, rc=0):
    client.loop_stop()


client.on_disconnect = on_disconnect
offset = PROX1.value() - PROX2.value()

while True:
    distancia1 = ULTRA1.value() / 10
    # distancia2 = ULTRA2.value() / 10
    # erro = (PROX1.value() - PROX2.value()) - offset
    # pid.update(erro)
    # correcao = pid.output

    # client.publish(topic="topic/sensor/pid", payload=correcao, qos=0)
    client.publish(topic="topic/sensor/ultrasonic1", payload=distancia1, qos=0, retain=False)
    # elif distancia2 <= DISTANCIA_BONECOS:
    # client.publish("topic/sensor/ultrasonic2", True)
