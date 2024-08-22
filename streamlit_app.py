import streamlit as st
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
import re
from groq import Groq

# Establece la clave API para acceder a la API de Groq desde st.secrets
api_key = st.secrets["general"]["GROQ_API_KEY"]

# Streamlit UI
st.title("Generador de Presentaciones")

tema_input = st.text_input("Tema: Introduce el tema sobre el que quieres desarrollar la ppt")
cantidad_slides_input = st.selectbox("Cantidad de Slides: Selecciona la cantidad de Hojas que quieres que tenga la ppt", ["2", "3", "4", "5", "6", "7", "8", "9"])
publico_objetivo_input = st.text_input("Público Objetivo: ¿A quien irá dirigida?", "Público en General")

extension_input = st.selectbox("Extensión del contenido:", ["Corto", "Medio", "Extenso", "Muy extenso"])
fuente_input = st.text_input("Fuentes de preferencia: Ingresa la fuente de preferencia, por ejemplo "publicaciones de organización x"", "Lo que encuentres")

with st.sidebar:
    st.write("Estás usando  **Streamlit💻** and **Groq🖥**\n from Vitto ✳️")
    
    # Permite al usuario subir un archivo txt
    uploaded_file = st.file_uploader("Si subes un txt la ppt se genera con estos datos", type=["txt"])

    # Permite al usuario seleccionar el modelo a utilizar
    modelo = st.selectbox("Modelo", ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"])
  
    # Ajusta la temperatura del modelo para controlar la creatividad
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.5, 0.2)


def llama3(prompt, modelo, temperature:int=0.5):
    client = Groq(api_key = api_key)
    MODEL = modelo
    # Step 1: send the conversation and available functions to the model
    messages=[
        {
            "role": "system",
            "content": "you are a helpful assistant."
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
        max_tokens=4096
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
    extension = extension_input
    update_progress_bar(25)

    prompt = f"""Genera {extension} contenido en español para una presentación en PowerPoint, 
    enumera los slides indicando: Slide1, slide2, etc.
    Indica el Título de cada slide siempre con este formato "Título:".
    Genera títulos pregnantes, impactantes y cortos (menos de 8 palabras).
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
    contenido = llama3(prompt, modelo, temperature)
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

        slide = prs.slides.add_slide(prs.slide_layouts[1])  # Puedes elegir un diseño de diapositiva diferente si lo deseas

        title_shape = slide.shapes.title
        title_shape.text = title
        title_shape.text_frame.paragraphs[0].font.name = 'Poppins'
        title_shape.text_frame.paragraphs[0].font.size = Pt(28)
        title_shape.text_frame.paragraphs[0].font.bold = True
        title_shape.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT

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
    generar_presentacion()
    st.success("Presentación generada exitosamente. Descárgala desde abajo.")
    with open("presentacion_generada.pptx", "rb") as file:
        st.download_button("Descargar Presentación", file, "presentacion_generada.pptx")
