#!/usr/bin/env python3

from ev3dev.ev3 import UltrasonicSensor, ColorSensor, Button
from os import system
import paho.mqtt.client as mqtt

# Sensores ultrasonicos
ULTRA1 = UltrasonicSensor("in1")
ULTRA2 = UltrasonicSensor("in2")
ULTRA1.mode = "US-DIST-CM"
ULTRA2.mode = "US-DIST-CM"

# Sensores de Cor
CL1 = ColorSensor("in3")
CL2 = ColorSensor("in4")
CL1.mode = "COL-COLOR"
CL2.mode = "COL-COLOR"

DISTANCIA_BONECOS = 20
cor_anterior1 = ""
cor_anterior2 = ""
client = mqtt.Client()
botao = Button()
client.connect("localhost", 1883, 60)
client.loop_start()


def on_disconnect(client, userdata, rc=0):
    client.loop_stop()


client.on_disconnect = on_disconnect

print("\n\n\n\n\n\n\n\n\n\n   ----- Botao do meio para iniciar -----")
while True:
    if botao.enter:
        system("clear")
        break

while True:
    distancia1 = ULTRA1.value() / 10
    distancia2 = ULTRA2.value() / 10
    cor_atual1 = CL1.value()
    cor_atual2 = CL2.value()

    if cor_atual1 != cor_anterior1:
        client.publish(topic="topic/sensor/color1", payload=cor_atual1, qos=0, retain=False)
        cor_anterior1 = cor_atual1
    if cor_atual2 != cor_anterior2:
        client.publish(topic="topic/sensor/color2", payload=cor_atual2, qos=0, retain=False)
        cor_anterior2 = cor_atual2

    if distancia1 <= DISTANCIA_BONECOS:
        client.publish(topic="topic/sensor/ultrasonic1", payload=True, qos=0, retain=False)
    elif distancia2 <= DISTANCIA_BONECOS:
        client.publish(topic="topic/sensor/ultrasonic2", payload=True, qos=0, retain=False)
