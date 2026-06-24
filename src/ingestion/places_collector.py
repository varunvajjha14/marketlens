import requests
import json
import time
from pathlib import Path
from tqdm import tqdm
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))
from config.settings import MUMBAI_WARDS, SEARCH_RADIUS_KM, FOOD_AMENITIES

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def build_overpass_query(lat: float, lng: float, radius_km: float) -> str:
    """Build Overpass QL query to fetch all food/drink venues near a point."""
    radius_m = int(radius_km * 1000)
    amenity_filter = "|".join(FOOD_AMENITIES)

    query = f"""
    [out:json][timeout:60];
    (
      node["amenity"~"{amenity_filter}"](around:{radius_m},{lat},{lng});
      way["amenity"~"{amenity_filter}"](around:{radius_m},{lat},{lng});
      node["shop"="bakery"](around:{radius_m},{lat},{lng});
      node["cuisine"](around:{radius_m},{lat},{lng});
    );
    out center tags;
    """
    return query


def parse_element(element: dict, ward: dict) -> dict | None:
    """Extract relevant fields from an OSM node or way."""
    tags = element.get("tags", {})

    # Get coordinates (ways have 'center', nodes have direct lat/lon)
    if element["type"] == "node":
        lat = element.get("lat")
        lng = element.get("lon")
    elif element["type"] == "way":
        center = element.get("center", {})
        lat = center.get("lat")
        lng = center.get("lon")
    else:
        return None

    if not lat or not lng:
        return None

    name = tags.get("name") or tags.get("name:en") or tags.get("brand")
    if not name:
        return None  # skip unnamed venues

    return {
        "osm_id": f"{element['type']}_{element['id']}",
        "name": name,
        "lat": lat,
        "lng": lng,
        "amenity": tags.get("amenity"),
        "cuisine": tags.get("cuisine"),
        "diet": tags.get("diet:vegetarian") or tags.get("diet:vegan"),
        "opening_hours": tags.get("opening_hours"),
        "phone": tags.get("phone") or tags.get("contact:phone"),
        "takeaway": tags.get("takeaway"),
        "delivery": tags.get("delivery"),
        "outdoor_seating": tags.get("outdoor_seating"),
        "price_range": tags.get("price_range"),
        "brand": tags.get("brand"),
        "operator": tags.get("operator"),
        "ward": ward["ward"],
        "ward_name": ward["name"],
    }


def collect_ward_data(ward: dict) -> list:
    """Fetch all food venues for one ward from Overpass API."""
    query = build_overpass_query(ward["lat"], ward["lng"], SEARCH_RADIUS_KM)

    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=90,
            headers={"User-Agent": "MarketLens-Portfolio-Project/1.0"}
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print(f"  ⚠ Timeout for {ward['name']}, skipping")
        return []
    except Exception as e:
        print(f"  ⚠ Error for {ward['name']}: {e}")
        return []

    elements = data.get("elements", [])
    places = []
    seen_ids = set()

    for element in elements:
        parsed = parse_element(element, ward)
        if parsed and parsed["osm_id"] not in seen_ids:
            seen_ids.add(parsed["osm_id"])
            places.append(parsed)

    return places


def run_collection():
    """Collect data for all Mumbai wards and save to data/raw/."""
    print(f"Starting OSM collection for {len(MUMBAI_WARDS)} wards...")
    print("No API key needed — using OpenStreetMap Overpass API\n")

    all_places = []

    for ward in tqdm(MUMBAI_WARDS, desc="Collecting wards"):
        ward_key = ward["ward"]
        out_file = RAW_DIR / f"ward_{ward_key}_{ward['name'].replace(' ', '_')}.json"

        if out_file.exists():
            print(f"  ✓ {ward['name']} already collected, skipping")
            with open(out_file) as f:
                all_places.extend(json.load(f))
            continue

        print(f"\n→ {ward['name']} (ward {ward_key})")
        places = collect_ward_data(ward)

        with open(out_file, "w") as f:
            json.dump(places, f, indent=2)

        print(f"  ✓ {len(places)} venues found")
        all_places.extend(places)

        time.sleep(3)  # be polite to the free Overpass server

    # Deduplicate across wards (venues near ward boundaries appear twice)
    seen = set()
    deduped = []
    for p in all_places:
        if p["osm_id"] not in seen:
            seen.add(p["osm_id"])
            deduped.append(p)

    consolidated = RAW_DIR / "all_wards_places.json"
    with open(consolidated, "w") as f:
        json.dump(deduped, f, indent=2)

    print(f"\n✅ Done! {len(deduped)} unique venues across all wards")
    print(f"   Saved to: data/raw/all_wards_places.json")
    return deduped


if __name__ == "__main__":
    run_collection()