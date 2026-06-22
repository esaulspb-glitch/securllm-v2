import streamlit as st
import re
from gigachat import GigaChat

st.set_page_config(page_title="SecurLLM — прототип V2", layout="centered")

# --- ШАПКА ---
st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
        <i class="fas fa-building-columns" style="font-size: 28px; color: #21a038;"></i>
        <span style="font-size: 24px; font-weight: 600; color: #21a038;">СБЕР</span>
        <span style="font-size: 18px; color: #b0c9d4;">| SecurLLM V2</span>
    </div>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

st.title("🏦 Проектирование ИТСО и пожарной безопасности")
st.markdown("_Интеллектуальная генерация проектной документации на основе GigaChat_")

# --- ПРОВЕРКА СЕКРЕТА ---
try:
    GIGACHAT_KEY = st.secrets["GIGACHAT_KEY"]
except Exception:
    st.error("❌ Ошибка: не найден секрет GIGACHAT_KEY. Проверьте настройки приложения.")
    st.stop()

# --- РАСШИРЕННЫЙ СПИСОК ТИПОВЫХ ПОМЕЩЕНИЙ ---
room_options = {
    "": "— Выберите типовое помещение —",
    "Кабинет генерального директора": "Кабинет руководителя, сейф для документов, переговорная зона.",
    "Операционный зал": "Зал обслуживания клиентов, 4 кассы, работа с наличными и безналом.",
    "Кассовый узел": "Кассовая комната, 2 кассы, сейф для денег, работа с наличными.",
    "Серверная (ЦОД)": "Серверная стойка, 5 серверов, система охлаждения, круглосуточный доступ.",
    "Хранилище ценностей": "Сейфовая комната, металлические сейфы, система климат-контроля.",
    "ИТ-отдел": "Рабочие места программистов, сетевое оборудование, доступ в серверную.",
    "Туалет / подсобка": "Подсобное помещение, минимальная ценность активов.",
    "Архив": "Хранение документов, бумажные носители, ограниченный доступ.",
    "Конференц-зал": "Помещение для совещаний, до 30 человек, проектор.",
    "Помещение охраны": "Пост охраны, мониторы, пульт управления.",
    "Электрощитовая": "Распределительный щит, высокое напряжение."
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
        placeholder="Например: переговорная комната на 10 человек",
        label_visibility="collapsed"
    )

# --- ВЫБОР СЦЕНАРИЯ ---
st.markdown("**Выберите сценарий выдачи результата:**")
scenario = st.radio(
    "",
    options=["Справка", "Смета", "Проект", "Заявка"],
    index=0,
    horizontal=True,
    label_visibility="collapsed"
)

# --- ЮРИДИЧЕСКИЙ ФИЛЬТР (заглушка) ---
legal_check = st.checkbox("✅ Проверить аттестат МЧС у проектировщика (заглушка)")

# --- ФУНКЦИЯ ГЕНЕРАЦИИ ПРОФЕССИОНАЛЬНОГО ЧЕРТЕЖА В SVG ---
def generate_blueprint(room_desc, equipment_list, width_m=6.0, height_m=8.0):
    """
    Генерирует SVG-чертёж помещения с расстановкой оборудования по нормативным обозначениям.
    Размеры по умолчанию (6×8 м) используются для демонстрации.
    В промышленной версии размеры загружаются из BIM/1С.
    """
    # Масштаб: 1 м = 40 пикселей
    scale = 40
    # Приводим размеры к целым для range
    w_int = int(round(width_m))
    h_int = int(round(height_m))
    
    svg_w = w_int * scale + 120
    svg_h = h_int * scale + 160

    # Отступы для чертежа
    margin = 50
    room_x = margin
    room_y = margin
    room_w = w_int * scale
    room_h = h_int * scale

    # Цвета
    bg = "#0f1a1a"
    wall = "#4ade80"
    door = "#f59e0b"
    window = "#60a5fa"
    text = "#e0e9ee"
    grid = "#1e2a2a"

    svg = f'<svg width="{svg_w}" height="{svg_h}" xmlns="http://www.w3.org/2000/svg" style="background-color: {bg}; border-radius: 12px; font-family: Inter, sans-serif;">'

    # --- Сетка (для масштаба) ---
    for x in range(0, w_int + 1):
        x_px = room_x + x * scale
        svg += f'<line x1="{x_px}" y1="{room_y}" x2="{x_px}" y2="{room_y + room_h}" stroke="{grid}" stroke-width="0.5" />'
    for y in range(0, h_int + 1):
        y_px = room_y + y * scale
        svg += f'<line x1="{room_x}" y1="{y_px}" x2="{room_x + room_w}" y2="{y_px}" stroke="{grid}" stroke-width="0.5" />'

    # --- Стены ---
    svg += f'<rect x="{room_x}" y="{room_y}" width="{room_w}" height="{room_h}" fill="none" stroke="{wall}" stroke-width="2" />'

    # --- Подпись помещения ---
    svg += f'<text x="{room_x + 10}" y="{room_y + 20}" fill="{text}" font-size="12" font-weight="bold">{room_desc[:40]}</text>'

    # --- Дверь (входная, слева снизу) ---
    door_x = room_x + 10
    door_y = room_y + room_h - 30
    svg += f'<rect x="{door_x}" y="{door_y}" width="30" height="20" fill="{door}" rx="2" />'
    svg += f'<text x="{door_x + 5}" y="{door_y + 25}" fill="{text}" font-size="8">Дверь</text>'

    # --- Окно (справа сверху) ---
    win_x = room_x + room_w - 50
    win_y = room_y + 20
    svg += f'<rect x="{win_x}" y="{win_y}" width="40" height="15" fill="{window}" rx="2" />'
    svg += f'<text x="{win_x + 5}" y="{win_y + 28}" fill="{text}" font-size="8">Окно</text>'

    # --- Размещение оборудования (по нормативным символам) ---
    equipment_positions = {
        "СКУД": {"x": door_x + 15, "y": door_y - 20, "symbol": "C"},
        "Видео": {"x": room_x + room_w - 30, "y": room_y + 30, "symbol": "V"},
        "Движение": {"x": room_x + room_w // 2, "y": room_y + 20, "symbol": "Д"},
        "Дым": {"x": room_x + 40, "y": room_y + 30, "symbol": "И"},
        "Ручной": {"x": room_x + room_w - 40, "y": room_y + room_h - 30, "symbol": "Р"},
        "Газ": {"x": room_x + room_w // 2, "y": room_y + room_h // 2, "symbol": "Г"},
        "Контроллер": {"x": room_x + 20, "y": room_y + 60, "symbol": "K"},
    }

    drawn = []
    for eq in equipment_list:
        eq_clean = eq.strip()
        if eq_clean in equipment_positions:
            pos = equipment_positions[eq_clean]
            if eq_clean not in drawn:
                x = pos["x"]
                y = pos["y"]
                sym = pos["symbol"]
                if eq_clean == "СКУД":
                    svg += f'<rect x="{x-10}" y="{y-10}" width="20" height="15" fill="#3b82f6" rx="2" />'
                    svg += f'<text x="{x-6}" y="{y+2}" fill="#fff" font-size="8">{sym}</text>'
                elif eq_clean == "Видео":
                    svg += f'<circle cx="{x}" cy="{y}" r="10" fill="#ef4444" />'
                    svg += f'<circle cx="{x}" cy="{y}" r="4" fill="#fff" />'
                    svg += f'<text x="{x-6}" y="{y+4}" fill="#000" font-size="6">{sym}</text>'
                elif eq_clean == "Движение":
                    svg += f'<circle cx="{x}" cy="{y}" r="8" fill="#facc15" />'
                    svg += f'<text x="{x-6}" y="{y+3}" fill="#000" font-size="8">{sym}</text>'
                elif eq_clean == "Дым":
                    svg += f'<circle cx="{x}" cy="{y}" r="8" fill="#a855f7" />'
                    svg += f'<text x="{x-4}" y="{y+3}" fill="#fff" font-size="8">{sym}</text>'
                elif eq_clean == "Ручной":
                    svg += f'<rect x="{x-6}" y="{y-10}" width="12" height="15" fill="#ec4899" rx="2" />'
                    svg += f'<text x="{x-4}" y="{y+2}" fill="#fff" font-size="8">{sym}</text>'
                elif eq_clean == "Газ":
                    svg += f'<rect x="{x-12}" y="{y-8}" width="24" height="16" fill="#06b6d4" rx="2" />'
                    svg += f'<text x="{x-6}" y="{y+3}" fill="#fff" font-size="8">{sym}</text>'
                elif eq_clean == "Контроллер":
                    svg += f'<rect x="{x-12}" y="{y-8}" width="24" height="16" fill="#8b5cf6" rx="2" />'
                    svg += f'<text x="{x-6}" y="{y+3}" fill="#fff" font-size="8">{sym}</text>'
                
                svg += f'<text x="{x}" y="{y + 25}" fill="{text}" font-size="7">{eq_clean[:3]}{drawn.count(eq_clean)+1}</text>'
                drawn.append(eq_clean)

    # --- Легенда ---
    legend_x = margin
    legend_y = room_y + room_h + 30
    svg += f'<text x="{legend_x}" y="{legend_y}" fill="{text}" font-size="12" font-weight="bold">Условные обозначения:</text>'
    legend_items = [
        ("C", "Считыватель СКУД", "#3b82f6"),
        ("K", "Контроллер СКУД", "#8b5cf6"),
        ("V", "Видеокамера", "#ef4444"),
        ("Д", "Датчик движения", "#facc15"),
        ("И", "Дымовой извещатель", "#a855f7"),
        ("Р", "Ручной извещатель", "#ec4899"),
        ("Г", "Газовое пожаротушение", "#06b6d4"),
    ]
    for i, (code, name, color) in enumerate(legend_items):
        x = legend_x + 30 + i * 100
        svg += f'<rect x="{x}" y="{legend_y + 10}" width="16" height="12" fill="{color}" rx="2" />'
        svg += f'<text x="{x + 20}" y="{legend_y + 22}" fill="{text}" font-size="8">{code} — {name}</text>'

    # --- Масштабная линейка ---
    scale_x = room_x + room_w - 80
    scale_y = room_y + room_h + 10
    svg += f'<line x1="{scale_x}" y1="{scale_y}" x2="{scale_x + 40}" y2="{scale_y}" stroke="{text}" stroke-width="1" />'
    svg += f'<text x="{scale_x}" y="{scale_y + 12}" fill="{text}" font-size="7">1 м</text>'

    svg += '</svg>'
    return svg

# --- КНОПКА ---
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
        with st.spinner("🔄 GigaChat анализирует..."):
            try:
                with GigaChat(credentials=GIGACHAT_KEY, verify_ssl_certs=False) as client:
                    # --- ФОРМИРОВАНИЕ ПРОМПТА ---
                    base_prompt = """
Ты — эксперт по проектированию систем безопасности банков.
Нормативная база (приоритет): внутренний «Сборник стандартов по комплексной безопасности № 4461», РД 78.36.003-2002, Р 102-2024 (Росгвардия), ТТ 78.36.003-99 (ЦБ РФ), ГОСТ Р 51558, 123-ФЗ, СП 484.1311500.2020, ВНП 001-01/Банк России, ГОСТ Р 21.110-2013.

Классификация зон:
- Зона 1 (клиентская/общедоступная): операционные залы, вестибюли, коридоры.
  Требования: видеонаблюдение, дымовые извещатели, стандартная вентиляция.
- Зона 2 (офисная/ограниченного доступа): кабинеты руководителей, бухгалтерия, ИТ-отделы.
  Требования: СКУД (карты), тревожная кнопка, видеонаблюдение, датчики открытия/движения, дымовые и ручные извещатели, кондиционирование.
- Зона 3A (ЦОД/серверная): серверные, коммутационные.
  Требования: СКУД (двухфакторная: карта+PIN), многорубежная сигнализация, видео с высоким разрешением, дымовые извещатели, газовое пожаротушение, климат-контроль.
- Зона 3B (хранилище ценностей): сейфовые комнаты, депозитарии.
  Требования: СКУД (карта+биометрия), многорубежная сигнализация (вибрация, акустика), видео с распознаванием лиц, газовое пожаротушение, вывод на Росгвардию.
- Зона 3C (кассовый узел): операционные кассы, кассовые комнаты.
  Требования: СКУД (карта+PIN), сигнализация, видео над каждым рабочим местом, дымовые и ручные извещатели.
- Зона 3D (служба безопасности): помещения охраны, пультовые.
  Требования: СКУД (двухфакторная), многорубежная сигнализация, видео с аналитикой, дымовые извещатели, резервирование питания.

Помещение: {room_desc}
"""

                    scenario_instruction = ""
                    if scenario == "Справка":
                        scenario_instruction = """
Выдай краткую справку: определи зону, перечисли обязательные системы и оборудование, дай обоснование (ссылки на нормативные документы).
Формат ответа:
**Зона:** ...
**Состав ИТСО и пожарной безопасности:** ...
**Обоснование:** ...
"""
                    elif scenario == "Смета":
                        scenario_instruction = """
Выдай справку и добавь таблицу с примерными ценами на оборудование и монтаж (по внутренним расценкам).
Формат ответа:
**Зона:** ...
**Состав ИТСО и пожарной безопасности:** ...
**Смета (примерные цены):**
| Наименование | Кол-во | Цена за ед., ₽ | Сумма, ₽ |
|--------------|--------|----------------|----------|
| ...          | ...    | ...            | ...      |
**Итого:** ... ₽
**Обоснование:** ...
"""
                    elif scenario == "Проект":
                        scenario_instruction = """
Сформируй полный пакет проектной документации в соответствии с РД 78.36.003-2002 и ГОСТ Р 21.110-2013.

1. Пояснительная записка:
   Объект: [помещение]
   Нормативная база: Сборник № 4461, РД 78.36.003-2002, 123-ФЗ, СП 484.1311500.2020, ГОСТ Р 21.110-2013.

2. Визуальная схема расстановки оборудования (текстовое описание):
   Опиши, где и какое оборудование устанавливается. Используй условные обозначения:
   - СКУД: считыватель, контроллер.
   - ОС: датчик движения.
   - Видео: камера.
   - ПБ: дымовой извещатель, ручной извещатель, модуль газового пожаротушения.

3. Спецификация оборудования и материалов (по ГОСТ 21.110-2013):
   Таблица с колонками: Поз., Наименование и техническая характеристика, Тип, марка, Код, Поставщик, Ед. изм., Кол-во, Масса ед., Примечание.

4. Смета (на основе спецификации):
   Таблица: Наименование работ, Ед. изм., Кол-во, Стоимость ед., Сумма.
   Добавить накладные расходы (15% от прямых затрат).

После текстового описания схемы выведи список оборудования в формате:
Оборудование: [список через запятую: СКУД, Видео, Движение, Дым, Ручной, Газ, Контроллер]
"""
                    elif scenario == "Заявка":
                        scenario_instruction = """
Выдай полный проект и добавь текст: "Заявка сформирована и направлена исполнителям. Исполнитель: назначен автоматически. Статус: принята в работу."

1. Пояснительная записка...
2. Визуальная схема...
3. Спецификация...
4. Смета...
5. Заявка: Заявка сформирована и направлена исполнителям. Исполнитель: назначен автоматически. Статус: принята в работу.
После текстового описания схемы выведи список оборудования в формате:
Оборудование: [список через запятую: СКУД, Видео, Движение, Дым, Ручной, Газ, Контроллер]
"""

                    legal_text = ""
                    if legal_check:
                        legal_text = """
Дополнительно: проверен аттестат МЧС у проектировщика — аттестат действителен (заглушка).
"""

                    full_prompt = base_prompt + scenario_instruction + legal_text

                    response = client.chat(full_prompt)
                    raw = response.choices[0].message.content

                    st.success("✅ Документация готова")
                    st.markdown(raw)

                    # --- ГЕНЕРАЦИЯ ЧЕРТЕЖА ДЛЯ СЦЕНАРИЕВ "ПРОЕКТ" И "ЗАЯВКА" ---
                    if scenario in ["Проект", "Заявка"]:
                        # Парсим список оборудования
                        equipment_list = []
                        if "Оборудование:" in raw:
                            equip_part = raw.split("Оборудование:")[-1].strip()
                            equipment_list = [e.strip() for e in equip_part.split(",") if e.strip()]
                        
                        if not equipment_list:
                            equipment_list = ["СКУД", "Видео", "Движение", "Дым", "Ручной", "Газ", "Контроллер"]
                        
                        # Генерируем чертёж с условными размерами (6×8 м)
                        # В промышленной версии размеры будут загружаться из BIM/1С
                        svg = generate_blueprint(room_desc, equipment_list)
                        st.markdown("### 📐 План расстановки оборудования")
                        st.markdown("_*Размеры помещения указаны условно (6×8 м). В промышленной версии данные загружаются из BIM/1С._")
                        st.markdown(svg, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Ошибка при обращении к GigaChat: {e}")
