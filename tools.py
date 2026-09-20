"""
Kisan Vaani - Agricultural tools for mandi prices and scheme eligibility.
"""

import json
from pathlib import Path
from typing import Dict, Any, Union

DATA_DIR = Path(__file__).resolve().parent / "data"


def get_mandi_price(crop: str, district: str) -> Union[Dict[str, Any], str]:
    """
    Fetch the latest mandi market price for a given crop and district.

    Args:
        crop: Name of the crop (e.g. 'onion', 'wheat', 'rice', 'cotton', 'tomato').
        district: Name of the district (e.g. 'Nashik', 'Pune', 'Indore', 'Karnal').

    Returns:
        Dictionary with price and date details, or a string indicating no data available.
    """
    mandi_file = DATA_DIR / "mandi_prices.json"
    if not mandi_file.exists():
        return "Error: Mandi price database not found."

    with open(mandi_file, "r", encoding="utf-8") as f:
        prices = json.load(f)

    target_crop = crop.strip().lower()
    target_district = district.strip().lower()

    for item in prices:
        if (
            item.get("crop", "").strip().lower() == target_crop
            and item.get("district", "").strip().lower() == target_district
        ):
            return {
                "crop": item["crop"].capitalize(),
                "district": item["district"].capitalize(),
                "price_per_quintal": item["price_per_quintal"],
                "unit": "INR per quintal",
                "date": item["date"],
            }

    return (
        f"No data available for crop '{crop}' in district '{district}'. "
        f"Currently tracked crops: onion, wheat, rice, cotton, tomato across Nashik, Pune, Indore, Karnal."
    )


def check_scheme_eligibility(land_acres: float, category: str) -> Dict[str, Any]:
    """
    Check eligibility for government agricultural schemes based on land holding and farmer category.

    Args:
        land_acres: Cultivated or owned land size in acres (e.g., 2.5).
        category: Farmer category, such as 'farmer' (land-owning farmer) or 'tenant' (tenant farmer).

    Returns:
        Dictionary containing qualifying schemes with reasons and non-qualifying schemes with reasons.
    """
    schemes_file = DATA_DIR / "schemes.json"
    if not schemes_file.exists():
        return {"error": "Schemes database not found."}

    with open(schemes_file, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    user_cat = category.strip().lower()
    qualifying = []
    non_qualifying = []

    for scheme in schemes:
        name = scheme.get("scheme_name", "Unknown Scheme")
        rules = scheme.get("eligibility_rules", {})
        max_land = rules.get("max_land_acres")
        allowed_cat = rules.get("category", "any").lower()
        benefit = scheme.get("benefit", "")

        disqualify_reasons = []

        # Check landholding limit
        if max_land is not None and land_acres > max_land:
            disqualify_reasons.append(
                f"Landholding ({land_acres} acres) exceeds the scheme maximum limit of {max_land} acres."
            )

        # Check farmer category
        if allowed_cat != "any" and allowed_cat != user_cat:
            disqualify_reasons.append(
                f"Scheme is designated for category '{allowed_cat}', but user category provided is '{category}'."
            )

        if not disqualify_reasons:
            reasons = []
            if max_land is not None:
                reasons.append(f"Landholding ({land_acres} acres) is within eligible limit ({max_land} acres).")
            else:
                reasons.append("No upper landholding limit applies.")
            reasons.append(f"Category '{category}' qualifies for this scheme.")

            qualifying.append({
                "scheme_name": name,
                "benefit": benefit,
                "reason": " ".join(reasons)
            })
        else:
            non_qualifying.append({
                "scheme_name": name,
                "reason": " ".join(disqualify_reasons)
            })

    return {
        "land_acres": land_acres,
        "category": category,
        "qualifying_schemes": qualifying,
        "non_qualifying_schemes": non_qualifying
    }
