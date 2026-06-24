import json
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_data() -> pd.DataFrame:
    """Load the consolidated raw JSON into a DataFrame."""
    with open(RAW_DIR / "all_wards_places.json") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} raw venues")
    return df


def clean_venues(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardise the raw venue DataFrame."""

    # Drop rows with no amenity (the 60 None values)
    df = df[df["amenity"].notna()].copy()

    # Drop non-food amenities that slipped through
    exclude = {"internet_cafe", "pub"}
    df = df[~df["amenity"].isin(exclude)].copy()

    # Normalise cuisine: lowercase, strip whitespace, take first if multiple
    df["cuisine"] = (
        df["cuisine"]
        .fillna("unknown")
        .str.lower()
        .str.strip()
        .str.split(r"[;,|]")
        .str[0]
        .str.strip()
    )

    # Simplify amenity into broader category
    amenity_map = {
        "restaurant":  "restaurant",
        "fast_food":   "fast_food",
        "cafe":        "cafe",
        "bar":         "bar",
        "ice_cream":   "dessert",
        "bakery":      "dessert",
        "food_court":  "food_court",
    }
    df["category"] = df["amenity"].map(amenity_map).fillna("other")

    # Boolean fields
    for col in ["takeaway", "delivery", "outdoor_seating"]:
        df[col] = df[col].map({"yes": True, "no": False}).fillna(False)

    # Flag chain/branded venues
    df["is_chain"] = df["brand"].notna() | df["operator"].notna()

    # Keep only columns we need going forward
    keep_cols = [
        "osm_id", "name", "lat", "lng",
        "ward", "ward_name",
        "amenity", "category", "cuisine",
        "takeaway", "delivery", "outdoor_seating",
        "is_chain", "opening_hours",
    ]
    df = df[keep_cols].reset_index(drop=True)

    print(f"After cleaning: {len(df)} venues")
    return df


def build_ward_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate venue-level data into one row per ward.
    These become the features for the ML opportunity scorer.
    """

    features = []

    for ward_name, group in df.groupby("ward_name"):
        total = len(group)

        feat = {
            "ward_name": ward_name,
            "ward_id": group["ward"].iloc[0],

            # --- Volume features ---
            "total_venues": total,
            "restaurant_count": (group["category"] == "restaurant").sum(),
            "fast_food_count":  (group["category"] == "fast_food").sum(),
            "cafe_count":       (group["category"] == "cafe").sum(),
            "bar_count":        (group["category"] == "bar").sum(),
            "dessert_count":    (group["category"] == "dessert").sum(),

            # --- Chain vs independent ---
            "chain_count":       group["is_chain"].sum(),
            "independent_count": (~group["is_chain"]).sum(),
            "chain_ratio":       round(group["is_chain"].sum() / total, 3),

            # --- Service features ---
            "delivery_count":  group["delivery"].sum(),
            "takeaway_count":  group["takeaway"].sum(),
            "delivery_ratio":  round(group["delivery"].sum() / total, 3),

            # --- Cuisine diversity ---
            "unique_cuisines": group["cuisine"].nunique(),
            "top_cuisine":     group["cuisine"].mode()[0] if total > 0 else "unknown",

            # --- Dominant category ---
            "dominant_category": group["category"].mode()[0] if total > 0 else "unknown",
        }

        features.append(feat)

    ward_df = pd.DataFrame(features).sort_values("total_venues", ascending=False)
    print(f"Built feature table: {len(ward_df)} wards × {len(ward_df.columns)} features")
    return ward_df


def run_etl():
    """Full ETL pipeline: load → clean → aggregate → save."""
    print("=" * 50)
    print("STEP 1: Loading raw data")
    print("=" * 50)
    raw_df = load_raw_data()

    print("\n" + "=" * 50)
    print("STEP 2: Cleaning venues")
    print("=" * 50)
    clean_df = clean_venues(raw_df)

    print("\n" + "=" * 50)
    print("STEP 3: Building ward features")
    print("=" * 50)
    ward_df = build_ward_features(clean_df)

    # Save both outputs
    clean_df.to_csv(PROCESSED_DIR / "venues_clean.csv", index=False)
    ward_df.to_csv(PROCESSED_DIR / "ward_features.csv", index=False)

    print("\n" + "=" * 50)
    print("ETL complete. Files saved:")
    print("  data/processed/venues_clean.csv")
    print("  data/processed/ward_features.csv")
    print("=" * 50)

    print("\nWard feature table preview:")
    print(ward_df.to_string(index=False))

    return clean_df, ward_df


if __name__ == "__main__":
    run_etl()