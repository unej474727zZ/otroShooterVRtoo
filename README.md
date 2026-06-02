Es un shooter en 3D y Realidad Virtual (VR) en primera persona (CQB) diseñado para Android. El proyecto se basa en gráficos Low Poly y cuenta con soporte nativo para joysticks/mandos Bluetooth (como el modelo X3).

## 🚀 Características Principales

- **Realidad Virtual (VR) y 3D:** El núcleo del juego está desarrollado con tecnologías web (HTML5, **A-Frame**, Three.js) e integrado en una aplicación nativa de Android mediante WebView, lo que facilita gráficos inmersivos.
- **Soporte para Joystick/Mando:** Integración de un puente nativo para comunicar los ejes de los controles directamente desde el sistema Android al juego, resolviendo problemas de compatibilidad con controles genéricos (como el mando X3).
- **Mecánicas de Shooter CQB:**
  - Sistema completo de armamento: Control de munición, cadencia, ráfagas y recarga.
  - Efectos visuales: Destellos de cañón (Muzzle flash), agujeros de bala (Decals) e impactos mediante Raycasting de alta precisión.
  - Diseño de audio: Sonidos espaciales en 3D (pasos, disparos aislados y ráfagas continuas).
- **Inteligencia Artificial (NPCs):** Sistema de oleadas dinámicas. Los enemigos son capaces de rastrear al jugador, moverse hacia él y atacarlo. Su nivel de dificultad visual se ajusta progresivamente.
- **Salud y HUD:** Interfaz para monitorear balas, cuadros por segundo (FPS) y un sistema de "vidas", junto con una pantalla de "Game Over".
- **Físicas:** Utiliza un motor de físicas para garantizar que el jugador y los enemigos no colisionen con los muros o atraviesen el suelo, además de detectar impactos precisos en el cuerpo y la cabeza (hitboxes diferenciados).

## 🛠 Tecnologías Utilizadas

- **Frontend / Motor Gráfico:**
  - [A-Frame (v1.5.0)](https://aframe.io/)
  - THREE.js (incluido con A-Frame)
  - [A-Frame Physics System](https://github.com/c-frame/aframe-physics-system)
  - [A-Frame Extras](https://github.com/c-frame/aframe-extras) (Para Animation Mixer)
- **Backend / Wrapper Nativo:**
  - Android SDK (Java/Kotlin) encapsulando los *assets* locales (`index.html`).
- **Herramientas de desarrollo:**
  - Dependencias en Node.js (glTF-Transform, Puppeteer, Sharp) usadas para la optimización de los modelos 3D y assets del juego.

## 📦 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/unej474727zZ/otroShooterVRtoo.git
   ```
2. **Abrir en Android Studio:**
   - Abre el proyecto en Android Studio.
   - Deja que Gradle sincronice las dependencias.
3. **Construir y Ejecutar:**
   - Conecta un dispositivo Android (preferiblemente con visor VR o para usar con gamepad).
   - Ejecuta la aplicación desde Android Studio o compila el APK mediante la línea de comandos:
     ```bash
     ./gradlew assembleDebug
     ```

## 🎮 Controles (Mando X3 recomendado)
- **Movimiento:** Palanca izquierda.
- **Cámara/Giro:** Palanca derecha (mapeada a través del puente nativo `nativeGamepadAxes` de Android).
- **Disparo:** Gatillos/Botones mapeados según el puente Android-WebXR.

---
*Proyecto en desarrollo iterativo. Optimizado para evitar parpadeos de shaders (Shader Warmup) y caídas de frames en Android.*
