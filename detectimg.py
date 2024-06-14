import cv2
import os
import random
import numpy as np
from ultralytics import YOLO
from ftp import ftp_func
from sys import argv
from request import send_post_request  # POST isteği fonksiyonunu içe aktarın

# Predefined variables
confidence_score = 0.75
text_color_b = (0, 0, 0)  # black
text_color_w = (255, 255, 255)  # white
font = cv2.FONT_HERSHEY_SIMPLEX

# Load model
model = YOLO("yolo8best.pt")  # Model dosyasının yolu
labels = model.names
colors = [[random.randint(0, 255) for _ in range(3)] for _ in labels]

# Input and output directories
input_dir = "test"
output_dir = "results"
os.makedirs(output_dir, exist_ok=True)

api_url = "http://145.239.134.25:5000/insert_weed_data"  # Gerçek API URL'nizi buraya ekleyin

# Process each image in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith((".jpg", ".jpeg", ".png")):
        # Dosya ismindeki koordinatları ayrıştırma
        name_part = os.path.splitext(filename)[0]
        latitude, longitude = name_part.split('-')

        image_path = os.path.join(input_dir, filename)
        image = cv2.imread(image_path)

        results = model(image, verbose=False)[0]
        boxes = np.array(results.boxes.data.tolist())
        percentages = []

        for box in boxes:
            x1, y1, x2, y2, score, class_id = box
            x1, y1, x2, y2, class_id = int(x1), int(y1), int(x2), int(y2), int(class_id)

            if score > confidence_score:
                box_color = colors[class_id]
                cv2.rectangle(image, (x1, y1), (x2, y2), box_color, 2)

                score_percentage = score * 100
                class_name = results.names[class_id]
                text = f"{class_name}: %{score_percentage:.2f}"
                percentages.append(score_percentage)

                # Metin konumunu ayarlama
                text_loc = (x1, y2 + 20)
                if y2 + 20 > image.shape[0]:  # Alt sınır kontrolü
                    text_loc = (x1, y1 - 10)

                labelSize, baseLine = cv2.getTextSize(text, font, 1, 1)
                top_left = (x1, text_loc[1] - labelSize[1] - baseLine)
                bottom_right = (x1 + labelSize[0], text_loc[1] + baseLine)

                cv2.rectangle(image, top_left, bottom_right, box_color, cv2.FILLED)
                cv2.putText(image, text, text_loc, font, 1, text_color_w, thickness=1)

        if percentages:
            avg_percentage = sum(percentages) / len(percentages)
        else:
            avg_percentage = 0

        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, image)
        print(f"[INFO] Processed {filename} with avg_percentage: {avg_percentage}")

        # Gönderilecek veri
        data = {
            "fb_local_id": argv[1],
            "latitude": latitude,
            "longitude": longitude,
            "image_path": filename,
            "percentage": avg_percentage  # Her görselin ortalama yüzde skoru
        }

        print(data)

        # POST isteği gönderme
        send_post_request(api_url, data)

# FTP işlemiyle sonuç dosyasındaki görselleri gönder
ftp_func(argv[1])

print("[INFO].. All images have been processed and saved in the results folder")
