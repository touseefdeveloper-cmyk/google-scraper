import requests
import json
import os

API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
PLACES_URL = "https://maps.googleapis.com/maps/api/place/details/json"

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
    results = [scrape_google(b) for b in BUSINESSES]

    output_file = "google_reviews.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n=== Done! Results saved to {output_file} ===")
    errors = sum(1 for r in results if r["error"])
    print(f"Success: {len(results) - errors} | Errors: {errors}")


if __name__ == "__main__":
    main()
