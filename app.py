import streamlit as st
import re
from gigachat import GigaChat

st.set_page_config(page_title="SecurLLM — прототип", layout="centered")

# --- ШАПКА СБЕРА ---
st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
        <i class="fas fa-building-columns" style="font-size: 28px; color: #1A991A;"></i>
        <span style="font-size: 24px; font-weight: 700; color: #1A991A;">Сбер</span>
        <span style="font-size: 18px; color: #333F48;">| SecurLLM</span>
    </div>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

st.title("🏦 Методология оснащения ИТСО и пожарной безопасности")
st.markdown("""
    *Работающий прототип методологии SecurLLM — интеллектуального подхода к оснащению объектов банка 
    системами безопасности на основе LLM, нормативной базы и экономического анализа.*
""")

# --- ПРОВЕРКА СЕКРЕТА ---
try:
    GIGACHAT_KEY = st.secrets["GIGACHAT_KEY"]
except Exception:
    st.error("❌ Ошибка: не найден секрет GIGACHAT_KEY. Проверьте настройки приложения.")
    st.stop()

# --- СПИСОК ТИПОВЫХ ПОМЕЩЕНИЙ ---
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

# --- ИНТЕРФЕЙС ---
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

# --- ВЫБОР СЦЕНАРИЯ ---
st.markdown("**Выберите сценарий:**")
scenario = st.radio(
    "",
    options=["Справка", "Смета", "Проект", "Заявка"],
    index=0,
    horizontal=True,
    label_visibility="collapsed"
)

# --- ЮРИДИЧЕСКИЙ ФИЛЬТР (заглушка) ---
legal_check = st.checkbox("✅ Проверить аттестат МЧС (заглушка)")

# --- ФУНКЦИЯ ГЕНЕРАЦИИ ПРОФЕССИОНАЛЬНОГО ЧЕРТЕЖА ---
def generate_blueprint(room_desc, equipment_list):
    # Размеры условные для демонстрации
    w_int, h_int = 6, 8
    scale = 40
    svg_w = w_int * scale + 120
    svg_h = h_int * scale + 180

    margin = 50
    room_x, room_y = margin, margin
    room_w = w_int * scale
    room_h = h_int * scale

    # Цвета (светлый фон)
    bg = "#ffffff"
    wall = "#333333"
    door = "#e67e22"
    window = "#3498db"
    text = "#333333"
    grid = "#e0e0e0"

    svg = f'<svg width="{svg_w}" height="{svg_h}" xmlns="http://www.w3.org/2000/svg" style="background-color: {bg}; border-radius: 8px; font-family: Inter, sans-serif; border: 1px solid #ccc;">'

    # Сетка
    for x in range(w_int + 1):
        x_px = room_x + x * scale
        svg += f'<line x1="{x_px}" y1="{room_y}" x2="{x_px}" y2="{room_y + room_h}" stroke="{grid}" stroke-width="0.5" />'
    for y in range(h_int + 1):
        y_px = room_y + y * scale
        svg += f'<line x1="{room_x}" y1="{y_px}" x2="{room_x + room_w}" y2="{y_px}" stroke="{grid}" stroke-width="0.5" />'

    # Стены
    svg += f'<rect x="{room_x}" y="{room_y}" width="{room_w}" height="{room_h}" fill="none" stroke="{wall}" stroke-width="2" />'

    # Подпись
    svg += f'<text x="{room_x + 10}" y="{room_y + 20}" fill="{text}" font-size="12" font-weight="bold">{room_desc[:30]}</text>'

    # Дверь
    door_x = room_x + 10
    door_y = room_y + room_h - 30
    svg += f'<rect x="{door_x}" y="{door_y}" width="30" height="20" fill="{door}" rx="2" />'
    svg += f'<text x="{door_x + 5}" y="{door_y + 25}" fill="{text}" font-size="8">Дверь</text>'

    # Окно
    win_x = room_x + room_w - 50
    win_y = room_y + 20
    svg += f'<rect x="{win_x}" y="{win_y}" width="40" height="15" fill="{window}" rx="2" />'
    svg += f'<text x="{win_x + 5}" y="{win_y + 28}" fill="{text}" font-size="8">Окно</text>'

    # Расстановка оборудования (условно, но по правилам)
    positions = {
        "СКУД": {"x": door_x + 15, "y": door_y - 20, "sym": "C", "color": "#2980b9"},
        "Видео": {"x": room_x + room_w - 30, "y": room_y + 30, "sym": "V", "color": "#e74c3c"},
        "Движение": {"x": room_x + room_w // 2, "y": room_y + 20, "sym": "Д", "color": "#f39c12"},
        "Дым": {"x": room_x + 40, "y": room_y + 30, "sym": "И", "color": "#8e44ad"},
        "Ручной": {"x": room_x + room_w - 40, "y": room_y + room_h - 30, "sym": "Р", "color": "#e84393"},
        "Газ": {"x": room_x + room_w // 2, "y": room_y + room_h // 2, "sym": "Г", "color": "#00b894"},
        "Контроллер": {"x": room_x + 20, "y": room_y + 60, "sym": "K", "color": "#6c5ce7"},
    }

    for eq in equipment_list:
        eq_clean = eq.strip()
        if eq_clean in positions:
            pos = positions[eq_clean]
            x, y, sym, color = pos["x"], pos["y"], pos["sym"], pos["color"]
            if eq_clean in ["СКУД", "Контроллер", "Ручной", "Газ"]:
                svg += f'<rect x="{x-10}" y="{y-8}" width="20" height="16" fill="{color}" rx="2" />'
                svg += f'<text x="{x-5}" y="{y+3}" fill="#fff" font-size="8" font-weight="bold">{sym}</text>'
            elif eq_clean in ["Видео", "Движение", "Дым"]:
                svg += f'<circle cx="{x}" cy="{y}" r="10" fill="{color}" />'
                svg += f'<text x="{x-4}" y="{y+3}" fill="#fff" font-size="8" font-weight="bold">{sym}</text>'

    # Легенда
    legend_x = margin
    legend_y = room_y + room_h + 40
    svg += f'<text x="{legend_x}" y="{legend_y}" fill="{text}" font-size="12" font-weight="bold">Условные обозначения:</text>'
    items = [
        ("C", "Считыватель", "#2980b9"),
        ("K", "Контроллер", "#6c5ce7"),
        ("V", "Камера", "#e74c3c"),
        ("Д", "Движение", "#f39c12"),
        ("И", "Дымовой", "#8e44ad"),
        ("Р", "Ручной", "#e84393"),
        ("Г", "Газ", "#00b894"),
    ]
    for i, (code, name, color) in enumerate(items):
        x = legend_x + 30 + i * 90
        svg += f'<rect x="{x}" y="{legend_y + 10}" width="16" height="12" fill="{color}" rx="2" />'
        svg += f'<text x="{x + 20}" y="{legend_y + 22}" fill="{text}" font-size="8">{code} — {name}</text>'

    # Масштаб
    scale_x = room_x + room_w - 70
    scale_y = room_y + room_h + 15
    svg += f'<line x1="{scale_x}" y1="{scale_y}" x2="{scale_x + 40}" y2="{scale_y}" stroke="#333" stroke-width="1" />'
    svg += f'<text x="{scale_x}" y="{scale_y + 12}" fill="#333" font-size="7">1 м</text>'

    svg += '</svg>'
    return svg

# --- КНОПКА ---
if st.button("Получить результат", type="primary", use_container_width=True):
    if manual_input.strip():
        room_desc = manual_input.strip()
    elif selected_key:
        room_desc = room_options[selected_key] + f" (Тип: {selected_key})"
    else:
        room_desc = ""

    if not room_desc.strip():
        st.warning("⚠️ Выберите типовое помещение или введите описание.")
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
Выдай краткую справку: зона, состав ИТСО и ПБ, обоснование по нормативам.
Формат:
**Зона:** ...
**Состав:** ...
**Обоснование:** ...
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
                        svg = generate_blueprint(room_desc, equip_list)
                        st.markdown("### 📐 План расстановки оборудования")
                        st.markdown("_*Размеры условные. В реальной системе — из BIM/1С._")
                        st.markdown(svg, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Ошибка: {e}")
