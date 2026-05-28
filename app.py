import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# =========================================
# CONFIGURACIÓN DE PÁGINA
# =========================================

st.set_page_config(
    page_title="VoiceControl AI",
    page_icon="🎙️",
    layout="centered"
)

# =========================================
# ESTILOS VISUALES
# =========================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #fff3b0,
        #ffcf99,
        #ff9f1c
    );
    background-attachment: fixed;
}

h1, h2, h3 {
    color: #7f4f24;
    text-align: center;
}

p, label, div {
    color: #5a3e1b;
}

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(12px);
}

.stButton>button {
    background-color: #ff7b00;
    color: white;
    border-radius: 14px;
    border: none;
    padding: 0.7rem 1rem;
    font-weight: bold;
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #ff9500;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# MQTT
# =========================================

broker = "broker.mqttdashboard.com"
port = 1883

client1 = paho.Client("Pglagarto2005")

# =========================================
# CALLBACKS
# =========================================

def on_publish(client, userdata, result):

    print("Dato publicado correctamente")

def on_message(client, userdata, message):

    global message_received

    time.sleep(1)

    message_received = str(
        message.payload.decode("utf-8")
    )

    st.success("📩 Mensaje recibido")

    st.write(message_received)

client1.on_message = on_message

# =========================================
# HEADER
# =========================================

st.title("🎙️ VoiceControl AI")

st.markdown("""
### Control inteligente de dispositivos mediante comandos de voz y MQTT
""")

st.markdown("---")

# =========================================
# IMAGEN
# =========================================

image = Image.open('Correa.jpg')

st.image(
    image,
    width=260
)

# =========================================
# COMANDOS
# =========================================

with st.expander("📖 Comandos disponibles"):

    st.markdown("""
- 🟢 **enciende las luces**
- 🔴 **apaga las luces**
- 🚪 **abre la puerta**
- 🔒 **Cierra la puerta**
""")

# =========================================
# TEXTO
# =========================================

st.subheader("🎤 Presiona el botón y da un comando")

st.info("""
📡 El sistema reconocerá tu voz y enviará el comando automáticamente mediante MQTT.
""")

# =========================================
# BOTÓN VOZ
# =========================================

stt_button = Button(
    label="🎙️ Iniciar reconocimiento",
    width=250
)

stt_button.js_on_event(
    "button_click",
    CustomJS(code="""
    var recognition = new webkitSpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "es-ES";

    recognition.onresult = function (e) {

        var value = "";

        for (var i = e.resultIndex; i < e.results.length; ++i) {

            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }

        if (value != "") {

            document.dispatchEvent(
                new CustomEvent(
                    "GET_TEXT",
                    {detail: value}
                )
            );
        }
    }

    recognition.start();
    """)
)

# =========================================
# STREAMLIT EVENTS
# =========================================

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# =========================================
# RESULTADO
# =========================================

if result:

    if "GET_TEXT" in result:

        comando = result.get(
            "GET_TEXT"
        ).strip()

        st.markdown("## 🗣️ Comando Detectado")

        st.success(comando)

        # MQTT
        client1.on_publish = on_publish

        client1.connect(
            broker,
            port
        )

        # JSON
        message = json.dumps({
            "Act1": comando
        })

        # PUBLICAR
        ret = client1.publish(
            "voice_ctrl",
            message
        )

        st.success(
            "✅ Comando enviado correctamente al ESP32"
        )

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.markdown(
    """
    <center>
    🧠 Desarrollado con Streamlit + MQTT + Speech Recognition
    </center>
    """,
    unsafe_allow_html=True
)
