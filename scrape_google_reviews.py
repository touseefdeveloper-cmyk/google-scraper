import requests
import json
import os
import sys

API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
PLACES_URL = "https://maps.googleapis.com/maps/api/place/details/json"
OUTPUT_FILE = "google_reviews.json"

BUSINESSES = [
    {"id": "cabinet-refresh",          "place_id": "ChIJTceywKawwoAR7P0e_XuYHv0"},
    {"id": "american-vision-windows",  "place_id": "ChIJicB12WvX3IARIEqNVXJXGfQ"},
    {"id": "one-week-bath",            "place_id": "ChIJids7swqXwoAR_CPlvgRtybs"},
    {"id": "abc-pro",                  "place_id": "ChIJ20Vpuu4x6IAR_tMxaN5lZ5o"},
    {"id": "1-degree-construction",    "place_id": "ChIJQXbmEyi_woARGsHUIUqPe-A"},
    {"id": "mr-cabinet-care",          "place_id": "ChIJaXWFPjfR3IARACZGggTZr00"},
    {"id": "payless-kitchen-cabinets", "place_id": "ChIJjz28RCfBwoAR_xCPCOC3mUk"},
    {"id": "payless-bath-makeover",    "place_id": "ChIJ2dRgx_7BwoAR2wi9xgQmRog"},
    {"id": "adar-builders",            "place_id": "ChIJh8iSdLi_woARrk1Bs0DDlbw"},
    {"id": "gm-home-remodeling",       "place_id": "ChIJr_Cg4cCXwoAR-DFxjpdjdIo"},
]


def load_previous() -> dict:
    """Load last saved results so a failed request never wipes good data."""
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return {r["id"]: r for r in json.load(f) if isinstance(r, dict) and "id" in r}
    except Exception:
        return {}


def scrape_google(business: dict) -> dict:
    print(f"  [{business['id']}] Fetching ...")
    try:
        params = {
            "place_id": business["place_id"],
            "fields": "name,rating,user_ratings_total,url",
            "key": API_KEY,
        }
        response = requests.get(PLACES_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            raise ValueError(f"API status: {data.get('status')} — {data.get('error_message', '')}")

        result_data = data.get("result", {})
        rating       = result_data.get("rating")
        review_count = result_data.get("user_ratings_total")
        maps_url     = result_data.get("url")

        print(f"    ✓ Rating: {rating} | Reviews: {review_count}")
        return {
            "id": business["id"],
            "place_id": business["place_id"],
            "average_rating": str(rating) if rating is not None else None,
            "total_reviews": str(review_count) if review_count is not None else None,
            "google_maps_url": maps_url,
            "error": None,
        }

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return {
            "id": business["id"],
            "place_id": business["place_id"],
            "average_rating": None,
            "total_reviews": None,
            "google_maps_url": None,
            "error": str(e),
        }


def main():
    print("=== Google Reviews Scraper ===\n")
    previous = load_previous()
    results = []
    failed = 0

    for b in BUSINESSES:
        fresh = scrape_google(b)
        if fresh["error"]:
            failed += 1
            old = previous.get(b["id"])
            # Keep the last known good numbers instead of overwriting with nulls
            if old and old.get("total_reviews") is not None:
                print(f"    ↩ Keeping previous data for {b['id']}")
                kept = dict(old)
                kept["error"] = f"Latest refresh failed, showing previous data: {fresh['error']}"
                results.append(kept)
                continue
        results.append(fresh)

    # If every request failed, don't touch the file and make the run show red
    if failed == len(BUSINESSES):
        print("\n✗ All requests failed — leaving existing google_reviews.json untouched.")
        print("  Check your Google Cloud billing and that Places API is enabled for the key.")
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n=== Done! Results saved to {OUTPUT_FILE} ===")
    print(f"Success: {len(BUSINESSES) - failed} | Errors: {failed}")


if __name__ == "__main__":
    main()
