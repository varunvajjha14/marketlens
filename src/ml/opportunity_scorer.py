import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"


def load_features() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "ward_features.csv")


def compute_opportunity_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Score each ward on market opportunity using a weighted composite.

    Logic:
      - Fewer total venues = less competition = higher opportunity
      - More independents vs chains = more fragmented market = higher opportunity
      - Low delivery ratio = underserved on delivery = higher opportunity
      - Low cuisine diversity = cuisine gap exists = higher opportunity
      - More fast food vs restaurants = quality gap = higher opportunity

    All signals are scaled 0-1 then combined with weights.
    Final score: 0 = low opportunity, 100 = high opportunity
    """

    features = df.copy()

    # --- Raw signals (higher raw value = more opportunity) ---

    # 1. Scarcity: inverse of total venues (fewer venues = more room to enter)
    features["sig_scarcity"] = 1 / (features["total_venues"] + 1)

    # 2. Fragmentation: independent ratio (more independents = weaker incumbents)
    features["sig_fragmentation"] = 1 - features["chain_ratio"]

    # 3. Delivery gap: inverse of delivery ratio (low delivery = unmet demand)
    features["sig_delivery_gap"] = 1 - features["delivery_ratio"]

    # 4. Cuisine gap: inverse of unique cuisines normalised (fewer = more gaps)
    features["sig_cuisine_gap"] = 1 / (features["unique_cuisines"] + 1)

    # 5. Quality gap: fast_food proportion (high fast food = demand for better options)
    features["sig_quality_gap"] = features["fast_food_count"] / (features["total_venues"] + 1)

    # --- Scale every signal to 0-1 ---
    signal_cols = [
        "sig_scarcity",
        "sig_fragmentation",
        "sig_delivery_gap",
        "sig_cuisine_gap",
        "sig_quality_gap",
    ]

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(features[signal_cols])
    scaled_df = pd.DataFrame(scaled, columns=signal_cols, index=features.index)

    # --- Weighted composite ---
    weights = {
        "sig_scarcity":      0.30,   # most important: how crowded is the market
        "sig_delivery_gap":  0.25,   # second: delivery is the core use case
        "sig_cuisine_gap":   0.20,   # third: cuisine diversity gap
        "sig_quality_gap":   0.15,   # fourth: fast food heavy = quality opportunity
        "sig_fragmentation": 0.10,   # fifth: chain vs independent dynamic
    }

    features["opportunity_score"] = sum(
        scaled_df[col] * weight for col, weight in weights.items()
    )

    # Scale to 0-100 for readability
    features["opportunity_score"] = (
        MinMaxScaler(feature_range=(0, 100))
        .fit_transform(features[["opportunity_score"]])
        .round(1)
        .flatten()
    )

    # --- Cluster into tiers ---
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    features["tier_raw"] = kmeans.fit_predict(features[["opportunity_score"]])

    # Map cluster numbers to meaningful labels based on score
    cluster_means = features.groupby("tier_raw")["opportunity_score"].mean().sort_values()
    tier_map = {
        cluster_means.index[0]: "Low",
        cluster_means.index[1]: "Medium",
        cluster_means.index[2]: "High",
    }
    features["opportunity_tier"] = features["tier_raw"].map(tier_map)

    # --- Final output columns ---
    # --- Data confidence score ---
    # Based on how many venues we have vs expected for a Mumbai ward
    # Wards with <10 venues are likely under-mapped on OSM
    features["data_confidence"] = features["total_venues"].apply(
        lambda x: "High" if x >= 30 else "Medium" if x >= 10 else "Low"
    )
    features["confidence_pct"] = features["total_venues"].apply(
        lambda x: min(round((x / 50) * 100, 0), 100)
    )

    result = features[[
        "ward_name", "ward_id",
        "total_venues", "restaurant_count", "fast_food_count",
        "cafe_count", "chain_count", "independent_count",
        "delivery_ratio", "unique_cuisines", "dominant_category",
        "opportunity_score", "opportunity_tier",
        "data_confidence", "confidence_pct",
    ]].sort_values("opportunity_score", ascending=False).reset_index(drop=True)
    
    return result


def run_scoring():
    print("=" * 50)
    print("Loading ward features...")
    df = load_features()

    print("Computing opportunity scores...")
    scored = compute_opportunity_score(df)

    # Save
    out_path = PROCESSED_DIR / "ward_scores.csv"
    scored.to_csv(out_path, index=False)

    print("\n" + "=" * 50)
    print("OPPORTUNITY SCORES — Mumbai Wards")
    print("=" * 50)

    for tier in ["High", "Medium", "Low"]:
        tier_df = scored[scored["opportunity_tier"] == tier]
        print(f"\n🟢 {tier} Opportunity:" if tier == "High"
              else f"\n🟡 {tier} Opportunity:" if tier == "Medium"
              else f"\n🔴 {tier} Opportunity:")
        for _, row in tier_df.iterrows():
            print(
                f"  {row['ward_name']:<20} "
                f"score={row['opportunity_score']:>5.1f}  "
                f"venues={row['total_venues']:>3}  "
                f"delivery_ratio={row['delivery_ratio']:.2f}  "
                f"cuisines={row['unique_cuisines']}"
            )

    print(f"\n✅ Saved to data/processed/ward_scores.csv")
    return scored


if __name__ == "__main__":
    run_scoring()