#!/usr/bin/env python3
"""
MasterCamp Robotique - Tâche 2 : LED WS2812
Utilise Lesson 10 How to Control WS2812 LED.pdf fourni par Adeept

But : Fournir un module logiciel qui permet de piloter à la couleur demandée 
      la LED demandée, ou l'éteindre, parmi les 2 + 4x3 = 14 LED.

Configuration des LED WS2812 :
- 2 LED sur la carte Robot HAT V3.1 (indices 0 et 1)
- 4 modules WS2812 externes avec 3 LED chacun (indices 2 à 13)
- Total : 14 LED WS2812
"""

import spidev
import time
import numpy

class WS2812Controller:
    """
    Contrôleur pour les LED WS2812 basé sur le code Adeept
    """
    
    def __init__(self, count=14, brightness=255, sequence='GRB', bus=0, device=0):
        """
        Initialise le contrôleur WS2812
        
        Args:
            count (int): Nombre total de LED (2 + 4*3 = 14)
            brightness (int): Luminosité globale (0-255)
            sequence (str): Ordre des couleurs ('GRB' par défaut)
            bus (int): Bus SPI (0 par défaut)
            device (int): Device SPI (0 par défaut)
        """
        self.led_count = count
        self.led_brightness = brightness
        self.set_led_type(sequence)
        self.led_color = [0, 0, 0] * self.led_count
        self.led_original_color = [0, 0, 0] * self.led_count
        
        # Initialisation SPI
        self.bus = bus
        self.device = device
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(self.bus, self.device)
            self.spi.mode = 0
            self.led_init_state = 1
            print("✅ SPI initialisé avec succès")
        except OSError:
            print("❌ Erreur SPI - Vérifiez la configuration dans /boot/firmware/config.txt")
            print("Vous devez activer 'SPI' dans 'Interface Options' avec 'sudo raspi-config'")
            self.led_init_state = 0
        
        # Éteindre toutes les LED au démarrage
        self.set_all_led_color(0, 0, 0)
    
    def set_led_type(self, rgb_type):
        """Configure l'ordre des couleurs RGB"""
        try:
            led_type = ['RGB', 'RBG', 'GRB', 'GBR', 'BRG', 'BGR']
            led_type_offset = [0x06, 0x09, 0x12, 0x21, 0x18, 0x24]
            index = led_type.index(rgb_type)
            self.led_red_offset = (led_type_offset[index] >> 4) & 0x03
            self.led_green_offset = (led_type_offset[index] >> 2) & 0x03
            self.led_blue_offset = (led_type_offset[index] >> 0) & 0x03
            return index
        except ValueError:
            self.led_red_offset = 1
            self.led_green_offset = 0
            self.led_blue_offset = 2
            return -1
    
    def set_ledpixel(self, index, r, g, b):
        """Configure une LED individuelle avec les valeurs RGB"""
        if index >= self.led_count:
            print(f"❌ Index {index} invalide (max: {self.led_count-1})")
            return
        
        p = [0, 0, 0]
        p[self.led_red_offset] = round(r * self.led_brightness / 255)
        p[self.led_green_offset] = round(g * self.led_brightness / 255)
        p[self.led_blue_offset] = round(b * self.led_brightness / 255)
        
        self.led_original_color[index*3 + self.led_red_offset] = r
        self.led_original_color[index*3 + self.led_green_offset] = g
        self.led_original_color[index*3 + self.led_blue_offset] = b
        
        for i in range(3):
            self.led_color[index*3 + i] = p[i]
    
    def get_led_position_name(self, led_num):
        """Retourne le nom de la position de la LED"""
        positions = {
            0: "Carte-1", 1: "Carte-2",
            2: "Bas_Gauche-1", 3: "Bas_Gauche-2", 4: "Bas_Gauche-3",
            5: "Bas_Droite-1", 6: "Bas_Droite-2", 7: "Bas_Droite-3", 
            8: "Arriere_Gauche-1", 9: "Arriere_Gauche-2", 10: "Arriere_Gauche-3",
            11: "Arriere_Droite-1", 12: "Arriere_Droite-2", 13: "Arriere_Droite-3"
        }
        return positions.get(led_num, f"LED-{led_num}")
    
    def control_led(self, led_identifier, color, intensity=255):
        """
        Fonction principale pour contrôler une LED ou un groupe (Partie 1 de la tâche)
        
        Args:
            led_identifier (int/str): Numéro LED (0-13) ou nom groupe ('C', 'BG', 'BD', 'AG', 'AD')
            color (str): Couleur ('R', 'G', 'B', 'N')
            intensity (int): Intensité (0-255) - Partie 3 de la tâche
        """
        # Conversion des identifiants en numéros de LED
        led_nums = self._parse_led_identifier(led_identifier)
        
        # Si c'est un seul numéro (LED individuelle)
        if isinstance(led_nums, int):
            if led_nums is None or led_nums < 0 or led_nums >= self.led_count:
                print(f"❌ LED '{led_identifier}' invalide")
                return
            led_list = [led_nums]
        # Si c'est une liste (groupe de LED)
        elif isinstance(led_nums, list):
            led_list = led_nums
        else:
            print(f"❌ Identifiant '{led_identifier}' invalide")
            return
        
        # Définition des couleurs de base
        colors = {
            'R': (intensity, 0, 0),        # Rouge
            'G': (0, intensity, 0),        # Vert
            'B': (0, 0, intensity),        # Bleu
            'N': (0, 0, 0)                 # Éteinte
        }
        
        if color.upper() not in colors:
            print(f"❌ Couleur '{color}' invalide. Utilisez: R, G, B, N")
            return
        
        r, g, b = colors[color.upper()]
        
        # Allumer toutes les LED du groupe ou la LED individuelle
        for led_num in led_list:
            self.set_ledpixel(led_num, r, g, b)
        
        self.show()
        
        color_name = {'R': 'Rouge', 'G': 'Vert', 'B': 'Bleu', 'N': 'Éteinte'}
        
        # Affichage selon le type (individuel ou groupe)
        if len(led_list) == 1:
            position_name = self.get_led_position_name(led_list[0])
            print(f"🎯 {position_name}: {color_name[color.upper()]} (intensité: {intensity})")
        else:
            group_names = {
                'C': 'Carte', 'BG': 'Bas_Gauche', 'BD': 'Bas_Droite',
                'AG': 'Arriere_Gauche', 'AD': 'Arriere_Droite'
            }
            group_name = group_names.get(str(led_identifier).upper(), str(led_identifier))
            print(f"🎯 Groupe {group_name} (LED {led_list[0]}-{led_list[-1]}): {color_name[color.upper()]} (intensité: {intensity})")
    
    def _parse_led_identifier(self, identifier):
        """Parse l'identifiant LED (numéro ou nom de groupe)"""
        # Si c'est déjà un numéro
        if isinstance(identifier, int):
            return identifier
        
        # Si c'est une chaîne qui représente un numéro
        if isinstance(identifier, str) and identifier.isdigit():
            return int(identifier)
        
        # Pour les groupes, on retourne une liste des LED du groupe
        group_mapping = {
            'C': [0, 1],                    # Carte
            'CARTE': [0, 1],
            'BG': [2, 3, 4],               # Bas Gauche
            'BAS_GAUCHE': [2, 3, 4],
            'BD': [5, 6, 7],               # Bas Droite
            'BAS_DROITE': [5, 6, 7],
            'AG': [8, 9, 10],              # Arrière Gauche
            'ARRIERE_GAUCHE': [8, 9, 10],
            'AD': [11, 12, 13],            # Arrière Droite
            'ARRIERE_DROITE': [11, 12, 13]
        }
        
        # Retourne la liste des LED du groupe ou None
        return group_mapping.get(identifier.upper(), None)
    
    def set_all_led_color(self, r, g, b):
        """Allume toutes les LED avec la même couleur"""
        for i in range(self.led_count):
            self.set_ledpixel(i, r, g, b)
        self.show()
    
    def show(self):
        """Envoie les données aux LED via SPI"""
        if self.led_init_state == 0:
            print("❌ SPI non initialisé")
            return
        
        # Conversion des données LED en signaux SPI
        d = numpy.array(self.led_color).ravel()
        tx = numpy.zeros(len(d)*8, dtype=numpy.uint8)
        
        for ibit in range(8):
            tx[7-ibit::8] = ((d >> ibit) & 1) * 0x78 + 0x80
        
        if self.bus == 0:
            self.spi.xfer(tx.tolist(), int(8/1.25e-6))
        else:
            self.spi.xfer(tx.tolist(), int(8/1.0e-6))
    
    def control_group(self, group_name, color, intensity=255):
        """
        Contrôle un groupe entier de LED
        
        Args:
            group_name (str): Nom du groupe ('C', 'BG', 'BD', 'AG', 'AD')
            color (str): Couleur ('R', 'G', 'B', 'N')
            intensity (int): Intensité (0-255)
        """
        group_mapping = {
            'C': [0, 1],                    # Carte
            'CARTE': [0, 1],
            'BG': [2, 3, 4],               # Bas Gauche
            'BAS_GAUCHE': [2, 3, 4],
            'BD': [5, 6, 7],               # Bas Droite
            'BAS_DROITE': [5, 6, 7],
            'AG': [8, 9, 10],              # Arrière Gauche
            'ARRIERE_GAUCHE': [8, 9, 10],
            'AD': [11, 12, 13],            # Arrière Droite
            'ARRIERE_DROITE': [11, 12, 13]
        }
        
        group_name_upper = group_name.upper()
        if group_name_upper not in group_mapping:
            print(f"❌ Groupe '{group_name}' invalide. Utilisez: C, BG, BD, AG, AD")
            return
        
        leds = group_mapping[group_name_upper]
        for led_num in leds:
            self.control_led(led_num, color, intensity)
        
        group_names = {
            'C': 'Carte', 'BG': 'Bas_Gauche', 'BD': 'Bas_Droite',
            'AG': 'Arriere_Gauche', 'AD': 'Arriere_Droite'
        }
        color_name = {'R': 'Rouge', 'G': 'Vert', 'B': 'Bleu', 'N': 'Éteinte'}
        print(f"🎯 Groupe {group_names.get(group_name_upper, group_name)}: {color_name[color.upper()]}")
        
        """Test de toutes les LED avec différentes couleurs"""
        print("🔄 Test de toutes les LED...")
        colors = [('R', 255, 0, 0), ('G', 0, 255, 0), ('B', 0, 0, 255)]
        
        for color_name, r, g, b in colors:
            print(f"  Test couleur {color_name}")
            for i in range(self.led_count):
                self.set_ledpixel(i, r, g, b)
                self.show()
                time.sleep(0.1)
            time.sleep(0.5)
        
        # Éteindre toutes les LED
        self.set_all_led_color(0, 0, 0)
        print("✅ Test terminé")
    
    def close(self):
        """Ferme la connexion SPI et éteint les LED"""
        self.set_all_led_color(0, 0, 0)
        if hasattr(self, 'spi'):
            self.spi.close()
        print("🔌 Connexion SPI fermée")

def manual_control():
    """
    Protocole manuel pour piloter les LED (Partie 2 de la tâche)
    
    Commandes acceptées:
    - Format: led_num,color,intensity
    - Exemple: 5,R,128 (LED 5 en rouge à intensité 128)
    - Commandes spéciales: 'test', 'exit', 'off'
    """
    controller = WS2812Controller()
    
    if controller.led_init_state == 0:
        print("❌ Impossible de démarrer - SPI non disponible")
        return
    
    print("\n" + "="*60)
    print("🎮 CONTRÔLE MANUEL DES LED WS2812")
    print("="*60)
    print("📋 Configuration: 14 LED WS2812 (2 sur carte + 4 modules de 3)")
    print("\n📝 Commandes disponibles:")
    print("  • led_num,color,intensity     - Contrôler une LED par numéro")
    print("    Exemple: 5,R,128 (LED 5 en rouge à intensité 128)")
    print("  • groupe,color,intensity      - Contrôler TOUT un groupe")
    print("    Exemple: AD,R,200 (TOUTES les LED Arriere_Droite en rouge)")
    print("    Exemple: BG,G,150 (TOUTES les LED Bas_Gauche en vert)")
    print("  • test                        - Tester toutes les LED")
    print("  • off                         - Éteindre toutes les LED")
    print("  • exit                        - Quitter le programme")
    print("\n🎨 Couleurs: R (Rouge), G (Vert), B (Bleu), N (Éteinte)")
    print("💡 Intensité: 0-255")
    print("🔢 LED par numéro: 0-13")
    print("📍 Groupes: C/Carte(0,1), BG/Bas_Gauche(2,3,4), BD/Bas_Droite(5,6,7)")
    print("           AG/Arriere_Gauche(8,9,10), AD/Arriere_Droite(11,12,13)")
    print("="*60)
    
    try:
        while True:
            command = input("\n🎯 Commande > ").strip()
            
            if command.lower() == 'exit':
                break
            elif command.lower() == 'test':
                controller.test_all_leds()
            elif command.lower() == 'off':
                controller.set_all_led_color(0, 0, 0)
                print("💤 Toutes les LED éteintes")
            elif ',' in command:
                try:
                    parts = command.split(',')
                    if len(parts) == 2:
                        # Format: led_num/groupe,color (intensité par défaut 255)
                        led_identifier, color = parts
                        controller.control_led(led_identifier, color, 255)
                    elif len(parts) == 3:
                        # Format: led_num/groupe,color,intensity
                        led_identifier, color, intensity = parts
                        controller.control_led(led_identifier, color, int(intensity))
                    else:
                        print("❌ Format invalide. Utilisez: led_num/groupe,color,intensity")
                except ValueError as e:
                    print(f"❌ Erreur dans la commande: {e}")
            else:
                print("❌ Commande non reconnue")
                print("💡 Aide: utilisez 'led_num,color,intensity' ou 'groupe,color,intensity' ou 'test' ou 'exit'")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt du programme (Ctrl+C)")
    
    finally:
        controller.close()

def demo_sequence():
    """Démonstration des fonctionnalités des LED WS2812"""
    controller = WS2812Controller()
    
    if controller.led_init_state == 0:
        print("❌ Démonstration impossible - SPI non disponible")
        return
    
    print("\n🎭 DÉMONSTRATION LED WS2812")
    print("="*40)
    
    try:
        # Test 1: Allumage séquentiel
        print("🔄 Test 1: Allumage séquentiel...")
        for i in range(controller.led_count):
            controller.control_led(i, 'R', 100)
            time.sleep(0.2)
        time.sleep(1)
        
        # Test 2: Couleurs par position
        print("🔄 Test 2: Couleurs par position...")
        positions = [('C', 'R'), ('BG', 'G'), ('BD', 'B'), ('AG', 'R'), ('AD', 'G')]
        for position, color in positions:
            controller.control_group(position, color, 150)
            time.sleep(0.8)
        time.sleep(1)
        
        # Test 3: Variation d'intensité
        print("🔄 Test 3: Variation d'intensité...")
        for intensity in range(0, 256, 25):
            controller.control_led(7, 'B', intensity)  # LED centrale
            time.sleep(0.2)
        
        # Test 4: Extinction progressive
        print("🔄 Test 4: Extinction progressive...")
        for i in range(controller.led_count):
            controller.control_led(i, 'N', 0)
            time.sleep(0.1)
        
        print("✅ Démonstration terminée")
    
    except KeyboardInterrupt:
        print("\n⏹️  Démonstration interrompue")
    
    finally:
        controller.close()

if __name__ == "__main__":
    print("🤖 MasterCamp Robotique - Tâche 2: LED WS2812")
    print("📚 Basé sur Lesson 10 How to Control WS2812 LED")
    
    while True:
        print("\n" + "="*50)
        print("🎯 MENU PRINCIPAL")
        print("="*50)
        print("1. 🎮 Contrôle manuel des LED")
        print("2. 🎭 Démonstration automatique")  
        print("3. ❌ Quitter")
        print("="*50)
        
        choice = input("Votre choix (1-3): ").strip()
        
        if choice == '1':
            manual_control()
        elif choice == '2':
            demo_sequence()
        elif choice == '3':
            print("👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide, veuillez sélectionner 1, 2 ou 3")