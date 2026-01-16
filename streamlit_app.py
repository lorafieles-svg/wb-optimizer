import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO

# Настройка страницы
st.set_page_config(layout="wide", page_title="Удаление фона для WB/Ozon")

st.title("✂️ Генератор фото для маркетплейсов")
st.write("Загрузите фото товара, чтобы убрать фон и подготовить карточку.")

# --- Боковая панель настроек ---
st.sidebar.header("Настройки обработки")

# Опция: Альфа-матирование (для сложных объектов типа волос или меха)
use_alpha_matting = st.sidebar.checkbox(
    "Улучшить края (Alpha Matting)", 
    value=False, 
    help="Включите для пушистых объектов или волос. Обработка займет чуть больше времени."
)

# Опция: Цвет фона
bg_option = st.sidebar.radio(
    "Выберите фон результата:",
    ("Прозрачный (PNG)", "Белый (JPG/PNG)", "Цветной")
)

bg_color = "#FFFFFF" # По умолчанию белый
if bg_option == "Цветной":
    bg_color = st.sidebar.color_picker("Выберите цвет", "#00FF00")

# --- Основная логика ---

# Загрузчик файлов
uploaded_file = st.sidebar.file_uploader("Выберите изображение", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file is not None:
    # Загружаем и показываем оригинал
    original_image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Оригинал")
        st.image(original_image, use_container_width=True)

    # Кнопка обработки (чтобы не запускать тяжелую модель лишний раз)
    if st.sidebar.button("Удалить фон 🚀", type="primary"):
        with st.spinner("Обрабатываю изображение..."):
            try:
                # 1. Удаляем фон
                # Конвертируем в bytes для rembg
                buf = BytesIO()
                original_image.save(buf, format="PNG")
                image_bytes = buf.getvalue()

                # Параметры для rembg
                # alpha_matting помогает с полупрозрачными краями
                result_bytes = remove(
                    image_bytes, 
                    alpha_matting=use_alpha_matting,
                    alpha_matting_foreground_threshold=240,
                    alpha_matting_background_threshold=10
                )
                
                # Открываем результат как PIL Image
                result_image = Image.open(BytesIO(result_bytes))

                # 2. Обработка фона (если выбран не прозрачный)
                final_format = "PNG"
                if bg_option != "Прозрачный (PNG)":
                    # Создаем фон выбранного цвета
                    background = Image.new("RGB", result_image.size, bg_color)
                    # Накладываем вырезанное изображение сверху
                    # Используем result_image как маску само для себя
                    background.paste(result_image, mask=result_image.split()[3]) 
                    result_image = background
                    final_format = "JPEG" if bg_option == "Белый (JPG/PNG)" else "PNG"

                # 3. Показываем результат
                with col2:
                    st.header("Результат")
                    st.image(result_image, use_container_width=True)

                # 4. Кнопка скачивания
                # Конвертируем результат обратно в байты для скачивания
                buf_out = BytesIO()
                result_image.save(buf_out, format=final_format, quality=95)
                byte_im = buf_out.getvalue()

                filename = f"result.{final_format.lower()}"
                
                st.download_button(
                    label="⬇️ Скачать результат",
                    data=byte_im,
                    file_name=filename,
                    mime=f"image/{final_format.lower()}"
                )

            except Exception as e:
                st.error(f"Произошла ошибка: {e}")

else:
    # Инструкция если файл не загружен
    st.info("⬅️ Загрузите файл в меню слева, чтобы начать.")
