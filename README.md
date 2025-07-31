# JCVD
# Mise en situation
Dans le cadre du MasterCamp de 3ᵉ année en « Systèmes embarqués » à l’EFREI, j’ai participé au développement du robot JCVD : un robot autonome capable de se déplacer, de percevoir son environnement et d’interagir avec ce dernier.
# Mécanique et électronique
- Châssis : assemblage de la structure de base du robot  
- Moteur DC : marche avant et marche arrière du robot  
- 3 servomoteurs :  
  - 1 pour l’orientation des roues  
  - 1 pour l’axe de rotation de la tête  
  - 1 pour l’axe du capteur ultrason
- Capteur ultrason : détection d’obstacles frontaux  
- Capteur de luminosité : adaptation aux conditions d’éclairage  
- Caméra : perception visuelle avancée  
- LEDs infrarouges (IR) : détection de ligne au sol  
- LEDs RGB avant : affichage de la couleur de l'obstacle à l'aide de la caméra
- LEDs WS2812 : design du robot   
- Câblage & intégration : optimisation de la disposition pour un bon fonctionnement global
# Fonctionnalités
- Pilotage des moteurs avec gestion progressive de l’accélération et de la décélération  
- Contrôle précis des servomoteurs pour les différents axes  
- Gestion des LEDs RGB classiques et adressables (WS2812)  
- Capture vidéo en temps réel via la caméra embarquée  
- Détection et suivi de ligne via capteurs infrarouges  
- Reconnaissance des couleurs et des formes  
- Identification et suivi de flèches directionnelles  
