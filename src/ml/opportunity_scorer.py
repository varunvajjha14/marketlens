import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"


def load_features() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "ward_features.csv")


def load_census() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "ward_census_proxy.csv")


def compute_opportunity_score(df: pd.DataFrame, census: pd.DataFrame) -> pd.DataFrame:
    """
    Score each ward on market opportunity using a weighted composite.

    Signals:
      - Scarcity:        fewer venues = more room to enter
      - Delivery gap:    low delivery % = unmet demand
      - Cuisine gap:     fewer cuisine types = more gaps
      - Quality gap:     fast food heavy = demand for better options
      - Fragmentation:   independent-heavy = weaker incumbents
      - Population pull: high density + low income = high unmet demand
    """

    features = df.merge(
        census[["ward_name", "population", "population_density",
                "avg_income_proxy", "income_score"]],
        on="ward_name",
        how="left",
    )

    # ── Raw signals ──────────────────────────────────────────────

    # 1. Scarcity: venues per 1000 population (lower = more opportunity)
    features["venues_per_1000"] = (
        features["total_venues"] / (features["population"] / 1000)
    ).round(3)
    features["sig_scarcity"] = 1 / (features["venues_per_1000"] + 0.1)

    # 2. Delivery gap
    features["sig_delivery_gap"] = 1 - features["delivery_ratio"]

    # 3. Cuisine gap
    features["sig_cuisine_gap"] = 1 / (features["unique_cuisines"] + 1)

    # 4. Quality gap: fast food proportion
    features["sig_quality_gap"] = (
        features["fast_food_count"] / (features["total_venues"] + 1)
    )

    # 5. Fragmentation
    features["sig_fragmentation"] = 1 - (
        features["chain_count"] / (features["total_venues"] + 1)
    )

    # 6. Population demand signal:
    #    High density + Low income = highest unmet demand
    #    High density + High income = demand but more competition
    #    Low density + any income = lower signal
    density_scaled = MinMaxScaler().fit_transform(
        features[["population_density"]]
    ).flatten()
    income_inverse = (4 - features["income_score"]) / 3  # Low=1 → 1.0, High=3 → 0.33
    features["sig_population"] = density_scaled * income_inverse

    # ── Scale all signals to 0-1 ─────────────────────────────────
    signal_cols = [
        "sig_scarcity",
        "sig_delivery_gap",
        "sig_cuisine_gap",
        "sig_quality_gap",
        "sig_fragmentation",
        "sig_population",
    ]

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(features[signal_cols])
    scaled_df = pd.DataFrame(scaled, columns=signal_cols, index=features.index)

    # ── Weighted composite ───────────────────────────────────────
    weights = {
        "sig_scarcity":      0.25,
        "sig_delivery_gap":  0.20,
        "sig_population":    0.20,
        "sig_cuisine_gap":   0.15,
        "sig_quality_gap":   0.10,
        "sig_fragmentation": 0.10,
    }

    features["opportunity_score"] = sum(
        scaled_df[col] * weight for col, weight in weights.items()
    )

    features["opportunity_score"] = (
        MinMaxScaler(feature_range=(0, 100))
        .fit_transform(features[["opportunity_score"]])
        .round(1)
        .flatten()
    )

    # ── Cluster into tiers ───────────────────────────────────────
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    features["tier_raw"] = kmeans.fit_predict(features[["opportunity_score"]])

    cluster_means = (
        features.groupby("tier_raw")["opportunity_score"]
        .mean()
        .sort_values()
    )
    tier_map = {
        cluster_means.index[0]: "Low",
        cluster_means.index[1]: "Medium",
        cluster_means.index[2]: "High",
    }
    features["opportunity_tier"] = features["tier_raw"].map(tier_map)

    # ── Data confidence ──────────────────────────────────────────
    features["data_confidence"] = features["total_venues"].apply(
        lambda x: "High" if x >= 30 else "Medium" if x >= 10 else "Low"
    )
    features["confidence_pct"] = features["total_venues"].apply(
        lambda x: min(round((x / 50) * 100, 0), 100)
    )

    # ── Final output ─────────────────────────────────────────────
    result = features[[
        "ward_name", "ward_id",
        "total_venues", "restaurant_count", "fast_food_count",
        "cafe_count", "chain_count", "independent_count",
        "delivery_ratio", "unique_cuisines", "dominant_category",
        "population", "population_density", "avg_income_proxy",
        "venues_per_1000",
        "opportunity_score", "opportunity_tier",
        "data_confidence", "confidence_pct",
    ]].sort_values("opportunity_score", ascending=False).reset_index(drop=True)

    return result


def run_scoring():
    print("=" * 55)
    print("Loading ward features...")
    df = load_features()

    print("Loading census proxy data...")
    census = load_census()

    print("Computing opportunity scores with census integration...")
    scored = compute_opportunity_score(df, census)

    out_path = PROCESSED_DIR / "ward_scores.csv"
    scored.to_csv(out_path, index=False)

    print("\n" + "=" * 55)
    print("OPPORTUNITY SCORES — Mumbai Wards (v1.2)")
    print("=" * 55)

    for tier in ["High", "Medium", "Low"]:
        tier_df = scored[scored["opportunity_tier"] == tier]
        emoji = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}[tier]
        print(f"\n{emoji} {tier} Opportunity:")
        for _, row in tier_df.iterrows():
            print(
                f"  {row['ward_name']:<20} "
                f"score={row['opportunity_score']:>5.1f}  "
                f"pop={row['population']:>7,}  "
                f"density={row['population_density']:>6,}  "
                f"venues/1k={row['venues_per_1000']:.2f}  "
                f"income={row['avg_income_proxy']}"
            )

    print(f"\n✅ Saved to data/processed/ward_scores.csv")
    return scored


if __name__ == "__main__":
    run_scoring()