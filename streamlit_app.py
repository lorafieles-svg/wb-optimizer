import streamlit as st
# Импортируем 'new_session' для работы с конкретной моделью
from rembg import remove, new_session
from PIL import Image
import io

st.set_page_config(page_title="WB Optimizer", layout="centered")

st.title("📸 WB Photo Optimizer (Lite)")
st.write("Загрузите фото — фон удалится автоматически.")

# Создаем "легкую" сессию (u2netp весит мало и не убивает память)
# Это ключевое исправление!
model_name = "u2netp" 
session = new_session(model_name)

def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    
    # Передаем нашу легкую сессию в функцию remove
    with st.spinner('Обработка...'):
        output = remove(image, session=session)
    
    # Белый фон + ресайз
    bg_color = (255, 255, 255)
    new_image = Image.new("RGB", output.size, bg_color)
    new_image.paste(output, (0, 0), output)
    
    target_size = (2000, 2000)
    new_image.thumbnail(target_size)
    
    final_image = Image.new("RGB", target_size, bg_color)
    left = (target_size[0] - new_image.size[0]) // 2
    top = (target_size[1] - new_image.size[1]) // 2
    final_image.paste(new_image, (left, top))
    
    return final_image

uploaded_file = st.file_uploader("Выберите фото", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="Было")
        
    if st.button("🚀 Обработать"):
        result = process_image(uploaded_file)
        with col2:
            st.image(result, caption="Стало (WB)")
            
        buf = io.BytesIO()
        result.save(buf, format="JPEG", quality=95)
        st.download_button("Скачать", buf.getvalue(), "wb_photo.jpg", "image/jpeg")
