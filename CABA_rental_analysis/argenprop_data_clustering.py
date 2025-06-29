#Libraries
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# We use the previous CSV
df = pd.read_csv("C:/Users/SMoretti/Downloads/Portafolio/01. Alquileres/argenprop_data.csv")

# TC
tc = 1142

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
df_filtrado.to_csv("C:/Users/SMoretti/Downloads/Portafolio/01. Alquileres/argenprop_data_clustering.csv", index=False, encoding="utf-8-sig")
print("✅ Archivo guardado con outliers excluidos.")

