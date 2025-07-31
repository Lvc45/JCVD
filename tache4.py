#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                            TÂCHE 4 - PILOTAGE MOTEUR DC
                           Basé sur motor.py d'Adeept
═══════════════════════════════════════════════════════════════════════════════

OBJECTIF:
    Piloter le moteur DC de déplacement du Robot avec:
    1. Fonction simple de pilotage à faible vitesse (~25% du max)
    2. Rampe de montée en vitesse d'environ 1 seconde pour 0 à vitesse max
    3. Fonction avec 3 paramètres : vitesse, sens, pente de la rampe
    4. Commande manuelle pour test
    5. Étalonnage du servomoteur de direction

CONFIGURATION IDENTIFIÉE:
    • Moteur de propulsion: MOTEUR 1 (canaux 15-14)
    • Adresse I2C: 0x5f
    • Fonction de contrôle: Motor(1, direction, speed)

ATTENTION: 
    Module de transmission fragile - vitesse limitée à 25% pour sécurité!
"""

import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor

# ═══════════════════════════════════════════════════════════════════════════════
#                           CONFIGURATION SYSTÈME
# ═══════════════════════════════════════════════════════════════════════════════

# Configuration moteurs (reproduction exacte motor.py Adeept)
MOTOR_M1_IN1 = 15    # Moteur 1 - pole positif
MOTOR_M1_IN2 = 14    # Moteur 1 - pole négatif
MOTOR_M2_IN1 = 12    # Moteur 2 - pole positif
MOTOR_M2_IN2 = 13    # Moteur 2 - pole négatif
MOTOR_M3_IN1 = 11    # Moteur 3 - pole positif
MOTOR_M3_IN2 = 10    # Moteur 3 - pole négatif
MOTOR_M4_IN1 = 8     # Moteur 4 - pole positif
MOTOR_M4_IN2 = 9     # Moteur 4 - pole négatif

# Constantes de direction
DIR_FORWARD = 1      # Direction avant
DIR_BACKWARD = -1    # Direction arrière

# Configuration Tâche 4
PROPULSION_MOTOR = 1     # Moteur de propulsion identifié
MAX_SAFE_SPEED = 25      # Vitesse maximum sécurisée (25%)
MIN_RAMP_TIME = 0.1      # Temps minimum de rampe

# ═══════════════════════════════════════════════════════════════════════════════
#                        FONCTIONS ADEEPT ORIGINALES
# ═══════════════════════════════════════════════════════════════════════════════

def map_function(x, in_min, in_max, out_min, out_max):
    """Fonction de mapping Adeept - convertit une plage vers une autre"""
    return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

# Configuration I2C et moteurs (exacte d'Adeept)
print("🔧 Initialisation système Adeept...")

# Configuration I2C
i2c = busio.I2C(SCL, SDA)
pwm_motor = PCA9685(i2c, address=0x5f)
pwm_motor.frequency = 1000

# Création des 4 moteurs
motor1 = motor.DCMotor(pwm_motor.channels[MOTOR_M1_IN1], pwm_motor.channels[MOTOR_M1_IN2])
motor1.decay_mode = motor.SLOW_DECAY

motor2 = motor.DCMotor(pwm_motor.channels[MOTOR_M2_IN1], pwm_motor.channels[MOTOR_M2_IN2])
motor2.decay_mode = motor.SLOW_DECAY

motor3 = motor.DCMotor(pwm_motor.channels[MOTOR_M3_IN1], pwm_motor.channels[MOTOR_M3_IN2])
motor3.decay_mode = motor.SLOW_DECAY

motor4 = motor.DCMotor(pwm_motor.channels[MOTOR_M4_IN1], pwm_motor.channels[MOTOR_M4_IN2])
motor4.decay_mode = motor.SLOW_DECAY

def Motor(channel, direction, motor_speed):
    """
    Fonction Motor originale d'Adeept
    
    Args:
        channel (int): Canal moteur (1, 2, 3, 4)
        direction (int): Direction (1=avant, -1=arrière)
        motor_speed (int): Vitesse 0-100%
    """
    # Limitation vitesse
    if motor_speed > 100:
        motor_speed = 100
    elif motor_speed < 0:
        motor_speed = 0
    
    # Conversion vitesse
    speed = map_function(motor_speed, 0, 100, 0, 1.0)
    if direction == -1:
        speed = -speed
    
    # Application aux moteurs
    if channel == 1:
        motor1.throttle = speed
    elif channel == 2:
        motor2.throttle = speed
    elif channel == 3:
        motor3.throttle = speed
    elif channel == 4:
        motor4.throttle = speed

def motorStop():
    """Arrêt de tous les moteurs - fonction Adeept"""
    motor1.throttle = 0
    motor2.throttle = 0
    motor3.throttle = 0
    motor4.throttle = 0

def destroy():
    """Nettoyage système - fonction Adeept"""
    motorStop()
    pwm_motor.deinit()

print("✅ Système Adeept initialisé")

# ═══════════════════════════════════════════════════════════════════════════════
#                              TÂCHE 4 - CLASSE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

class Task4Controller:
    """Contrôleur principal pour la Tâche 4"""
    
    def __init__(self, motor_channel=PROPULSION_MOTOR):
        """
        Initialisation du contrôleur Tâche 4
        
        Args:
            motor_channel (int): Canal du moteur de propulsion (par défaut: 1)
        """
        self.motor_channel = motor_channel
        self.current_speed = 0
        self.current_direction = DIR_FORWARD
        self.is_running = False
        
        print(f"🤖 Contrôleur Tâche 4 initialisé")
        print(f"   Moteur de propulsion: {motor_channel}")
        print(f"   Vitesse max sécurisée: {MAX_SAFE_SPEED}%")
        
        # Test initial
        self._test_motor_connection()
    
    def _test_motor_connection(self):
        """Test de connexion du moteur sélectionné"""
        print(f"🧪 Test connexion moteur {self.motor_channel}...")
        try:
            Motor(self.motor_channel, DIR_FORWARD, 5)  # Test 5%
            time.sleep(0.3)
            Motor(self.motor_channel, DIR_FORWARD, 0)
            print("   ✅ Moteur répond correctement")
        except Exception as e:
            print(f"   ❌ Erreur test moteur: {e}")
    
    def _validate_speed(self, speed):
        """Validation et limitation de vitesse"""
        if speed > 100:
            print(f"   ⚠ Vitesse limitée de {speed}% à 100%")
            return 100
        elif speed < 0:
            print(f"   ⚠ Vitesse corrigée de {speed}% à 0%")
            return 0
        return speed
    
    def _validate_direction(self, direction):
        """Validation de direction"""
        if direction not in [DIR_FORWARD, DIR_BACKWARD]:
            print(f"   ⚠ Direction invalide {direction}, utilisation de {DIR_FORWARD}")
            return DIR_FORWARD
        return direction
    
    def _update_status(self, speed, direction):
        """Mise à jour du statut interne"""
        self.current_speed = speed
        self.current_direction = direction
        self.is_running = (speed > 0)
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                           TÂCHE 4.1 - FONCTION SIMPLE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def simple_control(self, command):
        """
        1. Fonction simple de pilotage à faible vitesse (~25% du max)
        
        Args:
            command (str): Commande ("avant", "arriere", "arret")
        """
        print(f"🐌 Fonction simple - Commande: {command}")
        
        command = command.lower().strip()
        
        if command == "avant":
            Motor(self.motor_channel, DIR_FORWARD, MAX_SAFE_SPEED)
            self._update_status(MAX_SAFE_SPEED, DIR_FORWARD)
            print(f"   → Marche avant à {MAX_SAFE_SPEED}%")
            
        elif command == "arriere":
            Motor(self.motor_channel, DIR_BACKWARD, MAX_SAFE_SPEED)
            self._update_status(MAX_SAFE_SPEED, DIR_BACKWARD)
            print(f"   → Marche arrière à {MAX_SAFE_SPEED}%")
            
        elif command == "arret":
            Motor(self.motor_channel, DIR_FORWARD, 0)
            self._update_status(0, DIR_FORWARD)
            print("   → Arrêt moteur")
            
        else:
            print(f"   ❌ Commande inconnue: '{command}'")
            print("       Commandes valides: 'avant', 'arriere', 'arret'")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                         TÂCHE 4.2 - RAMPE 1 SECONDE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def ramp_1_second(self, target_speed, direction=DIR_FORWARD):
        """
        2. Rampe de montée en vitesse d'environ 1 seconde pour 0 à vitesse max
        
        Args:
            target_speed (int): Vitesse cible (0-100%)
            direction (int): Direction (DIR_FORWARD ou DIR_BACKWARD)
        """
        # Validation des paramètres
        target_speed = self._validate_speed(target_speed)
        direction = self._validate_direction(direction)
        
        direction_str = "avant" if direction == DIR_FORWARD else "arrière"
        print(f"📈 Rampe 1 seconde - 0 → {target_speed}% ({direction_str})")
        
        # Arrêt initial pour sécurité
        Motor(self.motor_channel, DIR_FORWARD, 0)
        time.sleep(0.1)
        
        # Configuration rampe
        ramp_duration = 1.0  # 1 seconde exactement
        num_steps = 20       # 20 étapes = 50ms par étape
        step_delay = ramp_duration / num_steps
        speed_increment = target_speed / num_steps
        
        print(f"   Configuration: {num_steps} étapes, {step_delay*1000:.1f}ms/étape")
        
        try:
            # Exécution de la rampe
            for step in range(num_steps + 1):
                current_speed = int(speed_increment * step)
                Motor(self.motor_channel, direction, current_speed)
                
                # Affichage progrès (tous les 4 étapes + final)
                if step % 4 == 0 or step == num_steps:
                    progress = (step / num_steps) * 100
                    print(f"   Étape {step:2d}/{num_steps}: {current_speed:3d}% ({progress:3.0f}%)")
                
                if step < num_steps:
                    time.sleep(step_delay)
            
            self._update_status(target_speed, direction)
            print(f"   ✅ Rampe terminée - Vitesse finale: {target_speed}%")
            
        except KeyboardInterrupt:
            print("\n   ⚠ Rampe interrompue par utilisateur")
            Motor(self.motor_channel, DIR_FORWARD, 0)
            self._update_status(0, DIR_FORWARD)
        except Exception as e:
            print(f"\n   ❌ Erreur pendant rampe: {e}")
            Motor(self.motor_channel, DIR_FORWARD, 0)
            self._update_status(0, DIR_FORWARD)
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                      TÂCHE 4.3 - RAMPE PERSONNALISÉE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def custom_ramp(self, vitesse, sens, pente_rampe):
        """
        3. Fonction avec 3 paramètres : vitesse, sens, pente de la rampe
        
        Args:
            vitesse (int): Vitesse cible (0-100%)
            sens (int): Direction (DIR_FORWARD=1 ou DIR_BACKWARD=-1)
            pente_rampe (float): Temps de rampe en secondes
        """
        # Validation des paramètres
        vitesse = self._validate_speed(vitesse)
        sens = self._validate_direction(sens)
        
        if pente_rampe < MIN_RAMP_TIME:
            print(f"   ⚠ Temps de rampe corrigé de {pente_rampe}s à {MIN_RAMP_TIME}s")
            pente_rampe = MIN_RAMP_TIME
        
        sens_str = "avant" if sens == DIR_FORWARD else "arrière"
        print(f"⚙️ Rampe personnalisée")
        print(f"   Vitesse cible: {vitesse}%")
        print(f"   Direction: {sens_str}")
        print(f"   Durée rampe: {pente_rampe}s")
        
        # Arrêt initial
        Motor(self.motor_channel, DIR_FORWARD, 0)
        time.sleep(0.1)
        
        # Calcul des étapes (min 10, max 100)
        num_steps = max(10, min(100, int(pente_rampe * 20)))
        step_delay = pente_rampe / num_steps
        speed_increment = vitesse / num_steps
        
        print(f"   Configuration: {num_steps} étapes, {step_delay*1000:.1f}ms/étape")
        
        try:
            # Exécution de la rampe
            for step in range(num_steps + 1):
                current_speed = int(speed_increment * step)
                Motor(self.motor_channel, sens, current_speed)
                
                # Affichage progrès (tous les 10% + final)
                if step % max(1, num_steps // 10) == 0 or step == num_steps:
                    progress = (step / num_steps) * 100
                    print(f"   Étape {step:3d}/{num_steps}: {current_speed:3d}% ({progress:3.0f}%)")
                
                if step < num_steps:
                    time.sleep(step_delay)
            
            self._update_status(vitesse, sens)
            print(f"   ✅ Rampe personnalisée terminée")
            
        except KeyboardInterrupt:
            print("\n   ⚠ Rampe interrompue par utilisateur")
            Motor(self.motor_channel, DIR_FORWARD, 0)
            self._update_status(0, DIR_FORWARD)
        except Exception as e:
            print(f"\n   ❌ Erreur pendant rampe: {e}")
            Motor(self.motor_channel, DIR_FORWARD, 0)
            self._update_status(0, DIR_FORWARD)
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                        TÂCHE 4.4 - COMMANDE MANUELLE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def manual_control(self):
        """4. Interface de commande manuelle pour test"""
        print("\n" + "═" * 70)
        print("🎮 INTERFACE DE COMMANDE MANUELLE - TÂCHE 4")
        print("═" * 70)
        print(f"Moteur de propulsion: {self.motor_channel}")
        print(f"Vitesse max sécurisée: {MAX_SAFE_SPEED}%")
        print("═" * 70)
        
        self._show_manual_help()
        
        while True:
            try:
                # Affichage statut
                status = self._get_status_string()
                command = input(f"\n{status} | Commande: ").strip().lower()
                
                if command == 'q' or command == 'quit':
                    Motor(self.motor_channel, DIR_FORWARD, 0)
                    print("👋 Interface manuelle fermée")
                    break
                
                elif command == 'help' or command == 'h':
                    self._show_manual_help()
                
                elif command in ['avant', 'arriere', 'arret']:
                    self.simple_control(command)
                
                elif command == 'rampe':
                    self._handle_ramp_command()
                
                elif command == 'custom':
                    self._handle_custom_command()
                
                elif command.startswith('test'):
                    self._handle_test_command(command)
                
                elif command == 'stop':
                    Motor(self.motor_channel, DIR_FORWARD, 0)
                    self._update_status(0, DIR_FORWARD)
                    print("🛑 Arrêt d'urgence")
                
                elif command == 'status':
                    self._show_detailed_status()
                
                else:
                    print(f"❌ Commande inconnue: '{command}'")
                    print("   Tapez 'help' pour voir les commandes disponibles")
                    
            except KeyboardInterrupt:
                print("\n⚠ Interface interrompue")
                Motor(self.motor_channel, DIR_FORWARD, 0)
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def _show_manual_help(self):
        """Affichage de l'aide des commandes manuelles"""
        print("\n📋 COMMANDES DISPONIBLES:")
        print("  • 'avant'/'arriere'/'arret' : Contrôle simple")
        print("  • 'rampe'                  : Rampe 1 seconde")
        print("  • 'custom'                 : Rampe personnalisée")
        print("  • 'test X'                 : Test vitesse X%")
        print("  • 'stop'                   : Arrêt d'urgence")
        print("  • 'status'                 : Statut détaillé")
        print("  • 'help' ou 'h'            : Cette aide")
        print("  • 'q' ou 'quit'            : Quitter")
    
    def _get_status_string(self):
        """Génération de la chaîne de statut"""
        if self.is_running:
            direction_str = "AVANT" if self.current_direction == DIR_FORWARD else "ARRIÈRE"
            return f"🟢 M{self.motor_channel}: {self.current_speed}% {direction_str}"
        else:
            return f"🔴 M{self.motor_channel}: ARRÊTÉ"
    
    def _show_detailed_status(self):
        """Affichage du statut détaillé"""
        print("📊 STATUT DÉTAILLÉ:")
        print(f"   Moteur: {self.motor_channel}")
        print(f"   Vitesse: {self.current_speed}%")
        print(f"   Direction: {'Avant' if self.current_direction == DIR_FORWARD else 'Arrière'}")
        print(f"   État: {'En marche' if self.is_running else 'Arrêté'}")
        print(f"   Sécurité: Vitesse max {MAX_SAFE_SPEED}%")
    
    def _handle_ramp_command(self):
        """Gestion de la commande rampe"""
        try:
            direction_input = input("   Direction (avant/arriere): ").strip().lower()
            direction = DIR_FORWARD if direction_input == 'avant' else DIR_BACKWARD
            
            vitesse_input = input(f"   Vitesse cible (max {MAX_SAFE_SPEED}%): ").strip()
            vitesse = min(int(vitesse_input), MAX_SAFE_SPEED)
            
            self.ramp_1_second(vitesse, direction)
            
        except ValueError:
            print("   ❌ Vitesse invalide")
        except KeyboardInterrupt:
            print("\n   ⚠ Commande annulée")
    
    def _handle_custom_command(self):
        """Gestion de la commande custom"""
        try:
            vitesse = int(input("   Vitesse (0-100%): "))
            sens_input = input("   Sens (avant/arriere): ").strip().lower()
            sens = DIR_FORWARD if sens_input == 'avant' else DIR_BACKWARD
            pente = float(input("   Temps de rampe (secondes): "))
            
            self.custom_ramp(vitesse, sens, pente)
            
        except ValueError:
            print("   ❌ Paramètres invalides")
        except KeyboardInterrupt:
            print("\n   ⚠ Commande annulée")
    
    def _handle_test_command(self, command):
        """Gestion des commandes de test"""
        try:
            parts = command.split()
            if len(parts) == 2:
                speed = int(parts[1])
                if 0 <= speed <= 50:
                    print(f"   Test {speed}% pendant 2 secondes...")
                    Motor(self.motor_channel, DIR_FORWARD, speed)
                    time.sleep(2)
                    Motor(self.motor_channel, DIR_FORWARD, 0)
                    self._update_status(0, DIR_FORWARD)
                    print("   ✅ Test terminé")
                else:
                    print("   ❌ Vitesse doit être entre 0 et 50%")
            else:
                print("   ❌ Format: test [vitesse]")
        except ValueError:
            print("   ❌ Vitesse invalide")

# ═══════════════════════════════════════════════════════════════════════════════
#                            FONCTIONS DE DÉMONSTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def demo_original_adeept():
    """Démonstration du code original Adeept"""
    print("\n🧪 DÉMONSTRATION CODE ORIGINAL ADEEPT")
    print("─" * 50)
    print("Reproduction exacte du main() du fichier motor.py")
    
    try:
        channel = 1  # Comme dans motor.py original
        
        for iteration in range(2):
            print(f"\n→ Itération {iteration + 1}/2")
            
            speed_set = 25  # Réduit pour sécurité (était 110 dans l'original)
            
            Motor(channel, DIR_FORWARD, speed_set)
            print("Forward")
            time.sleep(2)
            
            Motor(channel, DIR_BACKWARD, speed_set)
            print("Backward")
            time.sleep(2)
        
        destroy()
        print("\n✅ Démonstration Adeept terminée")
        
    except KeyboardInterrupt:
        print("\n⚠ Démonstration interrompue")
        destroy()

def demo_task4_complete():
    """Démonstration complète de la Tâche 4"""
    print("\n🚀 DÉMONSTRATION COMPLÈTE TÂCHE 4")
    print("─" * 50)
    
    controller = Task4Controller(PROPULSION_MOTOR)
    
    try:
        # Test 1: Fonction simple
        print("\n1️⃣ TEST FONCTION SIMPLE")
        print("   Marche avant...")
        controller.simple_control("avant")
        time.sleep(2)
        print("   Arrêt...")
        controller.simple_control("arret")
        time.sleep(1)
        
        # Test 2: Rampe 1 seconde
        print("\n2️⃣ TEST RAMPE 1 SECONDE")
        controller.ramp_1_second(20, DIR_FORWARD)
        time.sleep(1)
        Motor(PROPULSION_MOTOR, DIR_FORWARD, 0)
        time.sleep(1)
        
        # Test 3: Rampe personnalisée
        print("\n3️⃣ TEST RAMPE PERSONNALISÉE")
        controller.custom_ramp(vitesse=25, sens=DIR_BACKWARD, pente_rampe=2.0)
        time.sleep(1)
        Motor(PROPULSION_MOTOR, DIR_FORWARD, 0)
        
        print("\n✅ DÉMONSTRATION COMPLÈTE TERMINÉE")
        
    except KeyboardInterrupt:
        print("\n⚠ Démonstration interrompue")
    finally:
        destroy()

def quick_motor_test():
    """Test rapide du moteur de propulsion"""
    print("\n⚡ TEST RAPIDE MOTEUR DE PROPULSION")
    print("─" * 40)
    
    try:
        print("Test avant 15%...")
        Motor(PROPULSION_MOTOR, DIR_FORWARD, 15)
        time.sleep(1.5)
        
        print("Test arrière 15%...")
        Motor(PROPULSION_MOTOR, DIR_BACKWARD, 15)
        time.sleep(1.5)
        
        print("Arrêt...")
        Motor(PROPULSION_MOTOR, DIR_FORWARD, 0)
        
        print("✅ Test rapide terminé")
        
    except KeyboardInterrupt:
        print("\n⚠ Test interrompu")
        Motor(PROPULSION_MOTOR, DIR_FORWARD, 0)

# ═══════════════════════════════════════════════════════════════════════════════
#                              PROGRAMME PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Programme principal - Menu de sélection des fonctionnalités"""
    
    print("\n" + "═" * 80)
    print("🤖 TÂCHE 4 - PILOTAGE MOTEUR DC DE DÉPLACEMENT DU ROBOT")
    print("═" * 80)
    print("📋 CONFIGURATION VALIDÉE:")
    print(f"   • Moteur de propulsion: {PROPULSION_MOTOR} (canaux {MOTOR_M1_IN1}-{MOTOR_M1_IN2})")
    print(f"   • Adresse I2C: 0x5f")
    print(f"   • Vitesse sécurisée: {MAX_SAFE_SPEED}% maximum")
    print(f"   • Fonction de contrôle: Motor({PROPULSION_MOTOR}, direction, speed)")
    print("═" * 80)
    print("🛡️ SÉCURITÉ: Transmission fragile - vitesse limitée pour protection")
    print("═" * 80)
    
    while True:
        print("\n📋 MENU PRINCIPAL:")
        print("┌─────────────────────────────────────────────┐")
        print("│  1. ⚡ Test rapide moteur propulsion        │")
        print("│  2. 🧪 Démonstration code original Adeept   │")
        print("│  3. 🚀 Démonstration complète Tâche 4       │")
        print("│  4. 🎮 Interface manuelle interactive       │")
        print("│  5. 🔧 Tests individuels des fonctions      │")
        print("│  6. 🏁 Quitter le programme                 │")
        print("└─────────────────────────────────────────────┘")
        
        try:
            choice = input("\n➤ Choisissez une option (1-6): ").strip()
            
            if choice == "1":
                quick_motor_test()
                
            elif choice == "2":
                demo_original_adeept()
                
            elif choice == "3":
                demo_task4_complete()
                
            elif choice == "4":
                controller = Task4Controller(PROPULSION_MOTOR)
                controller.manual_control()
                destroy()
                
            elif choice == "5":
                submenu_individual_tests()
                
            elif choice == "6":
                destroy()
                print("\n👋 Programme terminé - Au revoir!")
                break
                
            else:
                print("❌ Option invalide - Choisissez entre 1 et 6")
                
        except KeyboardInterrupt:
            print("\n⚠ Programme interrompu")
            destroy()
            break
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            destroy()

def submenu_individual_tests():
    """Sous-menu pour les tests individuels"""
    controller = Task4Controller(PROPULSION_MOTOR)
    
    while True:
        print("\n🔧 TESTS INDIVIDUELS DES FONCTIONS:")
        print("┌────────────────────────────────────────┐")
        print("│  1. 🐌 Test fonction simple            │")
        print("│  2. 📈 Test rampe 1 seconde            │")
        print("│  3. ⚙️  Test rampe personnalisée        │")
        print("│  4. 📊 Afficher statut moteur          │")
        print("│  5. 🔙 Retour au menu principal        │")
        print("└────────────────────────────────────────┘")
        
        try:
            choice = input("\n➤ Choisissez un test (1-5): ").strip()
            
            if choice == "1":
                print("\n🐌 TEST FONCTION SIMPLE")
                print("─" * 30)
                test_command = input("Commande (avant/arriere/arret): ").strip()
                controller.simple_control(test_command)
                if test_command != "arret":
                    time.sleep(2)
                    controller.simple_control("arret")
                
            elif choice == "2":
                print("\n📈 TEST RAMPE 1 SECONDE")
                print("─" * 30)
                try:
                    speed = int(input(f"Vitesse cible (max {MAX_SAFE_SPEED}%): "))
                    direction_input = input("Direction (avant/arriere): ").strip().lower()
                    direction = DIR_FORWARD if direction_input == "avant" else DIR_BACKWARD
                    
                    controller.ramp_1_second(speed, direction)
                    time.sleep(1)
                    Motor(PROPULSION_MOTOR, DIR_FORWARD, 0)
                    
                except ValueError:
                    print("❌ Vitesse invalide")
                
            elif choice == "3":
                print("\n⚙️ TEST RAMPE PERSONNALISÉE")
                print("─" * 30)
                try:
                    vitesse = int(input("Vitesse (0-100%): "))
                    sens_input = input("Sens (avant/arriere): ").strip().lower()
                    sens = DIR_FORWARD if sens_input == "avant" else DIR_BACKWARD
                    pente = float(input("Temps de rampe (secondes): "))
                    
                    controller.custom_ramp(vitesse, sens, pente)
                    time.sleep(1)
                    Motor(PROPULSION_MOTOR, DIR_FORWARD, 0)
                    
                except ValueError:
                    print("❌ Paramètres invalides")
                
            elif choice == "4":
                controller._show_detailed_status()
                
            elif choice == "5":
                Motor(PROPULSION_MOTOR, DIR_FORWARD, 0)
                break
                
            else:
                print("❌ Option invalide - Choisissez entre 1 et 5")
                
        except KeyboardInterrupt:
            print("\n⚠ Test interrompu")
            Motor(PROPULSION_MOTOR, DIR_FORWARD, 0)
            break
    
    destroy()

# ═══════════════════════════════════════════════════════════════════════════════
#                            TÂCHE 4.5 - ÉTALONNAGE SERVO
# ═══════════════════════════════════════════════════════════════════════════════

def servo_calibration():
    """5. Étalonnage du servomoteur de direction (bonus)"""
    try:
        import Adafruit_PCA9685
        
        print("\n🔧 ÉTALONNAGE SERVOMOTEUR DE DIRECTION")
        print("═" * 50)
        print("ATTENTION: Surveillez les servos pendant l'étalonnage!")
        print("Arrêtez avec Ctrl+C si quelque chose force!")
        print("═" * 50)
        
        # Configuration servo (adresse 0x40 ou 0x5f selon le robot)
        try:
            servo_pwm = Adafruit_PCA9685.PCA9685(address=0x40)
            servo_addr = "0x40"
        except:
            servo_pwm = Adafruit_PCA9685.PCA9685(address=0x5f)  # Même adresse que moteurs
            servo_addr = "0x5f"
            
        servo_pwm.set_pwm_freq(50)  # 50Hz pour servos
        print(f"✅ Servo configuré sur adresse {servo_addr}")
        
        # Canaux servos probables
        servo_channels = {
            0: "Direction des roues",
            1: "Tête gauche/droite", 
            2: "Tête haut/bas"
        }
        
        print("\n📍 PHASE 1: Identification des servos")
        print("─" * 40)
        
        identified_servos = {}
        
        for channel, description in servo_channels.items():
            print(f"\nTest servo canal {channel} ({description}):")
            
            # Test de mouvement
            for pwm_val in [250, 300, 350, 300]:
                servo_pwm.set_pwm(channel, 0, pwm_val)
                print(f"   PWM: {pwm_val}")
                time.sleep(0.8)
            
            response = input(f"   Un servo a-t-il bougé? (o/n): ").lower()
            if response == 'o':
                servo_name = input(f"   Quel servo? ({description}): ").strip()
                identified_servos[channel] = servo_name
                print(f"   ✅ Canal {channel} = {servo_name}")
        
        if not identified_servos:
            print("❌ Aucun servo identifié")
            return
        
        print(f"\n📊 SERVOS IDENTIFIÉS:")
        for channel, name in identified_servos.items():
            print(f"   Canal {channel}: {name}")
        
        # Étalonnage du servo de direction
        direction_channel = None
        for channel, name in identified_servos.items():
            if "direction" in name.lower() or "roue" in name.lower():
                direction_channel = channel
                break
        
        if direction_channel is not None:
            print(f"\n🎯 ÉTALONNAGE SERVO DE DIRECTION (Canal {direction_channel})")
            print("─" * 50)
            
            calibration_data = {}
            
            # Recherche du centre
            print("Recherche de la position centre...")
            center_values = [250, 275, 300, 325, 350]
            
            for pwm_val in center_values:
                servo_pwm.set_pwm(direction_channel, 0, pwm_val)
                response = input(f"PWM {pwm_val} - Roues droites? (o/n): ").lower()
                if response == 'o':
                    calibration_data['center'] = pwm_val
                    print(f"✅ Centre trouvé: PWM {pwm_val}")
                    break
            
            if 'center' not in calibration_data:
                calibration_data['center'] = 300
                print("⚠ Centre par défaut: PWM 300")
            
            # Recherche des limites ±50°
            center_pwm = calibration_data['center']
            
            print("\nRecherche limite gauche (-50°)...")
            for offset in [50, 75, 100]:
                left_pwm = center_pwm - offset
                servo_pwm.set_pwm(direction_channel, 0, left_pwm)
                response = input(f"PWM {left_pwm} - Limite gauche OK? (o/n): ").lower()
                if response == 'o':
                    calibration_data['left_50'] = left_pwm
                    break
            
            print("\nRecherche limite droite (+50°)...")
            for offset in [50, 75, 100]:
                right_pwm = center_pwm + offset
                servo_pwm.set_pwm(direction_channel, 0, right_pwm)
                response = input(f"PWM {right_pwm} - Limite droite OK? (o/n): ").lower()
                if response == 'o':
                    calibration_data['right_50'] = right_pwm
                    break
            
            # Retour au centre
            servo_pwm.set_pwm(direction_channel, 0, calibration_data['center'])
            
            # Résultats
            print("\n📊 RÉSULTATS ÉTALONNAGE:")
            print("─" * 30)
            print(f"Centre (0°):     PWM {calibration_data.get('center', 'N/A')}")
            print(f"Gauche (-50°):   PWM {calibration_data.get('left_50', 'N/A')}")
            print(f"Droite (+50°):   PWM {calibration_data.get('right_50', 'N/A')}")
            
            print("\n💾 CODE À UTILISER:")
            print(f"SERVO_CENTER = {calibration_data.get('center', 300)}")
            print(f"SERVO_LEFT_50 = {calibration_data.get('left_50', 250)}")
            print(f"SERVO_RIGHT_50 = {calibration_data.get('right_50', 350)}")
            
        print("\n✅ Étalonnage terminé")
        
    except ImportError:
        print("❌ Module Adafruit_PCA9685 non disponible")
    except KeyboardInterrupt:
        print("\n⚠ Étalonnage interrompu")
    except Exception as e:
        print(f"❌ Erreur étalonnage: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
#                               POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Point d'entrée du programme"""
    try:
        print("🚀 Démarrage du programme Tâche 4...")
        main()
    except KeyboardInterrupt:
        print("\n⚠ Programme interrompu par l'utilisateur")
        destroy()
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        destroy()
    finally:
        print("🔒 Nettoyage final du système...")
        try:
            destroy()
        except:
            pass
        print("✅ Programme terminé proprement")
