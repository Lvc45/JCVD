import time
import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor
from gpiozero import InputDevice

# === Initialisation des capteurs IR ===
LEFT_SENSOR = InputDevice(22)
MIDDLE_SENSOR = InputDevice(27)
RIGHT_SENSOR = InputDevice(17)

# === Initialisation I2C pour le Robot HAT ===
i2c = busio.I2C(SCL, SDA)
pwm = PCA9685(i2c, address=0x5f)  # Remplace par 0x40 si nécessaire
pwm.frequency = 1000

# === Initialisation moteur M1 (marche/arrêt uniquement) ===
motor1 = motor.DCMotor(pwm.channels[15], pwm.channels[14])
motor1.decay_mode = motor.SLOW_DECAY

def avancer(vitesse=0.6):
    print("→ AVANCER")
    motor1.throttle = vitesse

def stop():
    print("→ STOP")
    motor1.throttle = 0

# === Boucle principale ===
try:
    print("Suivi de ligne actif... Ctrl+C pour arrêter.")
    while True:
        left = LEFT_SENSOR.value
        middle = MIDDLE_SENSOR.value
        right = RIGHT_SENSOR.value

        print(f"Capteurs : L={left} | M={middle} | R={right}")

        if middle == 1:
            avancer()
        else:
            stop()

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Arrêt manuel.")
    stop()
    pwm.deinit()
