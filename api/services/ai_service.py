from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from app.core.config import settings
import math
import logging
from functools import lru_cache
from app.models.waste import WasteType
from supabase import create_client, Client
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Sustainability scores for different waste types (higher = more sustainable reuse)
SUSTAINABILITY_SCORES = {
    WasteType.CHEMICAL.value: 0.8,
    WasteType.METAL.value: 0.9,
    WasteType.PLASTIC.value: 0.6,
    WasteType.ORGANIC.value: 0.7,
    WasteType.ELECTRONIC.value: 0.5,
    WasteType.OTHER.value: 0.3
}

class AIService:
    def __init__(self):
        # Initialize the model and tokenizer
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
        # Initialize Supabase client
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Initialize embedding cache
        self.embedding_cache = {}
        
        # Load waste categories and their embeddings
        self.waste_categories = self._load_waste_categories()
        
    def _load_waste_categories(self) -> Dict[str, np.ndarray]:
        """Load predefined waste categories and their embeddings."""
        categories = {
            "chemical": ["chemical waste", "hazardous materials", "toxic substances"],
            "metal": ["metal scraps", "steel", "aluminum", "copper"],
            "plastic": ["plastic waste", "polymers", "thermoplastics"],
            "organic": ["organic waste", "biodegradable materials", "food waste"],
            "electronic": ["e-waste", "electronic components", "circuit boards"],
            "other": ["general waste", "mixed materials"]
        }
        
        category_embeddings = {}
        for category, keywords in categories.items():
            embeddings = [self._get_embedding(keyword) for keyword in keywords]
            category_embeddings[category] = np.mean(embeddings, axis=0)
        return category_embeddings
    
    @lru_cache(maxsize=1000)
    def _get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a given text with caching."""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
            
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        embedding = embeddings[0]
        
        self.embedding_cache[text] = embedding
        return embedding
    
    def analyze_waste(self, description: str, waste_type: Optional[str] = None) -> Dict[str, Any]:
        """Analyze waste description and return category, keywords, and embedding."""
        description_embedding = self._get_embedding(description)
        
        category_scores = {}
        for category, category_embedding in self.waste_categories.items():
            similarity = np.dot(description_embedding, category_embedding)
            category_scores[category] = similarity
            
        best_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        if waste_type and waste_type in self.waste_categories:
            category_scores[waste_type] *= 1.2
            
        words = [word.lower() for word in description.split() if len(word) > 3]
        keywords = list(set(words))[:10]
        
        sustainability = SUSTAINABILITY_SCORES.get(waste_type or best_category, 0.5)
        
        return {
            "category": best_category,
            "keywords": keywords,
            "embedding": description_embedding.tolist(),
            "sustainability_score": sustainability
        }
    
    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the Haversine distance between two points in kilometers."""
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    def find_matches(self, waste_info: Dict[str, Any], consumer_preferences: List[Dict[str, Any]]) -> List[Tuple[float, str, Dict[str, Any]]]:
        """Find potential matches between waste and consumers with enhanced scoring."""
        waste_analysis = self.analyze_waste(
            waste_info["description"],
            waste_info.get("waste_type")
        )
        
        match_results = []
        for preference in consumer_preferences:
            score, details = self._calculate_match_score(waste_analysis, waste_info, preference)
            match_results.append((score, preference["id"], details))
            
        match_results.sort(key=lambda x: x[0], reverse=True)
        
        # Store top matches in Supabase
        self._store_matches(waste_info["id"], match_results[:5])
        
        return match_results
    
    def _calculate_match_score(self, waste_analysis: Dict[str, Any], waste_info: Dict[str, Any], preference: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Enhanced match scoring with business factors."""
        # Category match
        category_match = 1.0 if waste_analysis["category"] == preference["category"] else 0.0
        
        # Keyword overlap
        waste_keywords = set(waste_analysis["keywords"])
        consumer_keywords = set(preference.get("keywords", []))
        keyword_overlap = len(waste_keywords & consumer_keywords) / max(1, min(len(waste_keywords), len(consumer_keywords)))
        
        # Form compatibility
        form_match = 1.0 if waste_info.get("waste_form") == preference.get("waste_form") else 0.0
        
        # Geographical proximity
        lat1, lon1 = waste_info.get("latitude"), waste_info.get("longitude")
        lat2, lon2 = preference.get("latitude"), preference.get("longitude")
        distance = self._haversine(lat1, lon1, lat2, lon2) if None not in (lat1, lon1, lat2, lon2) else float('inf')
        distance_score = 1 / (1 + distance) if distance != float('inf') else 0.0
        
        # Quantity matching
        quantity_score = 1.0
        if "quantity" in waste_info and "desired_quantity" in preference:
            available = waste_info["quantity"]
            desired = preference["desired_quantity"]
            quantity_score = min(1.0, desired / available) if available > 0 else 0.0
        
        # Business factors
        business_score = 0.0
        if "business_type" in waste_info and "preferred_business_types" in preference:
            if waste_info["business_type"] in preference["preferred_business_types"]:
                business_score = 1.0
        
        # Calculate weighted score
        weights = {
            "category": 0.25,
            "keywords": 0.15,
            "form": 0.15,
            "distance": 0.15,
            "quantity": 0.15,
            "sustainability": 0.1,
            "business": 0.05
        }
        
        final_score = (
            weights["category"] * category_match +
            weights["keywords"] * keyword_overlap +
            weights["form"] * form_match +
            weights["distance"] * distance_score +
            weights["quantity"] * quantity_score +
            weights["sustainability"] * waste_analysis.get("sustainability_score", 0.5) +
            weights["business"] * business_score
        )
        
        score_details = {
            "category_match": category_match,
            "keyword_overlap": keyword_overlap,
            "form_match": form_match,
            "distance_km": distance if distance != float('inf') else None,
            "distance_score": distance_score,
            "quantity_score": quantity_score,
            "business_score": business_score,
            "weights": weights
        }
        
        return final_score, score_details
    
    def _store_matches(self, waste_id: str, matches: List[Tuple[float, str, Dict[str, Any]]]) -> None:
        """Store matches in Supabase and trigger notifications."""
        try:
            for score, consumer_id, details in matches:
                data = {
                    "waste_id": waste_id,
                    "consumer_id": consumer_id,
                    "score": score,
                    "details": details,
                    "created_at": datetime.utcnow().isoformat(),
                    "status": "pending"
                }
                self.supabase.table("matches").insert(data).execute()
                
                # Trigger notification
                self._send_notification(consumer_id, waste_id, score)
        except Exception as e:
            logger.error(f"Failed to store matches: {str(e)}")
    
    def _send_notification(self, consumer_id: str, waste_id: str, score: float) -> None:
        """Send notification about new potential match."""
        try:
            message = f"New waste match found with score {score:.2f}"
            self.supabase.table("notifications").insert({
                "user_id": consumer_id,
                "message": message,
                "waste_id": waste_id,
                "read": False,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
