# Detección de anomalías — Objetivo 5

Dos experimentos no supervisados de detección de anomalías sobre métricas
operacionales, según la rúbrica del obligatorio AIOps.

## Contenido

| Archivo | Descripción |
|---------|-------------|
| `isolation_forest.ipynb` | Experimento con **Isolation Forest** (sklearn) |
| `svm_anomaly_detection.ipynb` | Experimento con **One-Class SVM** (sklearn) |
| `generate_sample_dataset.py` | Genera el dataset sintético reproducible |
| `build_notebooks.py` | Reconstruye ambos notebooks desde código |
| `data/operational_metrics_sample.csv` | Dataset stand-in (2000 filas, 5% anomalías) |
| `requirements.txt` | Dependencias Python |

## Cómo correrlos

```bash
cd notebooks
python3 -m pip install -r requirements.txt
python3 generate_sample_dataset.py          # genera el CSV (ya incluido)
python3 -m nbconvert --to notebook --execute --inplace isolation_forest.ipynb
python3 -m nbconvert --to notebook --execute --inplace svm_anomaly_detection.ipynb
# o abrirlos con: jupyter notebook
```

## Dataset

Se usa un **dataset sintético reproducible** (`data/operational_metrics_sample.csv`)
que imita métricas de un microservicio: `cpu_usage`, `memory_usage`,
`request_latency_ms`, `error_rate`, `request_rate`, `network_io_mbps`. La columna
`is_anomaly` se usa **sólo para evaluar** (el entrenamiento es no supervisado).

> **Para usar el dataset real de los docentes:** reemplazar el CSV en `data/` (o
> cambiar `DATA_PATH` en la celda 1 de cada notebook) manteniendo las columnas de
> features. El resto del pipeline (EDA → escalado → modelo → evaluación) no cambia.

## Resultados (dataset sintético)

| Modelo | Precision (anom.) | Recall (anom.) | F1 (anom.) | ROC AUC |
|--------|------------------|----------------|-----------|---------|
| Isolation Forest | 1.00 | 1.00 | 1.00 | 1.000 |
| One-Class SVM | 0.72 | 0.73 | 0.73 | 0.981 |

Isolation Forest separa mejor las anomalías inyectadas en este dataset; One-Class
SVM es más sensible a la escala y al hiperparámetro `nu`. Ambos se evalúan con las
mismas métricas para permitir la comparación.
