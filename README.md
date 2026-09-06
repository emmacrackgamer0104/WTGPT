# WTGPT

## War Thunder Intelligence & Analytics

> Herramienta especializada para analizar vehículos, consultar datos y construir lineups coherentes de War Thunder.

### 🚀 Estado actual

WTGPT está en desarrollo y ya cuenta con:

- 🧠 Motor de recomendación de lineups en Python.
- 🔎 Análisis de vehículos.
- 🧩 Selección de lineups por vehículo, nación y BR.
- 🗃️ Base de datos en `vehicles.json`.
- 🌐 Interfaz web HUD en `index.html`.
- 🤝 Sistema preparado para contribuciones de la comunidad.

### 🌐 Interfaz web

La web usa `vehicles.json` como fuente de datos y muestra el estado de la base en tiempo real desde el navegador.

La interfaz está preparada para consultas como:

> "Dime un lineup para el Leopard 2A4"

Los vehículos de evento, Pase de Batalla y retirados pueden permanecer en la base de datos aunque ya no estén disponibles para adquisición.

### 🧠 Inteligencia de lineups

El motor no se limita a buscar cinco vehículos del mismo BR. Busca complementar roles y, cuando los datos estén disponibles, puede utilizar:

- Vehículo principal
- Antiaéreo / SPAA
- Antitanque
- Reconocimiento
- Aviación
- Helicópteros
- Diferencias de BR
- Modo de juego

**Regla de fiabilidad:** si un BR no está verificado, WTGPT no lo inventa.

### 🗃️ Datos

Los datos se mantienen separados de la lógica del programa. Esto permite actualizar vehículos sin tener que reescribir el motor.

Los datos desconocidos deben permanecer como `null` hasta ser verificados.

### 🛠️ Tecnología

- Python
- JSON
- HTML
- CSS
- JavaScript

El núcleo de análisis y recomendación permanece en Python; la interfaz web proporciona la capa de presentación.

### 🤝 Contribuir

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para añadir vehículos o corregir información.

### 📌 Visión

Construir una herramienta capaz de mantener, analizar y utilizar datos dinámicos de War Thunder para ofrecer recomendaciones útiles y explicables a sus jugadores.
