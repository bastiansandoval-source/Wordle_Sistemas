import random
import unicodedata
import streamlit as st

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Wordle: Termodinámica y Efecto Invernadero",
    page_icon="🌎",
    layout="centered"
)

MAX_INTENTOS = 6


# =========================
# BANCO DE PALABRAS
# =========================
PALABRAS_POR_TEMA = {
    "Termodinámica": [
        "CALOR",
        "FRIO",
        "TERMICO",
        "TERMICA",
        "ENERGIA",
        "TEMPERATURA",
        "TRANSFERENCIA",
        "CONDUCCION",
        "CONVECCION",
        "RADIACION",
        "ABSORCION",
        "REFLEXION",
        "EMISION",
        "EQUILIBRIO",
        "SISTEMA",
        "AISLANTE",
        "CONDUCTOR",
        "PARTICULAS",
        "DILATACION",
        "TERMOMETRO",
        "CELSIUS",
        "KELVIN",
        "FAHRENHEIT",
        "CALENTAR",
        "ENFRIAR",
        "EVAPORACION",
        "CONDENSACION",
        "VAPORIZACION",
        "FUSION",
        "SOLIDO",
        "LIQUIDO",
        "GASEOSO",
        "INTERCAMBIO",
        "CONTACTO",
        "FLUIDO",
        "AISLACION",
        "CONSERVACION"
    ],

    "Efecto invernadero": [
        "EFECTO",
        "INVERNADERO",
        "ATMOSFERA",
        "SOLAR",
        "GASES",
        "GEI",
        "CARBONO",
        "DIOXIDO",
        "METANO",
        "VAPOR",
        "RETENCION",
        "ESCAPA",
        "ESCAPE",
        "ALBEDO",
        "ABSORCION",
        "REFLEXION",
        "RADIACION",
        "INFRARROJA",
        "EMISION",
        "EMISIONES",
        "COMBUSTION",
        "FOSILES",
        "TEMPERATURA",
        "CALENTAMIENTO",
        "ENERGIA",
        "TIERRA",
        "SUPERFICIE",
        "INTENSIFICADO",
        "NATURAL",
        "RADIATIVO",
        "ATMOSFERICO",
        "RETENIDA"
    ]
}


# =========================
# FUNCIONES AUXILIARES
# =========================
def normalizar(texto: str) -> str:
    """
    Convierte el texto a mayúsculas y elimina tildes.
    Ejemplo: radiación -> RADIACION
    """
    texto = texto.strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caracter for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )
    return texto


def obtener_todas_las_palabras():
    palabras = []

    for lista in PALABRAS_POR_TEMA.values():
        palabras.extend(lista)

    palabras = [normalizar(p) for p in palabras if p.strip()]
    palabras = sorted(set(palabras))
    palabras = [p for p in palabras if len(p) >= 3 and p.isalpha()]

    return palabras


def obtener_palabras_por_tema(tema: str):
    palabras = PALABRAS_POR_TEMA[tema]
    palabras = [normalizar(p) for p in palabras if p.strip()]
    palabras = sorted(set(palabras))
    palabras = [p for p in palabras if len(p) >= 3 and p.isalpha()]
    return palabras


def filtrar_por_largo(palabras, largo_elegido):
    if largo_elegido == "Aleatorio":
        return palabras

    largo = int(largo_elegido)
    return [p for p in palabras if len(p) == largo]


# =========================
# SIDEBAR
# =========================
st.sidebar.title("Opciones del juego")

tema_elegido = st.sidebar.selectbox(
    "Tema de palabras:",
    list(PALABRAS_POR_TEMA.keys())
)

palabras_del_tema = obtener_palabras_por_tema(tema_elegido)
largos_disponibles = sorted(set(len(p) for p in palabras_del_tema))

largo_elegido = st.sidebar.selectbox(
    "Largo de palabra:",
    ["Aleatorio"] + [str(largo) for largo in largos_disponibles]
)

aceptar_cualquier_palabra = st.sidebar.checkbox(
    "Aceptar cualquier palabra como intento",
    value=True
)

modo_docente = st.sidebar.checkbox(
    "Modo docente: mostrar palabra secreta",
    value=False
)

palabras_filtradas = filtrar_por_largo(palabras_del_tema, largo_elegido)

if not palabras_filtradas:
    st.sidebar.warning("No hay palabras disponibles con ese largo.")
    palabras_filtradas = palabras_del_tema


# =========================
# ESTADO DEL JUEGO
# =========================
def iniciar_juego():
    st.session_state.palabra_secreta = random.choice(palabras_filtradas)
    st.session_state.largo_palabra = len(st.session_state.palabra_secreta)
    st.session_state.intentos = []
    st.session_state.juego_terminado = False
    st.session_state.gano = False
    st.session_state.configuracion_actual = (tema_elegido, largo_elegido)


if "palabra_secreta" not in st.session_state:
    iniciar_juego()

# Si cambia el tema o el largo, se inicia una nueva palabra
if st.session_state.get("configuracion_actual") != (tema_elegido, largo_elegido):
    iniciar_juego()
    st.rerun()

if st.sidebar.button("Nuevo juego"):
    iniciar_juego()
    st.rerun()


# =========================
# LÓGICA WORDLE
# =========================
def evaluar_intento(secreta: str, intento: str):
    """
    Devuelve una lista de estados por letra:
    - correcta: letra correcta en lugar correcto.
    - presente: letra está en la palabra, pero en otra posición.
    - ausente: letra no está en la palabra.
    """
    largo = len(secreta)

    resultado = ["ausente"] * largo
    letras_restantes = list(secreta)

    # Primera pasada: letras correctas
    for i in range(largo):
        if intento[i] == secreta[i]:
            resultado[i] = "correcta"
            letras_restantes[i] = None

    # Segunda pasada: letras presentes en otra posición
    for i in range(largo):
        if resultado[i] == "correcta":
            continue

        if intento[i] in letras_restantes:
            resultado[i] = "presente"
            indice = letras_restantes.index(intento[i])
            letras_restantes[indice] = None

    return resultado


def tamano_casilla(largo):
    """
    Ajusta el tamaño de las casillas según el largo de la palabra.
    """
    if largo <= 5:
        return 62, 1.9
    elif largo <= 7:
        return 54, 1.6
    elif largo <= 9:
        return 46, 1.35
    elif largo <= 11:
        return 39, 1.1
    elif largo <= 13:
        return 34, 0.95
    else:
        return 30, 0.85


# =========================
# ESTILOS CSS
# =========================
st.markdown(
    """
    <style>
    .titulo {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: #4CAF50;
        margin-bottom: 8px;
    }

    .subtitulo {
        text-align: center;
        color: #bbbbbb;
        margin-bottom: 8px;
        font-size: 18px;
    }

    .indicador {
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 20px;
        color: #ffffff;
        background-color: #1f2937;
        border-radius: 12px;
        padding: 10px;
    }

    .tablero-contenedor {
        overflow-x: auto;
        padding-bottom: 8px;
    }

    .fila {
        display: grid;
        gap: 6px;
        justify-content: center;
        margin-bottom: 6px;
    }

    .casilla {
        border: 2px solid #3a3a3c;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        text-transform: uppercase;
        background-color: #121213;
        color: white;
    }

    .correcta {
        background-color: #538d4e;
        border-color: #538d4e;
    }

    .presente {
        background-color: #b59f3b;
        border-color: #b59f3b;
    }

    .ausente {
        background-color: #3a3a3c;
        border-color: #3a3a3c;
    }

    .vacia {
        background-color: #121213;
        border-color: #3a3a3c;
    }

    .leyenda {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .item-leyenda {
        padding: 6px 10px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        font-size: 14px;
    }

    .verde {
        background-color: #538d4e;
    }

    .amarillo {
        background-color: #b59f3b;
    }

    .gris {
        background-color: #3a3a3c;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# INTERFAZ
# =========================
st.markdown(
    '<div class="titulo">🌎 Wordle: Termodinámica y Efecto Invernadero</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="subtitulo">
    Tema: {tema_elegido}
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="indicador">
    La palabra tiene {st.session_state.largo_palabra} letras
    </div>
    """,
    unsafe_allow_html=True
)

if modo_docente:
    st.info(f"Palabra secreta: {st.session_state.palabra_secreta}")


# =========================
# TABLERO
# =========================
def dibujar_tablero():
    largo = st.session_state.largo_palabra
    tamano, fuente = tamano_casilla(largo)

    html = '<div class="tablero-contenedor">'

    for fila_num in range(MAX_INTENTOS):
        html += (
            f'<div class="fila" '
            f'style="grid-template-columns: repeat({largo}, {tamano}px);">'
        )

        if fila_num < len(st.session_state.intentos):
            palabra, evaluacion = st.session_state.intentos[fila_num]

            for letra, estado in zip(palabra, evaluacion):
                html += (
                    f'<div class="casilla {estado}" '
                    f'style="width:{tamano}px; height:{tamano}px; font-size:{fuente}rem;">'
                    f'{letra}</div>'
                )
        else:
            for _ in range(largo):
                html += (
                    f'<div class="casilla vacia" '
                    f'style="width:{tamano}px; height:{tamano}px; font-size:{fuente}rem;">'
                    f'</div>'
                )

        html += '</div>'

    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)


dibujar_tablero()


# =========================
# LEYENDA
# =========================
st.markdown(
    """
    <div class="leyenda">
        <div class="item-leyenda verde">Correcta</div>
        <div class="item-leyenda amarillo">Está, pero en otro lugar</div>
        <div class="item-leyenda gris">No está</div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# INPUT DEL JUEGO
# =========================
if not st.session_state.juego_terminado:

    with st.form("formulario_intento", clear_on_submit=True):
        intento_usuario = st.text_input(
            f"Escribe una palabra de {st.session_state.largo_palabra} letras:",
            max_chars=st.session_state.largo_palabra
        )

        enviar = st.form_submit_button("Enviar", use_container_width=True)

    if enviar:
        intento = normalizar(intento_usuario)

        if len(intento) != st.session_state.largo_palabra:
            st.warning(
                f"La palabra debe tener exactamente "
                f"{st.session_state.largo_palabra} letras."
            )

        elif not intento.isalpha():
            st.warning("Solo debes escribir letras.")

        elif not aceptar_cualquier_palabra and intento not in obtener_todas_las_palabras():
            st.warning("Esa palabra no está en la lista de palabras válidas.")

        else:
            evaluacion = evaluar_intento(
                st.session_state.palabra_secreta,
                intento
            )

            st.session_state.intentos.append((intento, evaluacion))

            if intento == st.session_state.palabra_secreta:
                st.session_state.juego_terminado = True
                st.session_state.gano = True

            elif len(st.session_state.intentos) >= MAX_INTENTOS:
                st.session_state.juego_terminado = True

            st.rerun()

    if st.button("Reiniciar", use_container_width=True):
        iniciar_juego()
        st.rerun()

else:
    if st.session_state.gano:
        st.success("¡Ganaste! Adivinaste la palabra.")
    else:
        st.error(f"Perdiste. La palabra era: {st.session_state.palabra_secreta}")

    if st.button("Jugar otra vez", use_container_width=True):
        iniciar_juego()
        st.rerun()


# =========================
# AYUDA / EXPLICACIÓN
# =========================
with st.expander("Cómo leer los colores"):
    st.write("🟩 Verde: la letra está en la posición correcta.")
    st.write("🟨 Amarillo: la letra está en la palabra, pero en otra posición.")
    st.write("⬛ Gris: la letra no está en la palabra.")

with st.expander("Palabras posibles según la configuración actual"):
    st.write(", ".join(palabras_filtradas))