import os
import pytest
import pandas as pd
from typing import List, Dict

MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BUYERS_CSV_PATH = R'C:\Users\amrey\Desktop\industrial symbiosis market place\buyers.csv'
SELLERS_CSV_PATH = R'C:\Users\amrey\Desktop\industrial symbiosis market place\sellers.csv'  # Fixed filename

class MockAIService:
    def __init__(self):
        self.analyzed_data = {}
        
    def analyze_description(self, description: str) -> Dict:
        """Analyze waste/seller description"""
        self.analyzed_data[description] = {
            "category": "plastic" if "plastic" in description.lower() else "other",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        return self.analyzed_data[description]
    
    def find_best_matches(self, source: Dict, targets: List[Dict], is_seller: bool) -> List[tuple]:
        """Improved matching with better scoring"""
        matches = []
        for target in targets:
            score = 0.0
            
            # 1. Waste form match (50% weight)
            if source["waste_form"] == target["waste_form"]:
                score += 0.5
                
            # 2. Keyword match (50% weight)
            source_desc = source["description"].lower()
            target_desc = target["description"].lower()
            
            # Count matching keywords
            common_terms = set(source_desc.split()) & set(target_desc.split())
            if len(common_terms) > 0:
                score += 0.5 * (len(common_terms) / max(len(source_desc.split()), len(target_desc.split())))

            matches.append((score, target["id"]))
        
        return sorted(matches, reverse=True)[:3]

@pytest.fixture
def mock_ai_service():
    return MockAIService()

def load_and_prepare_data():
    """Load data with better validation"""
    if not os.path.exists(BUYERS_CSV_PATH):
        pytest.fail(f"Buyers CSV missing at {BUYERS_CSV_PATH}")
    if not os.path.exists(SELLERS_CSV_PATH):
        pytest.fail(f"Sellers CSV missing at {SELLERS_CSV_PATH}")

    try:
        buyers = pd.read_csv(BUYERS_CSV_PATH)
        sellers = pd.read_csv(SELLERS_CSV_PATH)
        
        # Validate data format
        required = {'id', 'description', 'waste_form', 'latitude', 'longitude'}
        for name, df in [('buyers', buyers), ('sellers', sellers)]:
            missing = required - set(df.columns)
            if missing:
                pytest.fail(f"{name} CSV missing columns: {missing}")

        return {"buyers": buyers.to_dict('records'), "sellers": sellers.to_dict('records')}
        
    except Exception as e:
        pytest.fail(f"Data load failed: {str(e)}")

def test_bidirectional_matching(mock_ai_service):
    """Enhanced test with detailed output"""
    data = load_and_prepare_data()
    buyers = data["buyers"]
    sellers = data["sellers"]
    
    # Pre-analyze all seller descriptions
    for seller in sellers:
        mock_ai_service.analyze_description(seller["description"])

    # Test seller-to-buyer matches
    print("\n[Seller to Buyer Matches]")
    for seller in sellers:
        matches = mock_ai_service.find_best_matches(
            source={"description": seller["description"], "waste_form": seller["waste_form"]},
            targets=buyers,
            is_seller=True
        )
        print(f"\nSeller {seller['id']}: {seller['description'][:50]}...")
        for score, buyer_id in matches:
            buyer = next(b for b in buyers if b["id"] == buyer_id)
            print(f"  Match with {buyer_id} ({score:.2f}): {buyer['description'][:50]}...")

    # Test buyer-to-seller matches
    print("\n[Buyer to Seller Matches]")
    for buyer in buyers:
        matches = mock_ai_service.find_best_matches(
            source={"description": buyer["description"], "waste_form": buyer["waste_form"]},
            targets=sellers,
            is_seller=False
        )
        print(f"\nBuyer {buyer['id']}: {buyer['description'][:50]}...")
        for score, seller_id in matches:
            seller = next(s for s in sellers if s["id"] == seller_id)
            print(f"  Match with {seller_id} ({score:.2f}): {seller['description'][:50]}...")

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])  # Added -s flag for output