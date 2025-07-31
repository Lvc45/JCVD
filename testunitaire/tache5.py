from gpiozero import DistanceSensor
from time import sleep

Tr = 23
Ec = 24
sensor = DistanceSensor(echo=Ec, trigger=Tr,max_distance=2) # Maximum detection distance 2m.

# Get the distance of ultrasonic detection.
def checkdist():
    return (sensor.distance) *100 # Unit: cm

if __name__ == "__main__":
    print("Mesure de la distance à l'aide du capteur à ultrason")
    while True:
        distance = checkdist() 
        print("Distance de l'obstacle : %.2f cm" %distance)
        sleep(0.2)
