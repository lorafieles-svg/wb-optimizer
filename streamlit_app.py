import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO
from streamlit_cropper import st_cropper  # Импортируем кроппер

st.set_page_config(layout="wide", page_title="Удаление фона для WB/Ozon")

st.title("✂️ Генератор фото для маркетплейсов")

# --- Боковая панель ---
st.sidebar.header("Настройки")

# Загрузка
uploaded_file = st.sidebar.file_uploader("Выберите изображение", type=["png", "jpg", "jpeg", "webp"])

# Настройки фона
bg_option = st.sidebar.radio(
    "Фон результата:",
    ("Прозрачный (PNG)", "Белый (JPG)", "Цветной")
)
bg_color = "#FFFFFF"
if bg_option == "Цветной":
    bg_color = st.sidebar.color_picker("Выберите цвет", "#00FF00")

# Настройки обработки
use_alpha_matting = st.sidebar.checkbox("Улучшить края (для меха/волос)", value=False)
enable_cropping = st.sidebar.checkbox("✂️ Обрезать фото перед обработкой", value=True)

# --- Основная часть ---
if uploaded_file is not None:
    original_image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    # БЛОК 1: Работа с оригиналом
    with col1:
        st.header("1. Исходник")
        
        # Логика обрезки
        if enable_cropping:
            st.info("Выделите область, которую нужно оставить:")
            # Виджет обрезки. realtime_update=True показывает результат сразу
            image_to_process = st_cropper(
                original_image,
                realtime_update=True,
                box_color='#FF0000',
                aspect_ratio=None 
            )
            st.caption("Результат обрезки (превью):")
            st.image(image_to_process, width=200)
        else:
            st.image(original_image, use_container_width=True)
            image_to_process = original_image

    # БЛОК 2: Результат
    with col2:
        st.header("2. Результат")
        
        # Кнопка запуска
        if st.button("Удалить фон 🚀", type="primary"):
            with st.spinner("Магия нейросетей..."):
                try:
                    # Конвертация для rembg
                    buf = BytesIO()
                    image_to_process.save(buf, format="PNG")
                    img_bytes = buf.getvalue()

                    # Удаление фона
                    result_bytes = remove(
                        img_bytes, 
                        alpha_matting=use_alpha_matting,
                        alpha_matting_foreground_threshold=240,
                        alpha_matting_background_threshold=10
                    )
                    
                    result_image = Image.open(BytesIO(result_bytes))

                    # Наложение фона
                    final_format = "PNG"
                    if bg_option != "Прозрачный (PNG)":
                        background = Image.new("RGB", result_image.size, bg_color)
                        background.paste(result_image, mask=result_image.split()[3])
                        result_image = background
                        final_format = "JPEG"

                    # Показ результата
                    st.image(result_image, use_container_width=True)

                    # Скачивание
                    buf_out = BytesIO()
                    result_image.save(buf_out, format=final_format, quality=95)
                    st.download_button(
                        label="⬇️ Скачать",
                        data=buf_out.getvalue(),
                        file_name=f"result.{final_format.lower()}",
                        mime=f"image/{final_format.lower()}"
                    )

                except Exception as e:
                    st.error(f"Ошибка: {e}")
        else:
            st.info("Нажмите кнопку, чтобы обработать выделенную область.")

else:
    st.info("⬅️ Загрузите файл в меню слева.")
