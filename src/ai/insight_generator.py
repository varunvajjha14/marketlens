import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from config.settings import GROQ_API_KEY


def generate_ward_insight(ward_data: dict) -> str:
    client = Groq(api_key=GROQ_API_KEY)

    total = ward_data['total_venues']
    chain_ratio = round(ward_data['chain_count'] / total * 100, 1) if total > 0 else 0

    prompt = f"""
You are a hyperlocal market intelligence analyst specialising in Mumbai's food and beverage sector.

A user has selected the following ward for analysis. Based purely on the data provided, write a concise, actionable market opportunity brief. Be specific — mention actual numbers from the data. Do not make up information not present in the data.

WARD DATA:
- Ward name: {ward_data['ward_name']}
- Opportunity score: {ward_data['opportunity_score']} / 100
- Opportunity tier: {ward_data['opportunity_tier']}
- Total food venues: {total}
- Restaurants: {ward_data['restaurant_count']}
- Fast food outlets: {ward_data['fast_food_count']}
- Cafes: {ward_data['cafe_count']}
- Chain venues: {ward_data['chain_count']} ({chain_ratio}% of total)
- Independent venues: {ward_data['independent_count']}
- Delivery-enabled venues: {round(ward_data['delivery_ratio'] * 100, 1)}% of total
- Unique cuisine types: {ward_data['unique_cuisines']}
- Dominant category: {ward_data['dominant_category']}

Write a brief with exactly three sections:
1. MARKET SNAPSHOT (2 sentences): What does this ward's food market look like right now?
2. KEY OPPORTUNITY (2-3 sentences): What is the single biggest opportunity here and why?
3. RECOMMENDED ENTRY (2 sentences): What type of business would have the best chance of success and why?

Keep the total response under 180 words. Use plain language — no jargon.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


def test_insight():
    test_ward = {
        "ward_name": "Dharavi",
        "opportunity_score": 81.4,
        "opportunity_tier": "High",
        "total_venues": 12,
        "restaurant_count": 2,
        "fast_food_count": 6,
        "cafe_count": 1,
        "chain_count": 0,
        "independent_count": 12,
        "delivery_ratio": 0.0,
        "unique_cuisines": 5,
        "dominant_category": "fast_food",
    }

    print(f"Generating insight for {test_ward['ward_name']}...\n")
    insight = generate_ward_insight(test_ward)
    print(insight)


if __name__ == "__main__":
    test_insight()