"""
Genera un dataset SINTÉTICO de métricas operacionales para los experimentos
de detección de anomalías (IsolationForest y One-Class SVM).

IMPORTANTE: Este dataset es un STAND-IN reproducible para desarrollar y validar
el pipeline. Cuando los docentes provean el dataset real, basta con reemplazar
el CSV en notebooks/data/ y apuntar la celda de carga de cada notebook a él.

Las features imitan métricas típicas de un microservicio bajo observación:
  - cpu_usage          (fracción 0..1)
  - memory_usage       (fracción 0..1)
  - request_latency_ms (ms)
  - error_rate         (fracción 0..1)
  - request_rate       (req/s)
  - network_io_mbps    (MB/s)

La columna `is_anomaly` (0=normal, 1=anomalía) se usa SOLO para evaluar los
modelos al final; el entrenamiento es NO supervisado (no la usa).
"""
import numpy as np
import pandas as pd

RANDOM_STATE = 42
N_NORMAL = 1900
N_ANOMALY = 100  # ~5% de contaminación


def generate(seed: int = RANDOM_STATE) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # --- Operación normal: correlaciones realistas alrededor de un punto de trabajo ---
    cpu = rng.normal(0.35, 0.08, N_NORMAL).clip(0.02, 0.95)
    memory = (0.40 + 0.5 * cpu + rng.normal(0, 0.05, N_NORMAL)).clip(0.05, 0.95)
    request_rate = rng.normal(120, 25, N_NORMAL).clip(5, None)
    # latencia crece levemente con cpu y carga
    latency = (40 + 60 * cpu + 0.1 * request_rate + rng.normal(0, 8, N_NORMAL)).clip(5, None)
    error_rate = rng.normal(0.01, 0.005, N_NORMAL).clip(0, 0.1)
    network = (request_rate * 0.02 + rng.normal(0, 0.3, N_NORMAL)).clip(0.05, None)

    normal = pd.DataFrame({
        "cpu_usage": cpu,
        "memory_usage": memory,
        "request_latency_ms": latency,
        "error_rate": error_rate,
        "request_rate": request_rate,
        "network_io_mbps": network,
        "is_anomaly": 0,
    })

    # --- Anomalías: spikes que rompen las correlaciones normales ---
    cpu_a = rng.uniform(0.85, 1.0, N_ANOMALY)
    memory_a = rng.uniform(0.85, 1.0, N_ANOMALY)
    # latencia y errores disparados (incidente)
    latency_a = rng.uniform(800, 4000, N_ANOMALY)
    error_a = rng.uniform(0.15, 0.8, N_ANOMALY)
    # request_rate puede colapsar (caída) o dispararse (tormenta)
    request_a = np.where(
        rng.random(N_ANOMALY) < 0.5,
        rng.uniform(0, 10, N_ANOMALY),       # colapso de tráfico
        rng.uniform(400, 900, N_ANOMALY),    # tormenta de requests
    )
    network_a = rng.uniform(0, 0.1, N_ANOMALY)  # red interrumpida

    anomaly = pd.DataFrame({
        "cpu_usage": cpu_a,
        "memory_usage": memory_a,
        "request_latency_ms": latency_a,
        "error_rate": error_a,
        "request_rate": request_a,
        "network_io_mbps": network_a,
        "is_anomaly": 1,
    })

    df = pd.concat([normal, anomaly], ignore_index=True)
    # mezclar filas
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate()
    out = "data/operational_metrics_sample.csv"
    df.to_csv(out, index=False)
    print(f"Dataset generado: {out}")
    print(f"  Filas: {len(df)}  |  Anomalías: {int(df.is_anomaly.sum())} ({df.is_anomaly.mean()*100:.1f}%)")
    print(df.describe().round(3).to_string())
