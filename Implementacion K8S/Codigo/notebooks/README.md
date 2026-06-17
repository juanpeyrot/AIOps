# Detección de anomalías — Isolation Forest y One-Class SVM

Dos experimentos no supervisados de detección de anomalías sobre **datasets reales**, según la
rúbrica del obligatorio AIOps:

> *Deben implementarse los algoritmos IsolationForest y Support Vector Machine para datasets que
> serán provistos por los docentes. Se deben entregar las notebooks de cada experimento y reportar
> los resultados.*

## Contenido

| Archivo | Algoritmo | Dataset |
|---------|-----------|---------|
| `isolation_forest_kpi.ipynb` | **Isolation Forest** (multivariado) | AIOps Challenge 2018 — KPIs (NetManAIOps) |
| `oneclass_svm_kc1.ipynb` | **One-Class SVM** (RBF) | NASA / PROMISE **KC1** (OpenML id 1067) |
| `requirements.txt` | Dependencias Python | — |
| `data/` | Cache de datos descargados (se crea sola) | — |

Los datasets se **descargan por HTTP** la primera vez (GitHub para los KPIs, OpenML para KC1) y
quedan cacheados en `data/`. No se versiona ningún CSV.

## Cómo correrlos

```bash
cd notebooks
python3 -m pip install -r requirements.txt
python3 -m nbconvert --to notebook --execute --inplace isolation_forest_kpi.ipynb
python3 -m nbconvert --to notebook --execute --inplace oneclass_svm_kc1.ipynb
# o abrirlos con: jupyter notebook
```

## Experimento 1 — Isolation Forest sobre KPIs (`isolation_forest_kpi.ipynb`)

Une **4 KPIs** del AIOps Challenge 2018 por `timestamp` (una fila por minuto, ~146k puntos) y
entrena un Isolation Forest multivariado sobre **14 features** (`value`, `diff_1`, `rolling_z` por
KPI + `hour`, `dayofweek`). Incluye comparación de configuraciones (`m`, `contamination`),
visualización de un iTree, contraste con un umbral univariado y barridos de sensibilidad a
`contamination`, `ψ` (max_samples) y `m` (n_estimators).

**Ejercicio del obligatorio (sección 15)** — consigna del docente: *agregar un KPI más, repetir los
experimentos con una feature más, y contar qué pasa*. Resuelto:

- Se **agrega un 5º KPI** elegido del propio `kpi_summary` (el de mayor solape temporal con los 4).
- Las features pasan de **14 → 17** (`5×3 + 2`).
- Se **repiten todos los experimentos** (3 configuraciones + sensibilidad a `contamination`, `ψ`, `m`)
  y se reporta qué cambia: solape del join, número y cuáles anomalías cambian (Jaccard 4-KPI vs
  5-KPI), costo operativo de `contamination` y por qué es necesario escalar.

## Experimento 2 — One-Class SVM sobre KC1 (`oneclass_svm_kc1.ipynb`)

Métricas estáticas de software de NASA **KC1** (21 features: LOC, McCabe `v(g)`, Halstead, etc.;
cada fila es un **módulo**). El OCSVM se entrena **solo con módulos sin defecto** y marca como
atípicos los que se salen de esa región; la etiqueta `defects` se usa **solo para evaluar**. Incluye
matriz de confusión, ranking, frontera RBF en 2D y sensibilidad a `nu` y `gamma`.

**Ejercicio del obligatorio (sección 12)** — consigna del docente: *armar una buena tabla de `nu` y
elegir el mejor; hacer un Isolation Forest con las 21 columnas y comparar qué da mejor, ¿IF o una SVM
tuneada?*. Resuelto:

- **Tabla amplia de `nu`** (`0.02 … 0.30`) con precision / recall / F1 (clase defecto) y ROC-AUC,
  eligiendo el mejor `nu` por F1; más un **grid `nu × gamma`** para tunear la SVM.
- **Isolation Forest sobre las 21 columnas**, evaluado con las mismas métricas.
- **Tabla comparativa final** IF vs mejor OCSVM (precision/recall/F1/ROC-AUC) y conclusión.

## Reporte de resultados

El reporte vive como **celdas markdown dentro de cada notebook** (secciones 15 y 12): explican qué
cambia al agregar el 5º KPI y cuál modelo gana en KC1, junto a las tablas/figuras generadas al
ejecutar. Las cifras concretas se producen al correr los notebooks con los datos reales.
