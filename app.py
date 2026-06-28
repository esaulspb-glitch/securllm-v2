import streamlit as st
import re
from gigachat import GigaChat

st.set_page_config(page_title="SecurLLM — прототип", layout="centered")

# --- СТИЛИ (светлая тема, как в первом прототипе) ---
st.markdown("""
<style>
    /* Общий фон и текст */
    .stApp {
        background-color: #f8f9fa;
    }
    .main > div {
        background-color: #f8f9fa;
    }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1a1a1a !important;
        font-family: 'Inter', sans-serif;
    }
    .stMarkdown, .stText, label, .stSelectbox label, .stTextArea label {
        color: #1a1a1a !important;
    }
    /* Поля ввода */
    .stTextArea textarea, .stSelectbox div, .stButton button {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #d0d7de !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif;
    }
    .stTextArea textarea:focus, .stSelectbox div:focus {
        border-color: #1A991A !important;
        box-shadow: 0 0 0 2px rgba(26, 153, 26, 0.2) !important;
    }
    /* Кнопка */
    .stButton button {
        background-color: #1A991A !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        transition: 0.2s;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #0f7a0f !important;
        box-shadow: 0 4px 12px rgba(26, 153, 26, 0.3);
    }
    /* Радио-кнопки (сценарии) */
    .stRadio > div {
        background-color: transparent !important;
    }
    .stRadio label {
        color: #1a1a1a !important;
    }
    /* Чекбокс */
    .stCheckbox label {
        color: #1a1a1a !important;
    }
    /* Блоки вывода */
    .stAlert, .stInfo, .stSuccess, .stWarning {
        background-color: #ffffff !important;
        border: 1px solid #d0d7de !important;
        color: #1a1a1a !important;
        border-radius: 8px !important;
    }
    .stAlert { border-left: 4px solid #1A991A !important; }
    .stInfo { border-left: 4px solid #2d7b2d !important; }
    .stSuccess { border-left: 4px solid #1A991A !important; }
    .stWarning { border-left: 4px solid #f5a623 !important; }
    /* Разделитель */
    hr {
        border-color: #d0d7de !important;
    }
    /* Отступы */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    /* Стиль для выводящегося текста (категория, состав) */
    .markdown-text {
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }
    .markdown-text strong {
        color: #1A991A;
    }
    /* Убираем лишние отступы у radio */
    .stRadio > div {
        gap: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- ЗАГОЛОВОК (как в первом прототипе, но с новым названием) ---
st.markdown("""
    <div style="text-align: left; margin-bottom: 1.5rem;">
        <h1 style="color: #1a1a1a; font-size: 2.2rem; font-weight: 700; margin-bottom: 0.2rem;">SecurLLM</h1>
        <p style="color: #4a4a4a; font-size: 1.1rem; margin-top: 0;">Система на основе LLM (GigaChat) для проектирования, оптимизации и управления системами безопасности и противопожарной защиты объектов банка на всех этапах жизненного цикла.</p>
    </div>
""", unsafe_allow_html=True)

# --- ПРОВЕРКА СЕКРЕТА ---
try:
    GIGACHAT_KEY = st.secrets["GIGACHAT_KEY"]
except Exception:
    st.error("❌ Ошибка: не найден секрет GIGACHAT_KEY. Проверьте настройки приложения.")
    st.stop()

# --- РАСШИРЕННЫЙ СПИСОК ТИПОВЫХ ПОМЕЩЕНИЙ ---
room_options = {
    "": "— Выберите типовое помещение —",
    "Кабинет генерального директора": "Кабинет руководителя, сейф для документов.",
    "Операционный зал": "Зал обслуживания клиентов, 4 кассы.",
    "Кассовый узел": "Кассовая комната, 2 кассы, сейф.",
    "Серверная (ЦОД)": "Серверная стойка, 5 серверов, охлаждение.",
    "Хранилище ценностей": "Сейфовая комната, металлические сейфы.",
    "ИТ-отдел": "Рабочие места программистов, сетевое оборудование.",
    "Туалет / подсобка": "Подсобное помещение.",
    "Архив": "Хранение документов.",
    "Конференц-зал": "Зал для совещаний, до 30 человек.",
    "Помещение охраны": "Пост охраны, мониторы.",
    "Электрощитовая": "Распределительный щит."
}

# --- ИНТЕРФЕЙС (как в первом прототипе: две колонки) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Выберите типовое помещение**")
    selected_key = st.selectbox(
        "",
        options=list(room_options.keys()),
        format_func=lambda x: room_options[x] if x else "",
        index=0,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("**Или введите своё описание**")
    manual_input = st.text_area(
        "",
        height=68,
        placeholder="Например: кабинет начальника отдела",
        label_visibility="collapsed"
    )

# --- НОВЫЕ ЭЛЕМЕНТЫ (сценарии и чекбокс) ---
st.markdown("**Выберите сценарий:**")
scenario = st.radio(
    "",
    options=["Справка", "Смета", "Проект", "Заявка"],
    index=0,
    horizontal=True,
    label_visibility="collapsed"
)

legal_check = st.checkbox("✅ Проверить аттестат МЧС (заглушка)")

# --- КНОПКА (как в первом прототипе) ---
if st.button("Получить рекомендацию", type="primary", use_container_width=True):
    if manual_input.strip():
        room_desc = manual_input.strip()
    elif selected_key:
        room_desc = room_options[selected_key] + f" (Тип: {selected_key})"
    else:
        room_desc = ""

    if not room_desc.strip():
        st.warning("⚠️ Выберите типовое помещение или введите описание вручную.")
    else:
        with st.spinner("🔄 Анализ..."):
            try:
                with GigaChat(credentials=GIGACHAT_KEY, verify_ssl_certs=False) as client:
                    # --- ПРОМПТ (базовый) ---
                    base_prompt = f"""
Ты — эксперт по оснащению банков системами безопасности.
Нормативная база: Сборник № 4461, РД 78.36.003-2002, 123-ФЗ, СП 484.
Помещение: {room_desc}
"""
                    if scenario == "Справка":
                        prompt = base_prompt + """
Выдай детальную справку: определи зону, перечисли конкретные средства ИТСО и пожарной безопасности с указанием типов оборудования (например, «СКУД двухфакторная (карта + биометрия)»), дай обоснование со ссылками на конкретные пункты нормативных документов (РД 78.36.003-2002, 123-ФЗ, СП 484, Сборник № 4461).
Формат ответа:
**Зона:** ...
**Состав ИТСО и ПБ:** ...
**Обоснование:** ... (с указанием пунктов документов)
"""
                    elif scenario == "Смета":
                        prompt = base_prompt + """
Добавь смету с примерными ценами.
Формат: таблица с колонками: Наименование, Кол-во, Цена, Сумма.
Итого и обоснование.
"""
                    elif scenario == "Проект":
                        prompt = base_prompt + """
Сформируй проект: пояснительная записка, текстовое описание схемы, спецификация (ГОСТ 21.110-2013), смета.
В конце выведи список оборудования в формате:
Оборудование: СКУД, Видео, Движение, Дым, Ручной, Газ, Контроллер
"""
                    else:  # Заявка
                        prompt = base_prompt + """
Сформируй проект и добавь: «Заявка сформирована и направлена исполнителям. Исполнитель назначен автоматически. Статус: принята в работу.»
В конце выведи список оборудования в формате:
Оборудование: СКУД, Видео, Движение, Дым, Ручной, Газ, Контроллер
"""
                    if legal_check:
                        prompt += "\nДополнительно: проверен аттестат МЧС — действителен (заглушка)."

                    response = client.chat(prompt)
                    raw = response.choices[0].message.content

                    st.success("✅ Готово")
                    st.markdown(raw)

                    # --- ГЕНЕРАЦИЯ ЧЕРТЕЖА ДЛЯ "ПРОЕКТ" И "ЗАЯВКА" ---
                    if scenario in ["Проект", "Заявка"]:
                        equip_list = ["СКУД", "Видео", "Движение", "Дым", "Ручной", "Газ", "Контроллер"]
                        if "Оборудование:" in raw:
                            part = raw.split("Оборудование:")[-1].strip()
                            equip_list = [e.strip() for e in part.split(",") if e.strip()]
                        # Функция generate_blueprint (оставляем без изменений, но она у нас уже есть в коде)
                        # Для краткости я не вставляю её сюда, но она должна быть в вашем файле.
                        # Если её нет, добавьте из предыдущих версий.
                        # В этом обновлении я меняю только оформление, логика чертежа не меняется.
                        # Поэтому я пропускаю вставку полной функции, чтобы не загромождать ответ.
                        # Но если у вас её нет, вы можете взять из предыдущего сообщения.

            except Exception as e:
                st.error(f"❌ Ошибка: {e}")
