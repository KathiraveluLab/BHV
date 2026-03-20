import numpy as np
from PIL import Image
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import io

router = APIRouter(prefix="/emotion", tags=["Color-Emotion Analysis"])

# Fuzzy color-emotion mapping based on research
# Reference: Color-Emotion Associations in Art: Fuzzy Approach
COLOR_EMOTION_MAP = {
    "red":     {"anger": 0.8, "passion": 0.7, "energy": 0.6, "calm": 0.1},
    "blue":    {"calm": 0.9, "sadness": 0.6, "trust": 0.7, "anger": 0.1},
    "green":   {"hope": 0.8, "calm": 0.7, "growth": 0.9, "sadness": 0.2},
    "yellow":  {"happiness": 0.9, "energy": 0.7, "anxiety": 0.4, "calm": 0.3},
    "purple":  {"creativity": 0.8, "sadness": 0.5, "mystery": 0.7, "calm": 0.4},
    "orange":  {"enthusiasm": 0.8, "energy": 0.7, "happiness": 0.6, "calm": 0.2},
    "black":   {"sadness": 0.7, "fear": 0.6, "mystery": 0.8, "calm": 0.3},
    "white":   {"calm": 0.9, "hope": 0.7, "peace": 0.8, "sadness": 0.1},
    "brown":   {"stability": 0.7, "calm": 0.6, "sadness": 0.4, "energy": 0.2},
    "gray":    {"sadness": 0.6, "calm": 0.5, "neutral": 0.8, "energy": 0.1},
    "pink":    {"love": 0.8, "happiness": 0.7, "calm": 0.6, "anger": 0.1},
}

def rgb_to_color_name(r, g, b):
    """Map RGB values to nearest color name using fuzzy logic."""
    colors = {
        "red":    (255, 0, 0),
        "blue":   (0, 0, 255),
        "green":  (0, 128, 0),
        "yellow": (255, 255, 0),
        "purple": (128, 0, 128),
        "orange": (255, 165, 0),
        "black":  (0, 0, 0),
        "white":  (255, 255, 255),
        "brown":  (139, 69, 19),
        "gray":   (128, 128, 128),
        "pink":   (255, 192, 203),
    }
    
    min_dist = float("inf")
    nearest = "gray"
    
    for name, (cr, cg, cb) in colors.items():
        dist = ((r-cr)**2 + (g-cg)**2 + (b-cb)**2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            nearest = name
    
    return nearest

def extract_dominant_colors(image: Image.Image, n_colors: int = 5):
    """Extract dominant colors from image."""
    img = image.convert("RGB").resize((150, 150))
    pixels = np.array(img).reshape(-1, 3)
    
    # Simple clustering by rounding to nearest 50
    rounded = (pixels // 50) * 50
    unique, counts = np.unique(rounded, axis=0, return_counts=True)
    
    top_indices = np.argsort(counts)[-n_colors:][::-1]
    total = pixels.shape[0]
    
    dominant = []
    for idx in top_indices:
        r, g, b = unique[idx]
        dominant.append({
            "rgb": [int(r), int(g), int(b)],
            "percentage": round(float(counts[idx]) / total * 100, 2),
            "color_name": rgb_to_color_name(int(r), int(g), int(b))
        })
    
    return dominant

def analyze_emotions(dominant_colors: list):
    """Analyze emotions from dominant colors using fuzzy logic."""
    emotion_scores = {}
    
    for color_info in dominant_colors:
        color_name = color_info["color_name"]
        weight = color_info["percentage"] / 100
        
        if color_name in COLOR_EMOTION_MAP:
            for emotion, score in COLOR_EMOTION_MAP[color_name].items():
                if emotion not in emotion_scores:
                    emotion_scores[emotion] = 0
                emotion_scores[emotion] += score * weight
    
    # Normalize scores
    if emotion_scores:
        max_score = max(emotion_scores.values())
        if max_score > 0:
            emotion_scores = {
                k: round(v / max_score, 3)
                for k, v in emotion_scores.items()
            }
    
    # Sort by score
    sorted_emotions = dict(
        sorted(emotion_scores.items(),
               key=lambda x: x[1], reverse=True)
    )
    
    return sorted_emotions

class EmotionAnalysisResponse(BaseModel):
    dominant_colors: list
    emotion_scores: dict
    primary_emotion: str
    analysis_summary: str

@router.post("/analyze", response_model=EmotionAnalysisResponse)
async def analyze_image_emotion(
    file: UploadFile = File(...)
):
    """
    Analyze color-emotion associations in an uploaded image.
    Uses fuzzy logic based on Color-Emotion Associations in Art research.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid image type")
    
    content = await file.read()
    
    try:
        image = Image.open(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    dominant_colors = extract_dominant_colors(image)
    emotion_scores = analyze_emotions(dominant_colors)
    
    primary_emotion = max(emotion_scores, key=emotion_scores.get) \
        if emotion_scores else "neutral"
    
    top_colors = [c["color_name"] for c in dominant_colors[:3]]
    summary = (
        f"Image predominantly contains {', '.join(top_colors)} tones, "
        f"suggesting primary emotional association with '{primary_emotion}' "
        f"(score: {emotion_scores.get(primary_emotion, 0):.2f})."
    )
    
    return EmotionAnalysisResponse(
        dominant_colors=dominant_colors,
        emotion_scores=emotion_scores,
        primary_emotion=primary_emotion,
        analysis_summary=summary
    )