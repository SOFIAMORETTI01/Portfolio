import streamlit as st
import pandas as pd
import unicodedata
import re
import csv
st.set_page_config(page_title="BOT - Materias FCE 🎓", page_icon="🎓", layout="centered")

st.markdown("""

<style>
/* Fondo blanco para toda la página */
.stApp {
    background-color: white;
    display: flex;
    justify-content: center;
}

/* Recuadro general del bot */
main .block-container {
    background-color: #fef3e2;             /* Fondo suave interior */
    border: 3px solid #e6b390;             /* Borde visible (color durazno) */
    border-radius: 20px;
    padding: 40px;
    max-width: 800px;
    margin-top: 30px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}


/* Estilo general de texto */
body, div, p, label {
    color: #1c1c1c;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* Burbuja del bot */
.stChatMessage {
    background-color: #ffffff !important;
    border-radius: 20px;
    padding: 10px 14px;
    max-width: 100% !important;
    border: 1px solid #e6b390;
    margin-bottom: 12px;
}

/* Alinear mensajes del usuario a la derecha */
div[data-testid="stChatMessage"]:has(div[data-testid="stAvatarIcon-user"]) {
    display: flex !important;
    justify-content: flex-end !important;
}
body, div, p, label {
    color: #1c1c1c;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
.stChatMessage {
    background-color: #fef3e2 !important;
    border-radius: 20px;
    padding: 10px 14px;
    max-width: 100% !important;
    border: 1px solid #e6b390;
    margin-bottom: 12px;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stAvatarIcon-user"]) {
    display: flex !important;
    justify-content: flex-end !important;
}

</style>
""", unsafe_allow_html=True)

def normalizar(texto):
    if pd.isna(texto):
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

@st.cache_data
def cargar_datos():
    import csv
    df = pd.read_csv(
        "bot_project/Materias_BOT.csv",
        encoding="latin1",
        sep=";",
        quoting=csv.QUOTE_MINIMAL,
        engine="python"
    )
    df.columns = df.columns.str.strip()

    for col in ["Carrera", "Materia", "Correlativas"]:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode('utf-8').strip())

    df["Carrera_norm"] = df["Carrera"].apply(normalizar)
    df["Materia_norm"] = df["Materia"].apply(normalizar)
    return df


# Cargar df una vez acá
df = cargar_datos()

carreras_opciones = [
    "Contador",
    "Licenciatura en Administración de Empresas",
    "Licenciatura en Economía",
    "Licenciatura en Sistemas",
    "Actuario"
]

def normalizar(texto):
    if pd.isna(texto):
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

# Inicializar estado
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{
        "rol": "assistant",
        "contenido": (
            "👋 ¡Hola! Soy el bot de ayuda de FCE.\n\n"
            "Estoy acá para ayudarte a entender las materias, sus correlativas, y también las optativas y electivas vigentes.\n\n"
            "📚 Para comenzar, elegí tu carrera escribiendo el número correspondiente:\n"
            "```\n"
            "1️⃣ Contador\n"
            "2️⃣ Licenciatura en Administración de Empresas\n"
            "3️⃣ Licenciatura en Economía\n"
            "4️⃣ Licenciatura en Sistemas\n"
            "5️⃣ Actuario\n"
            "```"
        )
    }]
if "estado" not in st.session_state:
    st.session_state.estado = "inicio"
if "carrera" not in st.session_state:
    st.session_state.carrera = ""
if "materia" not in st.session_state:
    st.session_state.materia = ""

def mostrar_menu():
    return (
        "📚 ¿Qué tipo de información necesitás consultar?\n"
        "```\n"
        "1️⃣ Materias correlativas\n"
        "2️⃣ Materias optativas\n"
        "3️⃣ Materias electivas\n"
        "4️⃣ Volver al menú inicial\n"
        "```"
    )

def responder_usuario(entrada_usuario):
    st.session_state.mensajes.append({"rol": "user", "contenido": entrada_usuario})
    entrada_norm = normalizar(entrada_usuario)

    if st.session_state.estado == "inicio":
        if entrada_norm in ["1", "2", "3", "4", "5", "6"]:
            seleccion = int(entrada_norm) - 1
            st.session_state.carrera = carreras_opciones[seleccion]
            st.session_state.estado = "menu"
            respuesta = f"🎓Tu carrera es: **{st.session_state.carrera}**.\n\n" + mostrar_menu()
        else:
            respuesta = (
                "❌ Opción inválida. Por favor escribí un número del 1 al 6 para elegir tu carrera:\n"
                "```\n"
                "1️⃣ Contador\n"
                "2️⃣ Licenciatura en Administración de Empresas\n"
                "3️⃣ Licenciatura en Economía\n"
                "4️⃣ Licenciatura en Sistemas\n"
                "5️⃣ Actuario\n"
                "```"
            )

    elif st.session_state.estado == "menu":
        carrera_norm = normalizar(st.session_state.carrera)
        df["Carrera_norm"] = df["Carrera"].apply(normalizar)

        if entrada_norm in ["1", "uno"]:
            st.session_state.estado = "correlativas"
            respuesta = "✏️ Escribí el nombre de la materia para ver sus correlativas:"
        elif entrada_norm in ["2", "dos"]:
            st.session_state.estado = "optativas"
            optativas = df[
                (df["Código"] == "Optativa") &
                (df["Carrera_norm"] == carrera_norm)
            ]["Materia"].dropna().tolist()

            if optativas:
                respuesta = "📘 Estas son las materias optativas vigentes para tu carrera:\n" + "\n".join(f"- {m}" for m in optativas)
            else:
                respuesta = "⚠️ No encontré materias optativas vigentes para tu carrera."

            respuesta += (
                "\n\n📋 ¿Qué querés hacer ahora?\n"
                "```\n"
                "1️⃣ Volver al menú\n"
                "```"
            )
        elif entrada_norm in ["3", "tres"]:
            st.session_state.estado = "electivas"
            electivas = df[
                (df["Código"] == "Electiva") &
                (df["Carrera_norm"] == carrera_norm)
            ]["Materia"].dropna().tolist()

            if electivas:
                respuesta = "📗 Estas son las materias electivas vigentes para tu carrera:\n" + "\n".join(f"- {m}" for m in electivas)
            else:
                respuesta = "⚠️ No encontré materias electivas vigentes para tu carrera."

            respuesta += (
                "\n\n📋 ¿Qué querés hacer ahora?\n"
                "```\n"
                "1️⃣ Volver al menú\n"
                "```"
            )
        elif entrada_norm in ["4", "cuatro"]:
            st.session_state.estado = "inicio"
            st.session_state.carrera = ""
            respuesta = (
                "🔁 Volviste al menú inicial.\n\n"
                "📚 Para comenzar, elegí tu carrera escribiendo el número correspondiente:\n"
                "```\n"
                "1️⃣ Contador\n"
                "2️⃣ Licenciatura en Administración de Empresas\n"
                "3️⃣ Licenciatura en Economía\n"
                "4️⃣ Licenciatura en Sistemas\n"
                "5️⃣ Actuario\n"
                "```"
            )
        else:
            respuesta = "❌ Opción inválida. Por favor escribí 1, 2, 3 o 4.\n\n" + mostrar_menu()

    elif st.session_state.estado == "correlativas":
        if entrada_norm == "2":
            st.session_state.estado = "menu"
            respuesta = mostrar_menu()
        elif entrada_norm == "1":
            respuesta = "✏️ Escribí el nombre de la materia para ver sus correlativas:"
        else:
            st.session_state.materia = entrada_usuario.strip()
            carrera_norm = normalizar(st.session_state.carrera)

            df["Carrera_norm"] = df["Carrera"].apply(normalizar)
            df["Materia_norm"] = df["Materia"].apply(normalizar)

            coincidencias = df[
                (df["Carrera_norm"] == carrera_norm) &
                (df["Materia_norm"] == entrada_norm)
            ]

            if coincidencias.empty:
                respuesta = f"❌ No encontré la materia **{st.session_state.materia}** en la carrera **{st.session_state.carrera}**."
            else:
                correlativas_raw = coincidencias["Correlativas"].values[0]
                correlativas = str(correlativas_raw).replace('"', '').strip()
                if correlativas in ["", "-", "", "|", "nan"]:
                   respuesta = f"✅ Para **{st.session_state.materia}**, ¡no necesitás correlativas!"
                else:
                   lista = [x.strip() for x in correlativas.split("|") if x.strip()]
                   respuesta = f"📚 Para **{st.session_state.materia}**, necesitás tener aprobada:\n"
                   for c in lista:
                    respuesta += f"- {c}\n"

            respuesta += (
                "\n\n📋 ¿Qué querés hacer ahora?\n"
                "```\n"
                "1️⃣ Consultar por otra materia\n"
                "2️⃣ Volver al menú\n"
                "```"
            )

    elif st.session_state.estado in ["optativas", "electivas"]:
        if entrada_norm == "1":
            st.session_state.estado = "menu"
            respuesta = mostrar_menu()
        else:
            respuesta = (
                "📋 ¿Qué querés hacer ahora?\n"
                "```\n"
                "1️⃣ Volver al menú\n"
                "```"
            )

        st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})
        return

    else:
        respuesta = "⚠️ Algo salió mal. Por favor, escribí nuevamente."

    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})

# -------------------
st.title("🎓 BOT - Materias FCE")

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

entrada = st.chat_input("Escribí tu respuesta acá...")

if entrada:
    responder_usuario(entrada)
    st.rerun()

