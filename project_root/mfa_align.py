def run_mfa_alignment():
    subprocess.run([
        "mfa", "align",
        str(CORPUS_DIR),
        str(DICTIONARY_PATH),
        str(ACOUSTIC_MODEL_DIR),
        str(OUTPUT_DIR),
        "--clean", "--verbose"
    ], check=True)
def parse_textgrid_to_ass(textgrid_path, ass_path):
    tg = TextGrid.fromFile(textgrid_path)
    word_tier = next((tier for tier in tg.tiers if tier.name.lower() in ["word", "words"]), None)
    if not word_tier:
        raise ValueError("Нет слоя 'word' в TextGrid.")

    subs = pysubs2.SSAFile()
    style = pysubs2.SSAStyle()
    style.name = "TikTokStyle"
    style.fontname = "Anton"
    style.fontsize = 28
    style.primarycolor = pysubs2.Color(255, 128, 0)
    style.outlinecolor = pysubs2.Color(0, 0, 0)
    style.bold = True
    style.shadow = 0
    style.outline = 1
    style.alignment = 2
    subs.styles[style.name] = style

    for interval in word_tier.intervals:
        word = interval.mark.strip()
        if not word:
            continue
        start = max(interval.minTime - 0.5, 0)
        end = interval.maxTime

        text = f"{{\\an5}}{word}"
        event = pysubs2.SSAEvent(
            start=int(start * 1000),
            end=int(end * 1000),
            text=text,
            style=style.name
        )
        subs.append(event)

    subs.save(ass_path)
