import streamlit as st
from models import DetectCards
from envido.cantar_envido import cantar_envido
from PIL import Image

def envido_from_img(img_path: str) -> str:
    image_rgb, cards = DetectCards.detect_and_show_cards_in_image(image_path=img_path)
    envido = cantar_envido(cards)
    st.write(envido)
    return envido

def envido_from_video(video_path: str) -> str:
    cards = DetectCards.detect_and_show_cards_in_video(video_path=video_path)
    envido = cantar_envido(cards)
    st.write(envido)
    return envido

def envido_from_stream():
    st_frame = st.empty()
    stream = DetectCards.detect_and_show_cards_real_time()

    try:
        for frame_rgb in stream:
            st_frame.image(frame_rgb, channels="RGB", caption="Transmisión en Tiempo Real")

            if st.button("Detener Transmisión", key="stop_stream"):
                break
    except RuntimeError as e:
        st.error(f"Error en la transmisión: {e}")
    except Exception as ex:
        st.error(f"Ocurrió un error inesperado: {ex}")

def display_image_with_boxes(img_path):
    image_rgb, cards = DetectCards.detect_and_show_cards_in_image(img_path)
    pil_img = Image.fromarray(image_rgb)
    
    return pil_img, cards

st.title("Truco Copilot")

st.header("Subir una Imagen")
uploaded_image = st.file_uploader("Elige una imagen", type=["jpg", "jpeg", "png"])
if uploaded_image is not None:
    img_path = f"temp_image.{uploaded_image.type.split('/')[-1]}"
    with open(img_path, "wb") as f:
        f.write(uploaded_image.getbuffer())
    pil_img, cards = display_image_with_boxes(img_path)
    st.image(pil_img, caption="Imagen con Bounding Boxes", use_column_width=True)
    envido_from_img(img_path)

st.header("Subir un Video")
uploaded_video = st.file_uploader("Elige un video", type=["mp4", "avi", "mov"])
if uploaded_video is not None:
    video_path = f"temp_video.{uploaded_video.type.split('/')[-1]}"
    with open(video_path, "wb") as f:
        f.write(uploaded_video.getbuffer())
    st.video(video_path)
    envido_from_video(video_path)

st.header("Transmisión en Tiempo Real")
if st.button("Iniciar Transmisión en Tiempo Real"):
    envido_from_stream()
