import cv2
import numpy as np
import os
from PIL import Image

video_path = r"C:\Users\Леонид\Downloads\ОТВЕТЫ ОГЭ (3).mp4"
output_folder = r"C:\Users\Леонид\Desktop\frames_with_alpha"
os.makedirs(output_folder, exist_ok=True)

cap = cv2.VideoCapture(video_path)
frame_num = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    alpha = cv2.bitwise_not(mask)

    b, g, r = cv2.split(frame)
    rgba = cv2.merge((r, g, b, alpha))  # PIL использует RGB-порядок

    out_path = f"{output_folder}/frame_{frame_num:04d}.png"

    try:
        im = Image.fromarray(rgba)
        im.save(out_path)
        print(f"✅ Сохранён: {out_path}")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

    frame_num += 1

cap.release()
print("Готово!")
