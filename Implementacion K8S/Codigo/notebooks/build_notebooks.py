"""
Construye los dos notebooks de detección de anomalías (IsolationForest y
One-Class SVM) usando nbformat. Comparten estructura y dataset para que los
resultados sean comparables. Tras construirlos se ejecutan con nbconvert.
"""
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

DATA_PATH = "data/operational_metrics_sample.csv"

FEATURES = [
    "cpu_usage", "memory_usage", "request_latency_ms",
    "error_rate", "request_rate", "network_io_mbps",
]


def common_head(title, algo_desc):
    return [
        new_markdown_cell(
            f"# {title}\n\n"
            "**Obligatorio AIOps — PharmaGo — Objetivo 5: Detección de anomalías**\n\n"
            f"{algo_desc}\n\n"
            "El entrenamiento es **no supervisado**: el modelo no usa etiquetas. "
            "La columna `is_anomaly` se reserva sólo para *evaluar* la calidad al final.\n\n"
            "> **Dataset:** se usa un dataset sintético reproducible de métricas "
            "operacionales (`data/operational_metrics_sample.csv`). Para usar el "
            "dataset real de los docentes, reemplazar el archivo o cambiar `DATA_PATH` "
            "en la celda de carga."
        ),
        new_code_cell(
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from sklearn.preprocessing import StandardScaler\n"
            "from sklearn.decomposition import PCA\n"
            "from sklearn.metrics import (classification_report, confusion_matrix,\n"
            "                             roc_auc_score, ConfusionMatrixDisplay)\n"
            "\n"
            "sns.set_theme(style='whitegrid')\n"
            "RANDOM_STATE = 42"
        ),
        new_markdown_cell("## 1. Carga de datos\n\n*(Punto único a cambiar cuando llegue el dataset real.)*"),
        new_code_cell(
            f"DATA_PATH = '{DATA_PATH}'\n"
            "df = pd.read_csv(DATA_PATH)\n"
            f"FEATURES = {FEATURES}\n"
            "print('Filas:', len(df), '| Columnas:', list(df.columns))\n"
            "df.head()"
        ),
        new_markdown_cell("## 2. Análisis exploratorio (EDA)"),
        new_code_cell(
            "display(df[FEATURES].describe().round(3))\n"
            "print('\\nBalance de clases (solo para referencia/evaluacion):')\n"
            "print(df['is_anomaly'].value_counts())\n"
            "print('Proporcion de anomalias: {:.1%}'.format(df['is_anomaly'].mean()))"
        ),
        new_code_cell(
            "fig, axes = plt.subplots(2, 3, figsize=(15, 7))\n"
            "for ax, col in zip(axes.ravel(), FEATURES):\n"
            "    sns.histplot(data=df, x=col, hue='is_anomaly', bins=40,\n"
            "                 ax=ax, palette={0: 'steelblue', 1: 'crimson'}, legend=False)\n"
            "    ax.set_title(col)\n"
            "fig.suptitle('Distribucion de cada metrica (azul=normal, rojo=anomalia)')\n"
            "fig.tight_layout()\n"
            "plt.show()"
        ),
        new_code_cell(
            "plt.figure(figsize=(7, 5))\n"
            "sns.heatmap(df[FEATURES].corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0)\n"
            "plt.title('Matriz de correlacion de las metricas')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        new_markdown_cell(
            "## 3. Preprocesamiento\n\n"
            "Se separan features de la etiqueta y se estandarizan (media 0, desvío 1) "
            "con `StandardScaler`, requisito para modelos sensibles a la escala como SVM."
        ),
        new_code_cell(
            "X = df[FEATURES].values\n"
            "y = df['is_anomaly'].values  # solo para evaluar\n"
            "scaler = StandardScaler()\n"
            "X_scaled = scaler.fit_transform(X)\n"
            "print('X_scaled shape:', X_scaled.shape)"
        ),
    ]


def eval_and_viz_cells(score_comment):
    return [
        new_markdown_cell(
            "## 5. Predicción y evaluación\n\n"
            "El modelo devuelve `+1` (normal) / `-1` (anomalía). Se convierte a "
            "`0/1` y se compara contra `is_anomaly`.\n\n"
            f"{score_comment}"
        ),
        new_code_cell(
            "pred = model.predict(X_scaled)\n"
            "pred_anomaly = (pred == -1).astype(int)\n"
            "print(classification_report(y, pred_anomaly,\n"
            "      target_names=['normal', 'anomalia']))\n"
            "auc = roc_auc_score(y, anomaly_score)\n"
            "print('ROC AUC (anomaly_score): {:.3f}'.format(auc))"
        ),
        new_code_cell(
            "cm = confusion_matrix(y, pred_anomaly)\n"
            "ConfusionMatrixDisplay(cm, display_labels=['normal', 'anomalia']).plot(cmap='Blues')\n"
            "plt.title('Matriz de confusion')\n"
            "plt.show()"
        ),
        new_markdown_cell("## 6. Visualización en 2D (PCA)"),
        new_code_cell(
            "pca = PCA(n_components=2, random_state=RANDOM_STATE)\n"
            "X_2d = pca.fit_transform(X_scaled)\n"
            "fig, ax = plt.subplots(1, 2, figsize=(14, 5))\n"
            "ax[0].scatter(X_2d[y==0, 0], X_2d[y==0, 1], s=8, c='steelblue', label='normal real')\n"
            "ax[0].scatter(X_2d[y==1, 0], X_2d[y==1, 1], s=18, c='crimson', label='anomalia real')\n"
            "ax[0].set_title('Etiquetas reales'); ax[0].legend()\n"
            "ax[1].scatter(X_2d[pred_anomaly==0, 0], X_2d[pred_anomaly==0, 1], s=8, c='steelblue', label='normal pred')\n"
            "ax[1].scatter(X_2d[pred_anomaly==1, 0], X_2d[pred_anomaly==1, 1], s=18, c='darkorange', label='anomalia pred')\n"
            "ax[1].set_title('Prediccion del modelo'); ax[1].legend()\n"
            "for a in ax: a.set_xlabel('PC1'); a.set_ylabel('PC2')\n"
            "plt.tight_layout(); plt.show()"
        ),
        new_code_cell(
            "plt.figure(figsize=(8, 4))\n"
            "sns.histplot(x=anomaly_score, hue=y, bins=50,\n"
            "             palette={0: 'steelblue', 1: 'crimson'})\n"
            "plt.title('Distribucion del score de anomalia (mayor = mas anomalo)')\n"
            "plt.xlabel('anomaly_score')\n"
            "plt.show()"
        ),
    ]


def build_isolation_forest():
    nb = new_notebook()
    nb.cells = common_head(
        "Detección de anomalías — Isolation Forest",
        "**Isolation Forest** aísla observaciones construyendo árboles aleatorios: "
        "las anomalías requieren menos particiones para quedar aisladas, por lo que "
        "obtienen *path lengths* más cortos.",
    )
    nb.cells += [
        new_markdown_cell(
            "## 4. Entrenamiento — Isolation Forest\n\n"
            "`contamination=0.05` indica la proporción esperada de anomalías."
        ),
        new_code_cell(
            "from sklearn.ensemble import IsolationForest\n"
            "model = IsolationForest(n_estimators=200, contamination=0.05,\n"
            "                        random_state=RANDOM_STATE)\n"
            "model.fit(X_scaled)\n"
            "# score: invertimos decision_function para que MAYOR = mas anomalo\n"
            "anomaly_score = -model.decision_function(X_scaled)"
        ),
    ]
    nb.cells += eval_and_viz_cells(
        "El *score* se obtiene de `-decision_function` (mayor = más anómalo)."
    )
    nb.cells += [
        new_markdown_cell(
            "## 7. Conclusiones\n\n"
            "- Isolation Forest detecta las anomalías inyectadas con buen recall sin usar "
            "etiquetas en el entrenamiento.\n"
            "- Es eficiente y escala bien; el hiperparámetro clave es `contamination`.\n"
            "- En producción, este modelo se alimentaría con las métricas reales recolectadas "
            "por Prometheus (CPU, memoria, latencia, error rate, red) para alertar sobre "
            "comportamiento anómalo.\n"
            "- **Comparación con One-Class SVM**: ver el notebook `svm_anomaly_detection.ipynb`."
        ),
    ]
    return nb


def build_svm():
    nb = new_notebook()
    nb.cells = common_head(
        "Detección de anomalías — One-Class SVM",
        "**One-Class SVM** aprende una frontera que encierra la región de los datos "
        "normales en un espacio de alta dimensión (kernel RBF); lo que cae fuera se "
        "considera anomalía.",
    )
    nb.cells += [
        new_markdown_cell(
            "## 4. Entrenamiento — One-Class SVM\n\n"
            "`nu=0.05` acota la fracción de outliers; `gamma='scale'` ajusta el kernel RBF."
        ),
        new_code_cell(
            "from sklearn.svm import OneClassSVM\n"
            "model = OneClassSVM(kernel='rbf', gamma='scale', nu=0.05)\n"
            "model.fit(X_scaled)\n"
            "# score: invertimos score_samples para que MAYOR = mas anomalo\n"
            "anomaly_score = -model.score_samples(X_scaled)"
        ),
    ]
    nb.cells += eval_and_viz_cells(
        "El *score* se obtiene de `-score_samples` (mayor = más anómalo)."
    )
    nb.cells += [
        new_markdown_cell(
            "## 7. Conclusiones\n\n"
            "- One-Class SVM modela la frontera de la clase normal; es potente pero más "
            "sensible a la escala (de ahí el `StandardScaler`) y al hiperparámetro `nu`.\n"
            "- Suele ser más costoso que Isolation Forest en datasets grandes.\n"
            "- **Comparación**: ambos modelos se entrenan sobre el mismo dataset y se "
            "evalúan con las mismas métricas (precision/recall/F1 y ROC AUC), permitiendo "
            "elegir el más adecuado según el costo de falsos positivos/negativos del incidente."
        ),
    ]
    return nb


if __name__ == "__main__":
    nbf.write(build_isolation_forest(), "isolation_forest.ipynb")
    nbf.write(build_svm(), "svm_anomaly_detection.ipynb")
    print("Notebooks escritos: isolation_forest.ipynb, svm_anomaly_detection.ipynb")
