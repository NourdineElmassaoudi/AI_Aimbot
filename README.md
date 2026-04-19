Project Overview
Hada wa7ed l-moussa3id d l-aim (Aimbot) kheddam b-l-AI, moussami3 bach i-detecti l-enemies f l-al3ab b-wa7ed l-mantiq d l-Hardware-level bypass. L-hadaf l-asassi mnnu houwa l-ba7t f moustawa s-sor3a d l-Inference AI o kifach n-commander l-mouse b-tariqa "Human-like" (machi robotic) bach l-anti-cheats ma-i-3iyquch.

Core Architecture (Modules)
L-project m-qassem l-ajza2 m-frouqa (Modular Design) bach i-koun optimized s7i7:

High-Speed Screen Capture (screen_capture.py): Kiy-jbed s-sowar mn l-xaxa b-wa7ed l-sor3a khayaliya (ROI 400x400) kadd-wsal l-aktar mn 200 FPS f l-al3ab.

Neural Network Inference (detector.py): Kiy-khdem b-l-model YOLOv8 (You Only Look Once) bach i-identifiyi l-"person" targets f l-waqt l-7aqiqi o i-7seb l-messafa binn l-center d l-xaxa o l-viktima (dx, dy).

Asynchronous Mouse Controller (mouse_controller.py): Hada houwa l-moukh d l-automation. Kiy-khdem b-wa7ed l-background thread (Threaded) bach ma-i-tqelch l-AI detection. Kiy-sta3mel:

Humanized Smoothing: Kiy-qsem l-7araka l-khoutouat sghira.

Random Jitter: Kiy-zid "Nchf" (Jitter) sghir bach l-7araka t-ban b7al d bnadm.

FOV Constraint: Ma-kiy-t-7errek l-aim ghir ila kan l-enemy wast wa7ed l-daira (FOV) m-7edd-da.

Visual Debugger (debug.py): Window kadd-biyyen l-khedma d l-AI f l-waqt l-7aqiqi m3a bounding boxes khadrin o daira d l-FOV.

Technical Stack
Language: Python

AI Model: YOLOv8 (Ultralytics)

Libraries: OpenCV, MSS (for fast capture), PyWin32 (low-level input)

Hardware Compatibility: Designed for Digispark ATtiny85 for physical hardware bypass.

Educational Goals
Hada project d-pentesting o automation kiy-biyyen:

Kifach n-optimiziw l-models d l-AI bach i-khdmou f low-spec hardware (i5 4th Gen / NVIDIA Quadro).

Kifach t-dar l-communication binn l-Python o l-Hardware (Digispark).

L-dirassa d l-vulnerabilities f s-systems d l-Anti-cheat.
