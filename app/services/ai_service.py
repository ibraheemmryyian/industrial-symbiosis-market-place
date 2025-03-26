from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from typing import List, Dict, Tuple
from app.core.config import settings
import json

class AIService:
    def __init__(self):
        # Initialize the model and tokenizer
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
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
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a given text."""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Use CLS token embedding
        embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        return embeddings[0]
    
    def analyze_waste(self, description: str) -> Dict:
        """Analyze waste description and return category and keywords."""
        # Generate embedding for the description
        description_embedding = self._get_embedding(description)
        
        # Find the most similar category
        category_scores = {}
        for category, category_embedding in self.waste_categories.items():
            similarity = np.dot(description_embedding, category_embedding)
            category_scores[category] = similarity
            
        best_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        # Extract keywords (simplified version)
        words = description.lower().split()
        keywords = [word for word in words if len(word) > 3]
        
        return {
            "category": best_category,
            "keywords": keywords[:5],
            "embedding": description_embedding.tolist()
        }
    
    def find_matches(self, waste_description: str, consumer_preferences: Dict) -> List[Tuple[float, str]]:
        """Find potential matches between waste and consumer preferences."""
        # Analyze waste
        waste_analysis = self.analyze_waste(waste_description)
        
        # Calculate match scores based on preferences
        match_scores = []
        for preference in consumer_preferences:
            score = self._calculate_match_score(waste_analysis, preference)
            match_scores.append((score, preference["id"]))
            
        # Sort by score and return top matches
        return sorted(match_scores, reverse=True)
    
    def _calculate_match_score(self, waste_analysis: Dict, preference: Dict) -> float:
        """Calculate match score between waste and consumer preference."""
        # Category match
        category_match = 1.0 if waste_analysis["category"] == preference["category"] else 0.0
        
        # Keyword overlap
        keyword_overlap = len(set(waste_analysis["keywords"]) & set(preference["keywords"])) / max(len(waste_analysis["keywords"]), len(preference["keywords"]))
        
        # Combine scores (can be adjusted based on importance)
        final_score = 0.7 * category_match + 0.3 * keyword_overlap
        
        return final_score 