import json
import math
import datetime
from collections import defaultdict

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from skimage import color as skcolor
import colorsys


try:
    with open("cleaned_data.json", "r", encoding="utf-8") as f:
        CLEANED = json.load(f)
except Exception as e:
    CLEANED = {"colors": []}  

COLOR_TO_EMOTIONS = {}
for c in CLEANED.get("colors", []):
    name = (c.get("name") or "").strip().lower()
    if not name:
        continue
    COLOR_TO_EMOTIONS[name] = [emo.strip().lower() for emo in c.get("emotion", []) if emo]


REFERENCE_RGB = {
    "red": (220, 20, 60),
    "blue": (30, 144, 255),
    "yellow": (255, 215, 0),
    "green": (34, 139, 34),
    "orange": (255, 140, 0),
    "purple": (128, 0, 128),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "pink": (255, 105, 180),
    "gray": (128, 128, 128),
    "brown": (150, 75, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "lime": (50, 205, 50),
    "teal": (0, 128, 128),
    "navy": (0, 0, 128),
    "maroon": (128, 0, 0),
    "olive": (128, 128, 0),
    "violet": (143, 0, 255),
    "indigo": (75, 0, 130),
    "gold": (212, 175, 55),
    "silver": (192, 192, 192),
    "unknown": (200, 200, 200)
}

def rgb255_to_lab(rgb):
    arr = np.array([[list(rgb)]], dtype=np.uint8) / 255.0
    lab = skcolor.rgb2lab(arr)[0][0]
    return lab

REF_LABS = {name: rgb255_to_lab(rgb) for name, rgb in REFERENCE_RGB.items()}


def _nearest_named_color(centroid_rgb):
    """Return nearest color name from REFERENCE_RGB by Lab distance."""
    lab = rgb255_to_lab(tuple(int(round(v)) for v in centroid_rgb))
    best = None
    bestd = float("inf")
    for name, rlab in REF_LABS.items():
        d = np.linalg.norm(lab - rlab)
        if d < bestd:
            bestd = d
            best = name
  
    if bestd > 45:
        return "unknown", bestd
    return best, bestd


def _image_visual_stats(img):
    """Return avg_brightness (0..1), avg_saturation (0..1), contrast (0..1)."""
   
    small = img.copy().convert("RGB").resize((200, 200))
    arr = np.array(small) / 255.0  
   
    hsv = np.apply_along_axis(lambda rgb: colorsys.rgb_to_hsv(*rgb), 2, arr)
    sats = hsv[..., 1]
    vals = hsv[..., 2]
    avg_sat = float(np.mean(sats))
    avg_val = float(np.mean(vals))
   
    lab = skcolor.rgb2lab(arr)
    contrast = float(np.std(lab[..., 0]) / 100.0)
    return {"avg_brightness": avg_val, "avg_saturation": avg_sat, "contrast": contrast}


def detect_fuzzy_emotion(image_path, k=5):
  
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
   
    short = 200
    if max(w, h) > short:
        if w >= h:
            nw = short
            nh = int(h * (short / w))
        else:
            nh = short
            nw = int(w * (short / h))
        img_small = img.resize((max(1, nw), max(1, nh)))
    else:
        img_small = img.copy()

    
    arr = np.array(img_small).reshape(-1, 3).astype(float)  # 0..255
    
    n_clusters = min(k, max(2, arr.shape[0] // 50))
    try:
        km = KMeans(n_clusters=n_clusters, random_state=0, n_init=10)
        labels = km.fit_predict(arr)
        centroids = km.cluster_centers_
    except ValueError as e:
       
        print(f"KMeans clustering failed: {e}")
       
        centroids = np.array(arr[:n_clusters])
        labels = np.zeros(len(arr), dtype=int)

   
    counts = np.bincount(labels, minlength=len(centroids)).astype(float)
    weights = counts / counts.sum()

    palette = []
    for cen, wgt in zip(centroids, weights):
        name, dist = _nearest_named_color(cen)
        palette.append({"color": name, "weight": float(round(float(wgt), 6)), "centroid_rgb": [int(round(c)) for c in cen], "lab_distance": float(round(float(dist), 3))})

    emotion_scores = defaultdict(float)
    for p in palette:
        cname = p["color"]
        weight = p["weight"]
       
        if cname in COLOR_TO_EMOTIONS:
            for emo in COLOR_TO_EMOTIONS[cname]:
                emotion_scores[emo] += weight
        else:
            pass


    total = sum(emotion_scores.values())
    if total > 0:
        for k_ in list(emotion_scores.keys()):
            emotion_scores[k_] = float(emotion_scores[k_] / total)
    else:
        
        emotion_scores = {}

   
    pos = {"happiness", "joy", "optimism", "love", "peace", "purity", "energy", "enthusiasm"}
    neg = {"sadness", "grief", "anger", "fear", "death", "disgust"}
    neu = set()
    group_scores = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
    for emo, score in emotion_scores.items():
        if emo in pos:
            group_scores["positive"] += score
        elif emo in neg:
            group_scores["negative"] += score
        else:
            group_scores["neutral"] += score

    
    visual_stats = _image_visual_stats(img)

    
    confidence = max([p["weight"] for p in palette]) if palette else 0.0

    metadata = {
        "palette": palette,
        "emotion_space": emotion_scores,
        "emotion_groups": group_scores,
        "visual_stats": visual_stats,
        "confidence": float(round(confidence, 6)),
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "algorithm": "fuzzy-color-v1"
    }
    return metadata

