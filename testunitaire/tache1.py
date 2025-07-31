import RPi.GPIO as GPIO
import time

def switchSetup():
    """Configuration initiale des GPIO pour toutes les LEDs"""
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    # Configuration des LEDs HAT 3.1
    GPIO.setup(9, GPIO.OUT)   # LED1
    GPIO.setup(25, GPIO.OUT)  # LED2
    GPIO.setup(11, GPIO.OUT)  # LED3
    
    # Configuration des LEDs RGB feux avant (logique inversée)
    GPIO.setup(0, GPIO.OUT)   # left_R
    GPIO.setup(19, GPIO.OUT)  # left_G
    GPIO.setup(13, GPIO.OUT)  # left_B
    GPIO.setup(1, GPIO.OUT)   # right_R
    GPIO.setup(5, GPIO.OUT)   # right_G
    GPIO.setup(6, GPIO.OUT)   # right_B
    
    # Initialisation: LEDs HAT éteintes, LEDs avant éteintes (HIGH car logique inversée)
    GPIO.output(9, GPIO.LOW)
    GPIO.output(25, GPIO.LOW)
    GPIO.output(11, GPIO.LOW)
    GPIO.output(0, GPIO.HIGH)
    GPIO.output(19, GPIO.HIGH)
    GPIO.output(13, GPIO.HIGH)
    GPIO.output(1, GPIO.HIGH)
    GPIO.output(5, GPIO.HIGH)
    GPIO.output(6, GPIO.HIGH)

def switch(led_number, status):
    """
    Contrôle individuel d'une LED en mode ON/OFF
    Args:
        led_number (int): Numéro de LED (1-9)
        status (int): 1 pour allumer, 0 pour éteindre
    """
    # Mapping des LEDs avec leurs GPIO et noms
    led_config = {
        1: {'pin': 9, 'name': 'LED1', 'type': 'hat'},
        2: {'pin': 25, 'name': 'LED2', 'type': 'hat'},
        3: {'pin': 11, 'name': 'LED3', 'type': 'hat'},
        4: {'pin': 0, 'name': 'left_R', 'type': 'front'},
        5: {'pin': 19, 'name': 'left_G', 'type': 'front'},
        6: {'pin': 13, 'name': 'left_B', 'type': 'front'},
        7: {'pin': 1, 'name': 'right_R', 'type': 'front'},
        8: {'pin': 5, 'name': 'right_G', 'type': 'front'},
        9: {'pin': 6, 'name': 'right_B', 'type': 'front'}
    }
    
    if led_number not in led_config:
        print(f"Erreur: LED {led_number} n'existe pas (1-9)")
        return
    
    led = led_config[led_number]
    
    if led['type'] == 'hat':
        # LEDs HAT: GPIO.HIGH = allumé, GPIO.LOW = éteint
        if status == 1:
            GPIO.output(led['pin'], GPIO.HIGH)
            print(f"{led['name']} allumée")
        elif status == 0:
            GPIO.output(led['pin'], GPIO.LOW)
            print(f"{led['name']} éteinte")
        else:
            print(f"Erreur: Status invalide pour {led['name']} (0 ou 1)")
    
    elif led['type'] == 'front':
        # LEDs avant: GPIO.LOW = allumé, GPIO.HIGH = éteint (logique inversée)
        if status == 1:
            GPIO.output(led['pin'], GPIO.LOW)
            print(f"{led['name']} allumée")
        elif status == 0:
            GPIO.output(led['pin'], GPIO.HIGH)
            print(f"{led['name']} éteinte")
        else:
            print(f"Erreur: Status invalide pour {led['name']} (0 ou 1)")

def set_all_switch_off():
    """Éteint toutes les LEDs"""
    for led_number in range(1, 10):
        switch(led_number, 0)

def set_all_switch_on():
    """Allume toutes les LEDs"""
    for led_number in range(1, 10):
        switch(led_number, 1)

def main():
    """
    Programme principal avec contrôle manuel des LEDs
    Codes de commande selon le cahier des charges:
    - 11 à 19: Allumer LED1 à LED9 (right_B)
    - 21 à 29: Éteindre LED1 à LED9 (right_B)
    """
    print("=== TÂCHE 1 - Contrôle des LEDs HAT3.1 et feux avant ===")
    print("Initialisation du système...")
    
    # Configuration initiale
    switchSetup()
    
    print("Configuration terminée!")
    print("\n=== Mapping des LEDs ===")
    print("1: LED1 (GPIO 9)")
    print("2: LED2 (GPIO 25)")
    print("3: LED3 (GPIO 11)")
    print("4: left_R (GPIO 0) - logique inversée")
    print("5: left_G (GPIO 19) - logique inversée")
    print("6: left_B (GPIO 13) - logique inversée")
    print("7: right_R (GPIO 1) - logique inversée")
    print("8: right_G (GPIO 5) - logique inversée")
    print("9: right_B (GPIO 6) - logique inversée")
    
    print("\n=== Codes de commande ===")
    print("11-19: Allumer LED 1-9")
    print("21-29: Éteindre LED 1-9")
    print("0: Éteindre toutes les LEDs")
    print("99: Allumer toutes les LEDs")
    print("quit: Quitter le programme")
    
    try:
        while True:
            print("\n" + "-"*50)
            command = input("Entrez le code de commande: ").strip()
            
            if command.lower() in ['quit', 'exit']:
                print("Arrêt du programme...")
                break
            
            elif command == '0':
                print("Extinction de toutes les LEDs...")
                set_all_switch_off()
                
            elif command == '99':
                print("Allumage de toutes les LEDs...")
                set_all_switch_on()
                
            elif command.isdigit() and len(command) == 2:
                action = int(command[0])
                led_num = int(command[1])
                
                if led_num < 1 or led_num > 9:
                    print("Erreur: Numéro de LED invalide (1-9)")
                    continue
                
                if action == 1:
                    # Allumer LED
                    switch(led_num, 1)
                elif action == 2:
                    # Éteindre LED
                    switch(led_num, 0)
                else:
                    print("Erreur: Action invalide (1=allumer, 2=éteindre)")
            
            else:
                print("Code de commande invalide!")
                print("Utilisez: 11-19 (allumer), 21-29 (éteindre), 0 (tout éteindre), 99 (tout allumer)")
    
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur")
    
    finally:
        print("Nettoyage: extinction de toutes les LEDs...")
        set_all_switch_off()
        GPIO.cleanup()
        print("Nettoyage GPIO terminé")

if __name__ == "__main__":
    main()