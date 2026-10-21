# Práctica 1 — Ejecución local en Visual Studio Code

Proyecto adaptado a la guía del docente: 500 transacciones CSV y 300 logs M2M JSON.
Este paquete trabaja con archivos locales. No requiere AWS ni credenciales.

## 1. Abrir el proyecto

1. Extrae el ZIP completo.
2. Abre Visual Studio Code.
3. Archivo > Abrir carpeta: selecciona `practica_local_vs`, donde están
   `practica_local.py` y `requirements.txt`.
4. Terminal > Nueva terminal. Los comandos siguientes son para PowerShell en Windows.

## 2. Preparar Python una vez

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si `py` no existe pero `python --version` funciona, crea el entorno con:

```powershell
python -m venv .venv
```

No necesitas activar el entorno ni cambiar la política de PowerShell:
los comandos usan su intérprete directamente.
En VS Code puedes seleccionar `.venv\Scripts\python.exe` con
Ctrl+Shift+P > Python: Select Interpreter, si tienes la extensión Python instalada.

## 3. Generar los archivos

```powershell
.\.venv\Scripts\python.exe practica_local.py generar
```

Se crean `raw/transacciones.csv` (500 filas, 7 columnas) y
`raw/logs_m2m.json` (300 registros). Las semillas mantienen los mismos valores
sintéticos de la guía; las fechas parten del momento de la generación.
Repetir `generar` vuelve a crear ambos archivos de ejemplo.

CAPTURA 1: comando y confirmación de ambos archivos. Deja visible la carpeta
`raw` en el explorador de VS Code si es posible.

## 4. Perfil del CSV

```powershell
.\.venv\Scripts\python.exe practica_local.py csv
```

CAPTURA 2: encabezado, 500 filas x 7 columnas y tipos.
CAPTURA 3: estadísticas de `monto` y primeros registros.
Puedes usar una sola captura si todo resulta legible.

## 5. Perfil del JSON

```powershell
.\.venv\Scripts\python.exe practica_local.py json
```

CAPTURA 4: encabezado, 300 filas x 9 columnas y tipos.
CAPTURA 5: estadísticas de `metrics.cpu_usage_pct`, `metrics.latency_ms`
y `metrics.bytes_sent`, y primeros registros si caben.
Puedes usar una sola captura si todo resulta legible.

Para ampliar la terminal, arrastra su borde superior hacia arriba. Si las tablas
no caben horizontalmente, usa Terminal > Alternar terminal en el área del editor
o reduce un poco el tamaño de letra de la terminal.

## Ubuntu o Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python practica_local.py generar
.venv/bin/python practica_local.py csv
.venv/bin/python practica_local.py json
```

## Qué realiza el programa

- Genera los mismos esquemas y cantidades de la guía.
- Lee los bytes locales y utiliza io.BytesIO para interpretar el CSV.
- Normaliza el JSON anidado mediante pandas.json_normalize.
- Muestra dimensiones, tipos, nulos, estadísticas numéricas y cinco registros.
- Conserva fechas como texto y no sustituye ni elimina valores.

El CSV tiene id_transaccion, id_usuario, fecha, monto, metodo_pago, estado y ciudad.
El JSON normalizado tiene log_id, timestamp, device_id, ip_address, level, event,
metrics.cpu_usage_pct, metrics.latency_ms y metrics.bytes_sent.

La parte de conexión e ingesta desde S3 solicitada por la práctica se completa
posteriormente; estas salidas locales no acreditan acceso a AWS.
