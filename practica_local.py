"""Generación y perfilamiento LOCAL de los datasets de la guía.

No requiere AWS, boto3, credenciales ni acceso a Internet para ejecutarse
una vez instalado pandas. No representa una ejecución en Amazon S3.

Pasos: python practica_local.py generar
       python practica_local.py csv
       python practica_local.py json
"""
import argparse
from datetime import datetime, timedelta
import io
import json
from pathlib import Path
import random
import sys

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / 'raw'
CSV_PATH = RAW_DIR / 'transacciones.csv'
JSON_PATH = RAW_DIR / 'logs_m2m.json'


def generar_transacciones(num_registros=500):
    """Genera el esquema y distribuciones indicados en la guía del docente."""
    rng = random.Random(42)
    inicio = datetime.now().replace(microsecond=0) - timedelta(days=30)
    metodos = ['Tarjeta de Crédito', 'Tarjeta de Débito', 'Transferencia', 'Efectivo']
    estados = ['Aprobada', 'Aprobada', 'Aprobada', 'Rechazada', 'Pendiente']
    ciudades = ['CDMX', 'Guadalajara', 'Monterrey', 'Puebla', 'Querétaro']
    datos = []
    for i in range(1, num_registros + 1):
        datos.append({
            'id_transaccion': f'TXN-{100000 + i}',
            'id_usuario': f'USR-{rng.randint(1001, 1200)}',
            'fecha': (inicio + timedelta(minutes=rng.randint(0, 30*24*60))).strftime('%Y-%m-%d %H:%M:%S'),
            'monto': round(rng.uniform(10.5, 2500.0), 2),
            'metodo_pago': rng.choice(metodos),
            'estado': rng.choice(estados),
            'ciudad': rng.choice(ciudades),
        })
    return pd.DataFrame(datos)


def generar_logs(num_registros=300):
    """Genera logs M2M con metrics anidado, igual que en la guía."""
    rng = random.Random(101)
    niveles = ['INFO', 'WARNING', 'ERROR', 'SUCCESS']
    eventos = ['DEVICE_HEARTBEAT', 'DATA_SYNC', 'CONNECTION_FAILED', 'FIRMWARE_UPDATE', 'SENSOR_READ']
    dispositivos = [f'DEV-M2M-{i:03d}' for i in range(1, 21)]
    inicio = datetime.now().replace(microsecond=0) - timedelta(days=7)
    logs = []
    for i in range(1, num_registros + 1):
        timestamp = inicio + timedelta(seconds=rng.randint(0, 7*24*3600))
        logs.append({
            'log_id': f'LOG-{10000 + i}',
            'timestamp': timestamp.isoformat(),
            'device_id': rng.choice(dispositivos),
            'ip_address': f'192.168.1.{rng.randint(10, 250)}',
            'level': rng.choice(niveles),
            'event': rng.choice(eventos),
            'metrics': {
                'cpu_usage_pct': round(rng.uniform(5.0, 99.0), 2),
                'latency_ms': rng.randint(10, 450),
                'bytes_sent': rng.randint(128, 65536),
            },
        })
    return logs


def guardar_datasets():
    """Crea los datos en raw/. Solo sustituye archivos de esta práctica."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df = generar_transacciones()
    logs = generar_logs()
    df.to_csv(CSV_PATH, index=False, encoding='utf-8')
    JSON_PATH.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding='utf-8')
    print('PRÁCTICA 1 | GENERACIÓN LOCAL DE DATOS')
    print(f'CSV:  raw/transacciones.csv | {len(df)} filas x {len(df.columns)} columnas')
    print(f'JSON: raw/logs_m2m.json     | {len(logs)} registros')
    print('Semillas: 42 para transacciones y 101 para logs.')
    print('\nARCHIVOS GENERADOS')
    for path in [CSV_PATH, JSON_PATH]:
        print(f'  {path.relative_to(BASE_DIR)} | {path.stat().st_size:,} bytes')
    print('\nGeneración completada correctamente.')


def cargar_y_perfilar_local(path, is_json=False):
    """Lee bytes del archivo local y analiza el DataFrame en memoria.

    Conserva io.BytesIO para el CSV y json_normalize para el JSON.
    La obtención de bytes procede del disco local, no de un bucket de S3.
    """
    body = path.read_bytes()
    if is_json:
        df = pd.json_normalize(json.loads(body.decode('utf-8-sig')))
    else:
        df = pd.read_csv(io.BytesIO(body))
    print(f'PRÁCTICA 1 | PERFILAMIENTO LOCAL {"JSON" if is_json else "CSV"}')
    print(f'Archivo: {path.relative_to(BASE_DIR)}')
    print(f'Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas')
    print('\nTIPOS DE DATOS')
    print(df.dtypes.to_string())
    print('\nVALORES NULOS POR COLUMNA')
    print(df.isna().sum().to_string())
    print('\nESTADÍSTICAS DESCRIPTIVAS NUMÉRICAS')
    numericas = df.select_dtypes(include='number')
    if numericas.empty:
        print('No hay columnas numéricas con registros para resumir.')
    else:
        print(numericas.describe().T.to_string(float_format=lambda x: f'{x:.4f}'))
    print('\nPRIMEROS 5 REGISTROS')
    print(df.head().to_string(index=False))
    print('\nPerfilamiento completado correctamente.')
    return df


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paso', choices=['generar', 'csv', 'json', 'todo'],
                        help='generar crea ambos archivos; csv/json muestran cada perfil')
    args = parser.parse_args(argv)
    try:
        if args.paso in ('generar', 'todo'):
            guardar_datasets()
        if args.paso in ('csv', 'todo'):
            cargar_y_perfilar_local(CSV_PATH)
        if args.paso in ('json', 'todo'):
            cargar_y_perfilar_local(JSON_PATH, is_json=True)
    except FileNotFoundError:
        print('Faltan los archivos de datos. Ejecuta primero: python practica_local.py generar', file=sys.stderr)
        return 1
    except (OSError, ValueError, UnicodeDecodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
        print(f'No se pudo procesar el archivo: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
