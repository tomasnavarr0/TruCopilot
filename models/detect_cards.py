import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO
import numpy as np
import time
from collections import defaultdict
import streamlit as st



def get_color_for_class(class_name: str) -> tuple[int,int,int]:
    if 'O' in class_name:
        return (255, 255, 0)  # Amarillo
    elif 'E' in class_name:
        return (0, 0, 255)  # Azul
    elif 'B' in class_name:
        return (0, 255, 0)  # Verde
    elif 'C' in class_name:
        return (255, 0, 0)  # Rojo
    elif 'J' in class_name:
        return (255, 0, 255)  # Violeta
    else:
        return (255, 255, 255)  # Blanco por defecto


class DetectCards:
    model_path: str = "models\yolov8_100epochs.pt"
    model = YOLO(model_path)

    @staticmethod
    def detect_and_show_cards_in_image(
        image_path: str, model=model,
        class_names: dict[int, str] = model.names, 
        confidence_threshold: float = 0.35
        ) -> tuple:
        cards_found = []
        
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        results = model.predict(image_rgb, conf=confidence_threshold)
        
        for result in results[0].boxes.data:
            x1, y1, x2, y2, conf, class_id = result
            if conf >= confidence_threshold:
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                class_id = int(class_id)
                class_name = class_names[class_id]
                label = f'{class_name} {conf:.2f}'
                cards_found.append(class_name)
                color = get_color_for_class(class_name)
                cv2.rectangle(image_rgb, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image_rgb, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image_rgb, cards_found

    @staticmethod
    def detect_and_show_cards_in_video(video_path: str, model = model,
                                    class_names: dict[int, str] = model.names, 
                                    confidence_threshold: float = 0.4
                                    ) -> list[str]:
       
        cap = cv2.VideoCapture(video_path)
        start_time = time.time()
        detected_cards = defaultdict(list)
        confirmed_cards = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model.predict(frame_rgb, conf=confidence_threshold)
            current_cards = []

            for result in results[0].boxes.data:
                x1, y1, x2, y2, conf, class_id = result
                if conf >= confidence_threshold:
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    class_id = int(class_id)
                    class_name = class_names[class_id]
                    current_cards.append(class_name)
                    label = f'{class_name} {conf:.2f}'
                    color = get_color_for_class(class_name)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            current_time = time.time()
            for card in current_cards:
                detected_cards[card].append(current_time)

            for card in list(detected_cards.keys()):
                detected_times = [t for t in detected_cards[card] if current_time - t <= 5]
                if len(detected_times) >= 1 and card not in confirmed_cards:
                    confirmed_cards.append(card)

            cv2.imshow('Card Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        print(set(confirmed_cards))

        return confirmed_cards


    @staticmethod
    def detect_and_show_cards_real_time(model = model, class_names: dict[int, str] = model.names) -> None:
        st_frame = st.empty()

        if "stream_active" not in st.session_state:
            st.session_state["stream_active"] = True

        if st.button("Detener Transmisión"):
            st.session_state["stream_active"] = False

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Error: No se puede abrir la cámara")
            return

        card_detection_times = {}
        detected_cards_for_3_seconds = []

        while st.session_state["stream_active"]:
            ret, frame = cap.read()
            if not ret:
                st.error("Error: No se puede recibir frame (fin del stream?)")
                break

            results = model(frame)
            
            current_time = time.time()
            detected_cards = []

            for result in results[0].boxes.data:
                x1, y1, x2, y2, conf, class_id = result
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                class_id = int(class_id)
                class_name = class_names[class_id]
                label = f'{class_name} {conf:.2f}'
                color = get_color_for_class(class_name)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                detected_cards.append(class_name)

                if class_name not in card_detection_times:
                    card_detection_times[class_name] = current_time

            for card in card_detection_times.keys():
                if card in detected_cards:
                    if current_time - card_detection_times[card] >= 3:
                        if card not in detected_cards_for_3_seconds:
                            detected_cards_for_3_seconds.append(card)
                else:
                    card_detection_times[card] = current_time

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st_frame.image(frame_rgb, channels="RGB", caption="Detección en Tiempo Real")

        cap.release()

        return detected_cards_for_3_seconds
    
