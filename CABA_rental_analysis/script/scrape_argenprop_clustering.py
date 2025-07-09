# Import libraries
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import requests

# Load previously scraped rental data from CSV
df = pd.read_csv("data/scrape_argenprop.csv")

# TC
# Fetch current exchange rate (USD → ARS) from Bluelytics API
url = "https://api.bluelytics.com.ar/v2/latest"
resp = requests.get(url)
resp.raise_for_status()
data = resp.json()
# Use the average of the blue dollar (parallel market rate)
tc = data["blue"]["value_avg"]
print(tc)

# --- DATA PREPARATION ---
#  Convert all prices to ARS based on currency
df["Precio_Pesos"] = df.apply(
    lambda x: x["Precio"] * tc if x["Moneda"] == "USD" else x["Precio"],
    axis=1
)

# Calculate price per square meter
df["Precio_m2"] = df["Precio_Pesos"] / df["Superficie"]

# Change in expenses format
df["Expensas"] = pd.to_numeric(df["Expensas"], errors="coerce")

# Nule and negatives treatment
df = df.dropna(subset=["Precio_Pesos", "Precio_m2", "Expensas", "Superficie"])
df = df[(df["Precio_Pesos"] > 0) & (df["Precio_m2"] > 0) & (df["Expensas"] > 0)]

# --- OUTLIER REMOVAL ---
# Remove extreme values using the 99th percentile as threshold
q99_precio = df["Precio_Pesos"].quantile(0.99)
q99_m2 = df["Precio_m2"].quantile(0.99)
df_filtrado = df[(df["Precio_Pesos"] <= q99_precio) & (df["Precio_m2"] <= q99_m2)]

# --- FEATURE TRANSFORMATION & SCALING ---

# Select numeric features for clustering and apply log transformation
X = df_filtrado[["Precio_Pesos", "Precio_m2", "Expensas"]].copy()
X = np.log(X)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- K-MEANS CLUSTERING ---

# Apply KMeans algorithm with 4 clusters
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df_filtrado["Cluster"] = kmeans.fit_predict(X_scaled)

# Assign human-readable labels to each cluster
df_filtrado["Tipo_Propiedad"] = df_filtrado["Cluster"].map({
    0: "Compact and budget-friendly",
    1: "Exclusive premium",
    2: "Spacious and affordable",
    3: "High price per m²"
})

# --- EXPORT RESULTS ---
# Save the clustered dataset to CSV for further analysis or dashboarding
df_filtrado.to_csv("data/scrape_argenprop_clustering.csv", index=False, encoding="utf-8-sig")


