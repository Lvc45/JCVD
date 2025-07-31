#!/usr/bin/env python3

import time
import sys

try:
    import Adafruit_PCA9685
    print("Bibliotheque Adafruit_PCA9685 importee avec succes")
except ImportError:
    print("Erreur: Module Adafruit_PCA9685 non trouve")
    print("Installation: sudo pip3 install Adafruit-PCA9685")
    sys.exit(1)

class ServoController:
    def __init__(self):
        """Initialise le controleur PCA9685 a l'adresse 0x5f"""
        try:
            # PCA9685 a l'adresse 0x5f (selon votre configuration)
            self.pwm = Adafruit_PCA9685.PCA9685(address=0x5f, busnum=1)
            self.pwm.set_pwm_freq(50)
            print("PCA9685 initialise avec succes a l'adresse 0x5f sur bus I2C 1")
            
        except Exception as e:
            print(f"Erreur initialisation PCA9685 a 0x5f: {e}")
            print("Verifications:")
            print("1. sudo i2cdetect -y 1 (doit montrer 5f)")
            print("2. Robot HAT alimente et connecte")
            sys.exit(1)
        
        # Configuration des servos avec OFFSET DE CALIBRAGE
        self.servo_configs = {
            0: {"name": "Direction roues", "min_angle": -90, "max_angle": 5, "offset": -35},  # Roues - pas changé
            1: {"name": "Tete L/R", "min_angle": -90, "max_angle": 90, "offset": -45},        # Tête L/R - décalé de 5° de plus vers la DROITE
            2: {"name": "Tete H/B", "min_angle": -45, "max_angle": 45, "offset": -45},        # Tête H/B - décalé de 5° de plus vers la DROITE  
            15: {"name": "Servo libre", "min_angle": -90, "max_angle": 90, "offset": -45}     # Servo libre - décalé de 5° de plus vers la DROITE
        }
        
        # Positions actuelles (angles logiques, pas mécaniques)
        self.current_positions = {ch: 0 for ch in self.servo_configs.keys()}
        
        # Valeurs PWM calibrees pour servos standard
        self.servo_min = 150
        self.servo_max = 650
        self.servo_center = 400
        
        print("Configuration terminee - Initialisation des servos...")
        self.move_to_center()
    
    def angle_to_pwm(self, channel, logical_angle):
        """Convertit un angle logique en valeur PWM avec calibrage"""
        config = self.servo_configs[channel]
        
        # Appliquer l'offset de calibrage
        mechanical_angle = logical_angle + config["offset"]
        
        # Limiter l'angle mécanique
        mechanical_angle = max(-90, min(90, mechanical_angle))
        
        # Convertir en PWM
        pwm_range = self.servo_max - self.servo_min
        pwm_value = self.servo_center + int((mechanical_angle / 90.0) * (pwm_range / 2))
        return max(self.servo_min, min(self.servo_max, pwm_value))
    
    def set_angle(self, channel, logical_angle):
        """Definit l'angle logique d'un servo (avec calibrage automatique)"""
        if channel not in self.servo_configs:
            print(f"Canal {channel} non configure")
            return False
        
        config = self.servo_configs[channel]
        
        if logical_angle < config["min_angle"] or logical_angle > config["max_angle"]:
            print(f"Angle {logical_angle} hors limites pour {config['name']}")
            print(f"Limites: {config['min_angle']} a {config['max_angle']}")
            return False
        
        try:
            pwm_value = self.angle_to_pwm(channel, logical_angle)
            mechanical_angle = logical_angle + config["offset"]
            
            self.pwm.set_pwm(channel, 0, pwm_value)
            self.current_positions[channel] = logical_angle
            
            print(f"✓ {config['name']} (CH{channel}) -> {logical_angle:+4.0f}° logique "
                  f"({mechanical_angle:+4.0f}° mécanique, PWM: {pwm_value})")
            return True
            
        except Exception as e:
            print(f"✗ Erreur servo {channel}: {e}")
            return False
    
    def save_config_to_file(self):
        """Sauvegarde automatiquement la configuration dans le fichier"""
        try:
            # Lire le fichier actuel
            with open(__file__, 'r') as file:
                lines = file.readlines()
            
            # Modifier les lignes contenant les offsets
            for i, line in enumerate(lines):
                for channel, config in self.servo_configs.items():
                    if f'"{channel}":' in line and '"offset":' in line:
                        # Remplacer l'ancienne valeur d'offset
                        import re
                        new_line = re.sub(r'"offset":\s*[+-]?\d+', f'"offset": {config["offset"]}', line)
                        lines[i] = new_line
                        break
            
            # Écrire le fichier modifié
            with open(__file__, 'w') as file:
                file.writelines(lines)
            
            print(f"✅ Configuration sauvegardée dans {__file__}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return False
        """Assistant de calibrage pour un servo"""
        if channel not in self.servo_configs:
            print(f"Canal {channel} non configure")
            return
        
        config = self.servo_configs[channel]
        print(f"\n🔧 CALIBRAGE DU SERVO {channel} ({config['name']})")
        print("="*50)
        print("But: Trouver l'offset pour que 0° logique = centre mécanique")
        print("\nÉtapes:")
        print("1. Le servo va aller à différentes positions")
        print("2. Observez la position mécanique réelle")
        print("3. Indiquez quand le servo est au centre mécanique")
        
        input("\nAppuyez sur Entrée pour commencer...")
        
        # Test de plusieurs angles (focus sur les négatifs et près de zéro)
        test_angles = [-30, -25, -20, -15, -10, -8, -6, -4, -2, 0, 2, 4]
        
        for angle in test_angles:
            # Utiliser l'ancien calcul (sans offset) pour le calibrage
            mechanical_angle = angle
            pwm_range = self.servo_max - self.servo_min
            pwm_value = self.servo_center + int((mechanical_angle / 90.0) * (pwm_range / 2))
            pwm_value = max(self.servo_min, min(self.servo_max, pwm_value))
            
            self.pwm.set_pwm(channel, 0, pwm_value)
            print(f"\nPosition test: {angle}° (PWM: {pwm_value})")
            
            response = input("Est-ce le centre mécanique? (y/n/q pour quitter): ").strip().lower()
            
            if response == 'y':
                # L'utilisateur a trouvé le centre
                offset = -angle  # Si angle==-30 donne le centre, offset = +30
                config["offset"] = offset
                print(f"\n✅ Calibrage terminé!")
                print(f"   Offset trouvé: {offset}°")
                print(f"   Maintenant 0° logique = centre mécanique")
                print(f"   ⚠️  IMPORTANT: Pour sauvegarder définitivement,")
                print(f"   modifiez manuellement le fichier:")
                print(f"   Changez 'offset': {config['offset']-offset} en 'offset': {offset}")
                
                # Test du calibrage
                self.set_angle(channel, 0)
                input("\nVérifiez que le servo est maintenant au centre. Appuyez sur Entrée...")
                return
            
            elif response == 'q':
                print("❌ Calibrage annulé")
                return
        
        # Si aucune position n'était correcte
        print("\n⚠️  Aucune position ne correspondait au centre.")
        print("Vous pouvez ajuster manuellement l'offset dans le code:")
        print(f"Dans servo_configs[{channel}], changez 'offset': {config['offset']}")
    
    def test_servo(self, channel):
        """Test d'un servo avec mouvement fluide"""
        if channel not in self.servo_configs:
            print(f"Canal {channel} non configure")
            return
        
        config = self.servo_configs[channel]
        print(f"\n🧪 Test du servo {channel} ({config['name']})...")
        print(f"   Offset de calibrage: {config['offset']}°")
        
        min_angle = config["min_angle"]
        max_angle = config["max_angle"]
        
        # Mouvement lent de min a max
        print(f"   Mouvement {min_angle}° -> {max_angle}°")
        for angle in range(min_angle, max_angle + 1, 10):
            self.set_angle(channel, angle)
            time.sleep(0.2)
        
        time.sleep(0.5)
        
        # Mouvement rapide de max a min
        print(f"   Mouvement {max_angle}° -> {min_angle}°")
        for angle in range(max_angle, min_angle - 1, -15):
            self.set_angle(channel, angle)
            time.sleep(0.1)
        
        # Retour au centre
        print("   Retour au centre logique (0°)")
        self.set_angle(channel, 0)
        print(f"✅ Test servo {channel} termine")
    
    def move_to_center(self):
        """Place tous les servos au centre LOGIQUE (0°)"""
        print("\n🎯 Deplacement vers le centre logique...")
        for channel in self.servo_configs.keys():
            self.set_angle(channel, 0)
            time.sleep(0.3)
        print("✅ Tous les servos au centre logique")
    
    def show_status(self):
        """Affiche l'etat des servos"""
        print(f"\n📊 ETAT ACTUEL DES SERVOS")
        print("="*60)
        for channel, config in self.servo_configs.items():
            logical_pos = self.current_positions[channel]
            mechanical_pos = logical_pos + config["offset"]
            indicator = "●" if abs(logical_pos) < 10 else "◐" if abs(logical_pos) < 45 else "○"
            print(f"Servo {channel:2d}: {config['name']:<15} {indicator} "
                  f"{logical_pos:+4.0f}° logique ({mechanical_pos:+4.0f}° mécanique)")
        print("="*60)
    
    def get_help(self):
        """Affiche l'aide"""
        print(f"\n{'='*55}")
        print("🤖 CONTROLEUR SERVO - ADRESSE 0x5F (AVEC CALIBRAGE)")
        print(f"{'='*55}")
        print("📋 SERVOS DISPONIBLES:")
        for channel, config in self.servo_configs.items():
            pos = self.current_positions[channel]
            offset = config["offset"]
            print(f"  {channel:2d}: {config['name']:<15} | Pos: {pos:+4.0f}° "
                  f"| Offset: {offset:+3d}° | Limites: {config['min_angle']:+3d}° à {config['max_angle']:+3d}°")
        
        print(f"\n{'='*55}")
        print("⌨️  COMMANDES:")
        print("  <canal> <angle>    → Déplacer servo (ex: 0 30)")
        print("  center             → Tous les servos à 0° logique")
        print("  status             → Afficher positions")
        print("  test <canal>       → Test d'un servo (ex: test 15)")
        print("  test_all           → Test de tous les servos")
        print("  calibrate <canal>  → Calibrer un servo (ex: calibrate 0)")
        print("  help               → Afficher cette aide")
        print("  quit               → Quitter")
        print(f"{'='*55}")
        print("💡 CONSEILS:")
        print("  - Les angles sont LOGIQUES (0° = centre mécanique)")
        print("  - Si un servo n'est pas centré, utilisez 'calibrate'")
        print("  - L'offset de calibrage est automatiquement appliqué")
        print(f"{'='*55}")
    
    def test_all_servos(self):
        """Test de tous les servos avec confirmation"""
        print(f"\n🧪 TEST DE TOUS LES SERVOS")
        print("⚠️  ATTENTION: Tous les servos du robot vont bouger!")
        print("   Assurez-vous que le robot est en sécurité")
        
        response = input("\nContinuer le test? (y/N): ").strip().lower()
        if response not in ['y', 'yes', 'oui']:
            print("❌ Test annulé")
            return
        
        print("\n🚀 Début du test complet...")
        
        # Test du servo libre en premier (sécurité)
        if 15 in self.servo_configs:
            print("\n1️⃣  Test du servo libre (CH15) - SÉCURITÉ")
            self.test_servo(15)
            time.sleep(1)
        
        # Test des servos du robot
        servo_order = [0, 1, 2]  # Direction, puis tête
        for i, channel in enumerate(servo_order, 2):
            if channel in self.servo_configs:
                print(f"\n{i}️⃣  Test du servo {channel}")
                self.test_servo(channel)
                time.sleep(1)
        
        print("\n✅ Test de tous les servos terminé")
        self.move_to_center()

def main():
    """Programme principal"""
    print("="*55)
    print("🚀 DÉMARRAGE CONTRÔLEUR SERVO")
    print("   Adresse PCA9685: 0x5F")
    print("   AVEC SYSTÈME DE CALIBRAGE")
    print("="*55)
    
    try:
        # Initialisation
        controller = ServoController()
        controller.get_help()
        
        # Boucle principale
        while True:
            try:
                command = input("\n🎮 Commande: ").strip().lower()
                
                if command in ['quit', 'exit', 'q']:
                    print("👋 Au revoir!")
                    break
                
                elif command == 'help':
                    controller.get_help()
                
                elif command == 'status':
                    controller.show_status()
                
                elif command == 'center':
                    controller.move_to_center()
                
                elif command == 'test_all':
                    controller.test_all_servos()
                
                elif command.startswith('test '):
                    try:
                        channel = int(command.split()[1])
                        controller.test_servo(channel)
                    except (ValueError, IndexError):
                        print("❌ Usage: test <canal> (ex: test 15)")
                
                elif command.startswith('calibrate '):
                    try:
                        channel = int(command.split()[1])
                        controller.calibrate_servo(channel)
                    except (ValueError, IndexError):
                        print("❌ Usage: calibrate <canal> (ex: calibrate 0)")
                
                elif ' ' in command:
                    try:
                        parts = command.split()
                        if len(parts) == 2:
                            channel = int(parts[0])
                            angle = float(parts[1])
                            controller.set_angle(channel, angle)
                        else:
                            print("❌ Format: <canal> <angle>")
                    except ValueError:
                        print("❌ Valeurs numériques attendues")
                
                else:
                    print("❌ Commande non reconnue. Tapez 'help' pour l'aide.")
            
            except KeyboardInterrupt:
                print("\n⏸️  Interruption détectée...")
                break
    
    except Exception as e:
        print(f"💥 Erreur fatale: {e}")
    
    finally:
        try:
            controller.move_to_center()
            print("🔒 Servos remis en position de sécurité")
        except:
            pass
        print("🏁 Programme terminé")

if __name__ == "__main__":
    main()
