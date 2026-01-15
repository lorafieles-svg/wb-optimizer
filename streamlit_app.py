import streamlit as st
from rembg import new_session, remove
from PIL import Image
import io

st.title("📸 WB Photo Optimizer")
st.write("Загрузка фото → белый фон → готово для Wildberries!")

session = new_session("u2netp")  # Легкая модель (4 МБ)

uploaded_file = st.file_uploader("Выберите фото товара", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("До")
        st.image(image, use_column_width=True)
    
    if st.button("🚀 Обработать для WB"):
        with st.spinner("Убираю фон..."):
            output = remove(image, session=session)
            
            # Белый фон
            bg = Image.new("RGB", output.size, (255, 255, 255))
            bg.paste(output, mask=output)
            
            # Ресайз под WB
            bg.thumbnail((2000, 2000))
            
            with col2:
                st.subheader("После")
                st.image(bg, use_column_width=True)
            
            buf = io.BytesIO()
            bg.save(buf, "JPEG", quality=95)
            st.download_button("💾 Скачать", buf.getvalue(), "wb_photo.jpg", "image/jpeg")
