import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.tree import export_graphviz
import graphviz
import joblib
import os
from datetime import datetime

# 📂 Cargar dataset combinado y limpio
df = pd.read_csv("../csv/dataset_combinado_puerta.csv")

# 🎯 Definir las features y etiquetas
X = df[["door_state_encoded", "hour", "minute", "second", "weekday", "delta_time"]]
y = df["label"]

# 📊 Dividir en entrenamiento y test (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(f"✅ Tamaño del conjunto de entrenamiento: {len(X_train)}")
print(f"✅ Tamaño del conjunto de test: {len(X_test)}")

# 🌲 Entrenar el modelo
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# 🔍 Evaluar
y_pred = modelo.predict(X_test)
print("\n📌 Accuracy del modelo:", accuracy_score(y_test, y_pred))
print("\n📌 Matriz de confusión:")
print(confusion_matrix(y_test, y_pred))
print("\n📌 Classification Report:")
print(classification_report(y_test, y_pred))

# 🟢 Generar gráfico del árbol (primer estimador)
output_graph_dir = "../graficas/arbol_puerta"
os.makedirs(output_graph_dir, exist_ok=True)
estimator = modelo.estimators_[0]
dot_data = export_graphviz(
    estimator,
    out_file=None,
    feature_names=["door_state_encoded", "hour", "minute", "second", "weekday", "delta_time"],
    class_names=["normal", "attack"],
    filled=True,
    rounded=True,
    special_characters=True
)
graphviz.Source(dot_data).render(
    os.path.join(output_graph_dir, "arbol_puerta"),
    format="png"
)
print(f"✅ Gráfico del modelo generado en '{output_graph_dir}/arbol_puerta.png'")

# 💾 Guardar el modelo
joblib.dump(modelo, "../modelos/modelo_puerta.pkl")
print("✅ Modelo guardado como 'modelo_puerta.pkl'")
