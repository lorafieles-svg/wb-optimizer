import streamlit as st
from rembg import remove
from PIL import Image, ImageOps
import io

# Настройки страницы
st.set_page_config(page_title="WB Photo Optimizer", page_icon="📸")

st.title("📸 WB Photo Optimizer")
st.write("Автоматическая подготовка фото для Wildberries: удаление фона + белый фон + ресайз.")

# Функция обработки
def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    
    # 1. Удаляем фон (AI)
    with st.spinner('Удаляю фон... 🤖'):
        output = remove(image)
    
    # 2. Создаем белый фон (стандарт WB)
    bg_color = (255, 255, 255)
    new_image = Image.new("RGB", output.size, bg_color)
    new_image.paste(output, (0, 0), output)
    
    # 3. Ресайз (2000x2000 - оптимально для зума на WB)
    # Сохраняем пропорции, добавляем белые поля если нужно (pad)
    target_size = (2000, 2000)
    # Сначала ресайзим само изображение чтобы влезло
    new_image.thumbnail(target_size)
    
    # Теперь создаем финальный холст 2000x2000 и центрируем
    final_image = Image.new("RGB", target_size, bg_color)
    
    # Вычисляем позицию для центрирования
    left = (target_size[0] - new_image.size[0]) // 2
    top = (target_size[1] - new_image.size[1]) // 2
    final_image.paste(new_image, (left, top))
    
    return final_image

# Интерфейс загрузки
uploaded_file = st.file_uploader("Загрузите фото товара (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Показываем оригинал
    original_image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    with col1:
        st.header("Оригинал")
        st.image(original_image, use_container_width=True)

    # Кнопка запуска
    if st.button("🚀 Обработать для Wildberries"):
        processed_image = process_image(uploaded_file)
        
        with col2:
            st.header("Готово (WB)")
            st.image(processed_image, use_container_width=True)
            
        # Кнопка скачивания
        buf = io.BytesIO()
        processed_image.save(buf, format="JPEG", quality=95)
        byte_im = buf.getvalue()
        
        st.download_button(
            label="💾 Скачать результат",
            data=byte_im,
            file_name="wb_optimized.jpg",
            mime="image/jpeg"
        )
