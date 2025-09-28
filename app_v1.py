import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI(model="gpt-5", temperature=0, api_key=openai_api_key)

st.title("U-Tutor, tu asistente universitario v1.0")

# Mensaje de sistema (contexto para la IA)
messages = [("system", """Eres Jake, un tutor universitario empático y profesional. Ayuda al estudiante con sus dudas, habla como humano y nunca reveles que eres una IA.""" )]

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de chat al recargar la app
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Reaccionar a la entrada del usuario
if prompt := st.chat_input("Escribe tu mensaje..."):
    # Mostrar mensaje del usuario
    st.chat_message("user").markdown(prompt)

    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    messages.append(["human", prompt])

    # Obtener respuesta 
    response = llm.invoke(messages).content

    # Mostrar respuesta
    with st.chat_message("assistant"):
        st.markdown(response)

    # Agregar respuesta al historial
    st.session_state.messages.append({"role": "assistant", "content": response})
