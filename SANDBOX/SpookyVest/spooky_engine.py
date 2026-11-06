import cv2
import numpy as np
from uniface import SCRFD
from PIL import Image
import io

class SpookyEngine:
    def __init__(self):
        self.detector = SCRFD()

    def process_image(self, image_bytes: bytes, mask_path: str, intensity: float = 0.7):
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_h, img_w, _ = img.shape

        # 1. Rileva viso (Bounding Box)
        faces = self.detector.detect(img)
        if not faces:
            return None, "Nessun viso rilevato."

        # Prendi il viso più grande
        face_box = max(faces, key=lambda f: (f[2]-f[0])*(f[3]-f[1]))
        x1, y1, x2, y2 = face_box[:4].astype(int)
        face_w = x2 - x1
        face_h = y2 - y1

        # 2. Carica maschera
        mask = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)
        if mask is None:
            return None, "Maschera non trovata."
        
        mask_h, mask_w = mask.shape[:2]

        # 3. Scala e Posizione
        # Vogliamo che la maschera sia leggermente più grande del viso
        scale = (face_w / mask_w) * 1.15 
        new_w = int(mask_w * scale)
        new_h = int(mask_h * scale)
        
        mask_resized = cv2.resize(mask, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Centratura sul viso, alzata di un 10% per coprire la fronte
        pos_x = int(x1 + (face_w - new_w) / 2)
        pos_y = int(y1 + (face_h - new_h) / 2 - face_h * 0.1)

        # 4. Crea tela e incolla
        mask_canvas = np.zeros((img_h, img_w, 4), dtype=np.uint8)
        
        y_start, y_end = max(0, pos_y), min(img_h, pos_y + new_h)
        x_start, x_end = max(0, pos_x), min(img_w, pos_x + new_w)

        mask_y_start, mask_y_end = max(0, -pos_y), max(0, -pos_y) + (y_end - y_start)
        mask_x_start, mask_x_end = max(0, -pos_x), max(0, -pos_x) + (x_end - x_start)

        mask_canvas[y_start:y_end, x_start:x_end] = mask_resized[mask_y_start:mask_y_end, mask_x_start:mask_x_end]

        # 5. FEATHERING (La magia anti-adesivo)
        alpha = mask_canvas[:, :, 3].astype(float) / 255.0
        # Sfumiamo i bordi dell'alpha per fonderla con la pelle
        alpha_blurred = cv2.GaussianBlur(alpha, (21, 21), 0)
        alpha_3d = cv2.merge([alpha_blurred, alpha_blurred, alpha_blurred])

        # 6. Blending
        img_float = img.astype(float)
        mask_float = mask_canvas[:, :, :3].astype(float)
        
        # Applichiamo l'intensità dello slider (0 = originale, 1 = maschera piena)
        alpha_final = alpha_3d * intensity

        blended = (mask_float * alpha_final) + (img_float * (1.0 - alpha_final))
        final_img = blended.astype(np.uint8)

        # 7. Output
        pil_result = Image.fromarray(cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB))
        out_bytes = io.BytesIO()
        pil_result.save(out_bytes, format='JPEG', quality=95)
        return out_bytes.getvalue(), None
