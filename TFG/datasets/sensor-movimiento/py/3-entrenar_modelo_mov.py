import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.tree import export_graphviz
import graphviz
import joblib
import os

# 📂 Ruta del dataset combinado ya preparado
dataset_path = "../csv/dataset_combinado_movimiento.csv"
df = pd.read_csv(dataset_path)

print(f"✅ Dataset cargado: {len(df)} registros")

# 🎯 Definir las features (sin hora) y la etiqueta
X = df[["motion_status", "delta_time"]]
y = df["label"]

# 📊 Dividir en entrenamiento y test (80% entrenamiento, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(f"✅ Entrenamiento: {len(X_train)} registros | Test: {len(X_test)} registros")

# 🌲 Entrenar RandomForest (con limitación de profundidad para evitar sobreajuste)
modelo = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
modelo.fit(X_train, y_train)

# 🔍 Evaluar el modelo
y_pred = modelo.predict(X_test)
print("\n📌 Accuracy del modelo:", accuracy_score(y_test, y_pred))
print("\n📌 Matriz de confusión:\n", confusion_matrix(y_test, y_pred))
print("\n📌 Classification Report:\n", classification_report(y_test, y_pred))

# 💾 Guardar el modelo entrenado
output_model_path = "../modelos/modelo_movimiento.pkl"
joblib.dump(modelo, output_model_path)
print(f"✅ Modelo entrenado y guardado como '{output_model_path}'")

# 🖼️ Generar gráfico del árbol
output_graph_dir = "../graficas/arbol_movimiento"
os.makedirs(output_graph_dir, exist_ok=True)
est = modelo.estimators_[0]
dot = export_graphviz(
    est,
    out_file=None,
    feature_names=["motion_status", "delta_time"],
    class_names=["normal", "attack"],
    filled=True,
    rounded=True,
    special_characters=True
)
graphviz.Source(dot).render(
    os.path.join(output_graph_dir, "arbol_movimiento"), format="png"
)
print(f"✅ Gráfico del árbol guardado en '{output_graph_dir}/arbol_movimiento.png'")
