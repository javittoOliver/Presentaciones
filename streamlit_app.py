import streamlit as st
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
import re
from groq import Groq

# Establece la clave API para acceder a la API de Groq desde st.secrets
api_key = st.secrets["general"]["GROQ_API_KEY"]

st.markdown("""
<style>
.title {
    font-size: 6rem;
    color: #5F9EA0;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">Generador de Presentaciones</p>', unsafe_allow_html=True)
tema_input = st.text_input("Tema: Introduce el tema sobre el que quieres desarrollar la ppt", "Historia del Arte")
cantidad_slides_input = st.selectbox("Cantidad de Slides: Selecciona la cantidad de Hojas que quieres que tenga la ppt", ["5", "2", "3", "4", "6", "7", "8", "9"])
publico_objetivo_input = st.text_input("Público Objetivo: ¿A quien irá dirigida?", "Público en General")
fuente_input = st.text_input("Fuentes de preferencia: Ingresa la fuente de preferencia, por ejemplo: publicaciones de organización x", "Lo que encuentres")


with st.sidebar:
    st.markdown("""
    <style>
    .sidebar .sidebar-content {
        font-family: 'Comic Sans MS', cursive, sans-serif;
        color: #ff5733;
        background-color: #f0f8ff;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    st.write("Estás usando  **Streamlit💻** and **Groq🖥**\n from Vitto ✳️")
    
    uploaded_file = st.file_uploader("Si subes un txt la ppt se genera con estos datos", type=["txt"])

    modelo = st.selectbox("Modelo", ["llama-3.1-70b-versatile","llama3-70b-8192","mixtral-8x7b-32768"])

    max_tokens = st.selectbox("Max New Tokens", [4096,2048,1024])  

    temperature = st.slider("Temperatura", 0.0, 1.0, 0.5, 0.2)


def llama3(prompt, modelo:str="llama-3.1-70b-versatile", max_tokens:int=4096, temperature:int=0.5):
    client = Groq(api_key = api_key)
    MODEL = modelo
    # Step 1: send the conversation and available functions to the model
    messages=[
        {
            "role": "system",
            "content": "Eres un Asistente experto"
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        #tools=tools,
        temperature=temperature,
        tool_choice="auto",
        max_tokens=max_tokens
    )

    response_message = response.choices[0].message.content
    
    return response_message

def analizar_fuente():
    
    if uploaded_file is not None:
        # Leer el contenido del archivo .txt
        fuente = uploaded_file.read().decode("utf-8")
        st.write(f"La fuente cargada es: {fuente}")
    else:
        fuente = fuente_input
    
    return fuente

def update_progress_bar(value):
    progress_bar.progress(value)

def eliminar_asteriscos(texto):
    # Utilizar una expresión regular para encontrar asteriscos
    asterisco_pattern = re.compile(r'\*', flags=re.UNICODE)
    # Eliminar asteriscos del texto
    texto_sin_asteriscos = asterisco_pattern.sub('', texto)
    return texto_sin_asteriscos    

def generar_presentacion():
    update_progress_bar(5)
     

    # Obtener los valores de las cajas de texto en Streamlit
    tema = tema_input
    cantidad_slides = int(cantidad_slides_input)
    publico_objetivo = publico_objetivo_input
    fuentes = analizar_fuente()
    update_progress_bar(25)

    prompt = f"""Genera amplio contenido en español para una presentación en PowerPoint, 
    enumera los slides indicando: Slide1, slide2, etc.
    Indica el Título de cada slide siempre con este formato "Título:".
    Genera títulos pregnantes, impactantes y cortos (menos de 8 palabras).
    No coloque los títulos entre comillas "".
    Comienza con una introducción general motivadora y persuasiva.
    Usa información de las fuentes recomendadas y las que consideres fiables para enriquecer el contenido, 
    puedes citar frases importantes, generar analogías, evidenciar con casos de éxito si el tema lo amerita.
    Desarrolla sobre todo lo que expongas, no des solo títulos u ítems.
    Otorga dinamismo la estructura del texto, usa adecuadamente tabulaciones y elementos para jerarquizar lo
    más importante y para que la lectura no se torne monótona, pero no exageres, no en todos los slides.
    No repitas información, no es necesario que en todos los slides haya evidencia científica por ejemplo.
    Coloca al final de cada slide un salto de línea e "Imagen:" y un texto corto indicando qué tipo de imagen 
    puedo usar en el slide, para usar el texto en el buscador de mi navegador de internet.
    
    Sigue estas instrucciones detalladas: {tema}
    Público objetivo: {publico_objetivo}
    Slides: {cantidad_slides}
    Fuentes: {fuentes}
    """

    # Generar contenido
    prompt = prompt
    contenido = llama3(prompt, modelo, max_tokens, temperature)
    contenidosa = eliminar_asteriscos(contenido)
    update_progress_bar(50)

    # Separar el contenido en diapositivas
    slides = contenidosa.split("Slide")

    # Crear una presentación PowerPoint
    prs = Presentation()

    update_progress_bar(75)

    # Agregar cada diapositiva a la presentación

    for slide_text in slides[1:]:  # El primer elemento de la lista está vacío
        titulo = slide_text.split("Título:", 1)
        title = titulo[1].split("\n", 1)[0].strip()
        content = titulo[1].split("\n", 1)[1].strip()
        
        # Agregar una diapositiva
        slide = prs.slides.add_slide(prs.slide_layouts[1])  # Puedes elegir un diseño de diapositiva diferente si lo deseas
    
        # Configurar el título
        title_shape = slide.shapes.title
        title_shape.text = title
        title_shape.text_frame.paragraphs[0].font.name = 'Poppins'
        title_shape.text_frame.paragraphs[0].font.size = Pt(28)
        title_shape.text_frame.paragraphs[0].font.bold = True
        title_shape.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
    
        # Configurar el contenido
        content_shape = slide.placeholders[1]
        content_shape.text = content
    
        # Reducir el tamaño de la fuente del contenido
        for paragraph in content_shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(14)

    # Guardar la presentación
    prs.save('presentacion_generada.pptx')
    update_progress_bar(100)


if st.button("Generar Presentación"):
    progress_bar = st.progress(0)
    
    try:
        # Llamada a la función para generar la presentación
        generar_presentacion()
        
        # Actualiza la barra de progreso al 100%
        progress_bar.progress(100)
        
        # Mensaje de éxito
        st.success("Presentación generada exitosamente. Descárgala desde abajo.")
        
        # Opción para descargar la presentación
        with open("presentacion_generada.pptx", "rb") as file:
            st.download_button("Descargar Presentación", file, "presentacion_generada.pptx")
    
    except Exception as e:
        # Mensaje de error
        st.error(f"Se produjo un error al generar la presentación: {e}")
