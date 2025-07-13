def convert_srt_to_ass_tiktok_style(srt_path: str, ass_output_path: str) -> None:
    """Конвертация srt в ass с улучшенными эффектами"""
    import pysubs2
    import random
    
    # Загружаем SRT файл
    subs = pysubs2.load(srt_path)
    
    # Создаем новые стили
    new_subs = pysubs2.SSAFile()
    
    # Основной стиль - желтый с тенью
    main_style = pysubs2.SSAStyle()
    main_style.fontname = "Comic Sans MS"  # Круглый рисованный шрифт
    main_style.fontsize = 32
    main_style.primarycolor = pysubs2.Color(255, 255, 0)  # Желтый
    main_style.outlinecolor = pysubs2.Color(0, 0, 0)      # Черная окантовка
    main_style.backcolor = pysubs2.Color(0, 0, 0)         # Фон (для тени)
    main_style.bold = True
    main_style.shadow = 2  # Тень
    main_style.outline = 1  # Окантовка
    main_style.alignment = 2  # По центру
    new_subs.styles["MainStyle"] = main_style
    
    # Альтернативный стиль с другим эффектом
    alt_style = pysubs2.SSAStyle()
    alt_style.fontname = "Comic Sans MS"
    alt_style.fontsize = 32
    alt_style.primarycolor = pysubs2.Color(255, 255, 0)  # Желтый
    alt_style.outlinecolor = pysubs2.Color(0, 0, 0)      # Черная окантовка
    alt_style.backcolor = pysubs2.Color(0, 0, 0)         # Фон
    alt_style.bold = True
    alt_style.shadow = 3  # Больше тени
    alt_style.outline = 2  # Больше окантовки
    alt_style.alignment = 2  # По центру
    new_subs.styles["AltStyle"] = alt_style
    
    # Эффекты появления
    effects = [
        "\\fad(300,0)\\fscx120\\fscy120\\t(0,300,\\fscx100\\fscy100)",  # Плавное появление с увеличением
        "\\fad(400,0)\\move(0,20,0,0,0,300)",  # Появление снизу
        "\\fad(350,0)\\frz0\\t(0,350,\\frz360)",  # Появление с поворотом
        "\\fad(300,0)\\fscx80\\fscy80\\t(0,300,\\fscx100\\fscy100)",  # Появление с уменьшением
        "\\fad(400,0)\\blur3\\t(0,400,\\blur0)",  # Появление с размытием
    ]
    
    # Обрабатываем каждую строку
    for i, line in enumerate(subs):
        if not line.text.strip():
            continue
            
        # Выбираем случайный эффект
        effect = random.choice(effects)
        
        # Выбираем стиль (чередуем для разнообразия)
        style_name = "MainStyle" if i % 2 == 0 else "AltStyle"
        
        # Исправлено: управляющие коды и эффекты внутри одних фигурных скобок
        text = f"{{\\an5{effect}}}{line.text.strip()}"
        
        # Создаем новое событие
        new_event = pysubs2.SSAEvent(
            start=line.start,
            end=line.end,
            text=text,
            style=style_name
        )
        new_subs.append(new_event)
    
    new_subs.save(ass_output_path)
    print(f"✅ ASS файл с улучшенными эффектами создан: {ass_output_path}")
    print(f"🎨 Применены эффекты: тень, желтый цвет, круглый шрифт, анимации появления")
