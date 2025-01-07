
import streamlit as st
import requests
import json

# Inicialización del session_state
if 'token' not in st.session_state:
    st.session_state.token = None

# Si no tenemos token, intentamos obtenerlo
if st.session_state.token is None:
    try:
        token_response = requests.post(
            'http://localhost:8000/api/v1/token',
            json={"username": "test-user"}
        )
        if token_response.ok:
            st.session_state.token = token_response.json()["access_token"]
        else:
            st.error("Error obteniendo el token de autenticación")
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")

st.title('Sistema Experto Holístico')

# Añadida key única al text_area
query = st.text_area(
    "Escribe tu consulta:",
    placeholder="Por ejemplo: ¿Qué efectos tiene la radiación del microondas sobre las plantas medicinales?",
    key="query_input"  # Añadida esta línea
)

# Añadida key única al botón
if st.button('Enviar Consulta', key="submit_button"):  # Añadida key aquí también
    if query and st.session_state.token:
        try:
            response = requests.post(
                'http://localhost:8000/api/v1/medical/query',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {st.session_state.token}'
                },
                json={
                    'query': query,
                    'user_id': 'test-user',
                    'context': {}
                }
            )
            
            if response.ok:
                result = response.json()
                st.subheader('Respuesta Integrada')
                st.write(result['response'])
                if 'sources' in result:
                    st.subheader('Análisis por Dominios')
                    for domain, info in result['sources'].items():
                        # Añadida key única para cada expander
                        with st.expander(f"Análisis {domain.capitalize()}"):
                            st.write(info['response'])
                            st.progress(info['confidence'])
            else:
                st.error(f'Error en la consulta: {response.text}')
        except Exception as e:
            st.error(f'Error: {str(e)}')
    elif not st.session_state.token:
        st.error("No hay token de autenticación disponible")
