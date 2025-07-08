#Libraries
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import requests

# We use the previous CSV
df = pd.read_csv("data/argenprop_data.csv")

# TC used for USD to ARS conversion
url = "https://api.bluelytics.com.ar/v2/latest"
resp = requests.get(url)
resp.raise_for_status()
data = resp.json()
tc = data["blue"]["value_avg"]
print(f"✅ Current USD→ARS rate (blue): {tc:.2f} ARS") 

# Conversion
df["Precio_Pesos"] = df.apply(
    lambda x: x["Precio"] * tc if x["Moneda"] == "USD" else x["Precio"],
    axis=1
)

# Price per m²
df["Precio_m2"] = df["Precio_Pesos"] / df["Superficie"]

# Change in expenses format
df["Expensas"] = pd.to_numeric(df["Expensas"], errors="coerce")

# Nule and negatives treatment
df = df.dropna(subset=["Precio_Pesos", "Precio_m2", "Expensas", "Superficie"])
df = df[(df["Precio_Pesos"] > 0) & (df["Precio_m2"] > 0) & (df["Expensas"] > 0)]

# Outliers treatment
q99_precio = df["Precio_Pesos"].quantile(0.99)
q99_m2 = df["Precio_m2"].quantile(0.99)
df_filtrado = df[(df["Precio_Pesos"] <= q99_precio) & (df["Precio_m2"] <= q99_m2)]

# Log transf.
X = df_filtrado[["Precio_Pesos", "Precio_m2", "Expensas"]].copy()
X = np.log(X)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Clustering
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df_filtrado["Cluster"] = kmeans.fit_predict(X_scaled)

df_filtrado["Tipo_Propiedad"] = df_filtrado["Cluster"].map({
    0: "Compact and budget-friendly",
    1: "Exclusive premium",
    2: "Spacious and affordable",
    3: "High price per m²"
})

# Paso 12: Exportar resultado
df_filtrado.to_csv("C:/Users/SMoretti/Downloads/Portafolio/01. Alquileres/data/argenprop_data_clustering.csv", index=False, encoding="utf-8-sig")
print("✅ Archivo guardado con outliers excluidos.")

