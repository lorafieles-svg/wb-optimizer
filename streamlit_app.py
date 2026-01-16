import streamlit as st
import numpy as np
import cv2
from rembg import remove
from PIL import Image
from io import BytesIO
from streamlit_drawable_canvas import st_canvas

st.set_page_config(layout="wide", page_title="Умное выделение объектов")

st.title("🖌️ Выделите предмет для обработки")
st.write("Обведите нужный предмет, и нейросеть оставит только его.")

# --- Сайдбар ---
st.sidebar.header("Настройки")
uploaded_file = st.sidebar.file_uploader("1. Загрузите фото", type=["png", "jpg", "jpeg", "webp"])

# Настройки кисти
stroke_width = st.sidebar.slider("Толщина линии выделения", 1, 10, 3)
point_display_radius = st.sidebar.slider("Радиус точек (для точности)", 0, 9, 3) if st.sidebar.checkbox("Показать точки контура") else 0

bg_option = st.sidebar.radio("Фон результата:", ("Прозрачный", "Белый", "Цветной"))
bg_color = "#FFFFFF"
if bg_option == "Цветной":
    bg_color = st.sidebar.color_picker("Цвет фона", "#00FF00")

# --- Логика ---
if uploaded_file:
    # 1. Подготовка изображения
    image = Image.open(uploaded_file).convert("RGB")
    
    # Подгоняем размер для удобства рисования (макс ширина 700px)
    max_width = 700
    if image.width > max_width:
        ratio = max_width / image.width
        new_height = int(image.height * ratio)
        image = image.resize((max_width, new_height))
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Оригинал (Рисуйте здесь)")
        st.info("👆 Выберите инструмент 'Polygon' (многоугольник) в меню ниже и обведите предмет по контуру (замкните линию).")
        
        # 2. Создаем Канвас (Холст) для рисования
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Оранжевая заливка выделения
            stroke_width=stroke_width,
            stroke_color="#FF0000",
            background_image=image,
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="polygon", # Режим рисования многоугольника
            point_display_radius=point_display_radius,
            key="canvas",
        )

    # 3. Обработка выделения
    if canvas_result.image_data is not None:
        # Получаем маску, которую нарисовал пользователь
        mask = canvas_result.image_data[:, :, 3] # Берем только Alpha канал (прозрачность)
        
        # Проверяем, нарисовал ли пользователь хоть что-то
        if np.sum(mask) > 0:
            with col2:
                st.header("Результат")
                
                if st.button("🚀 Вырезать выделенное", type="primary"):
                    with st.spinner("Вырезаю и чищу края..."):
                        try:
                            # А. Применяем грубую маску пользователя
                            img_array = np.array(image)
                            # Создаем 4-й канал (альфа)
                            img_array = np.dstack((img_array, np.zeros((image.height, image.width), dtype=np.uint8) + 255))
                            
                            # Там, где маска 0 (ничего не нарисовано), делаем картинку прозрачной
                            img_array[mask == 0] = [0, 0, 0, 0]
                            
                            rough_cut = Image.fromarray(img_array)

                            # Б. Отправляем грубый срез в REMBG для идеальной зачистки краев
                            # Сначала конвертируем в байты
                            buf = BytesIO()
                            rough_cut.save(buf, format="PNG")
                            rough_bytes = buf.getvalue()

                            # Чистовое удаление фона
                            clean_bytes = remove(rough_bytes)
                            final_image = Image.open(BytesIO(clean_bytes))

                            # В. Работа с фоном (белый/цветной)
                            final_format = "PNG"
                            if bg_option != "Прозрачный":
                                background = Image.new("RGB", final_image.size, bg_color)
                                background.paste(final_image, mask=final_image.split()[3])
                                final_image = background
                                final_format = "JPEG"

                            st.image(final_image, use_container_width=True)
                            
                            # Скачивание
                            buf_out = BytesIO()
                            final_image.save(buf_out, format=final_format, quality=100)
                            st.download_button("⬇️ Скачать результат", buf_out.getvalue(), f"cutout.{final_format.lower()}", f"image/{final_format.lower()}")

                        except Exception as e:
                            st.error(f"Ошибка: {e}")
        else:
            with col2:
                st.write("👈 Обведите предмет слева, чтобы появился результат.")
    
else:
    st.info("Загрузите картинку в меню слева.")
