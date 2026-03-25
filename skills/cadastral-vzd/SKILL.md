---
name: cadastral-vzd
description: Calculate real estate cadastral values in Latvia. Use when users request (1) apartment property cadastral value calculation, (2) land cadastral value calculation, (3) premises group (residential or common area) cadastral value calculation, (4) fiscal cadastral value determination for any real estate in Latvia. Implements MK regulations using Python functions for land, premises groups, and undivided shares.
metadata:
  author: Aivis Brutans
  version: "1.1"
---

# Cadastral Valuation (Latvia)

Calculate real estate cadastral values according to Latvian regulations using Python functions from `skills_kadastrs.py`.

## Assets

Under the assets directory there are 2 files:
- FISK_DZI_ZON_short.parquet - parquet file with base values
- skills_kadastrs.py - defined functions

## Available Functions

Import from `/mnt/user-data/uploads/skills_kadastrs.py`:

- `undivided_share(shares_owned, total_share)` - Calculate undivided share ratio
- `land_fiscal_cadastral_value_city(...)` - Calculate land cadastral value (EUR)
- `group_premises_fiscal_cadastral_value_city(...)` - Calculate premises group cadastral value (EUR)

Or skills_kadastrs.py could be available under the assets directory.

## Required Python Packages

Before using the functions, install these packages:

```bash
pip install geopandas pyarrow --break-system-packages
```

- **geopandas** - Geographic data handling
- **pyarrow** - Read parquet file format


## Apartment Property Valuation Workflow

Calculate apartment property cadastral value using formula: `A + B × C + D × C`

Where:
- **A** = Apartment premises cadastral value
- **B** = Common area premises cadastral value (if exists)
- **C** = Undivided share ratio
- **D** = Land cadastral value

### Step 1: Determine Property Type

**Has common areas (shared spaces)?**
- YES → Calculate all: A, B, C, D
- NO → Calculate: A, C, D (skip B)

### Step 2: Gather Information

Ask user for parameters using the prompts below. Never assume values.

#### For Apartment Premises (A):

**Usage type** (map user response to code):
- "How many apartments in the building?"
  - 1 apartment → `'UT1110'`
  - 2 apartments → `'UT1121'`
  - 3+ apartments → `'UT1122'`

**Value zone**: "What is the property's value zone code?" (e.g., "3-0010000-010")

**Premises area**: "What is the apartment's total area in m²?" (convert ha/km² if needed)

**Outdoor area** (optional): "Does the apartment have outdoor areas (balcony, terrace)? If yes, area in m²?"

**Floor**: "On which floor is the apartment located?"

**Amenities**:
- "Does the apartment have sewerage?" (is_sewer)
- "Does the apartment have a sanitary unit?" (is_sanitary_unit)
- "Does the apartment have heating?" (is_heating)

Set: `is_residential_premises=True`, `is_utility_room=False`

#### For Common Areas (B) - if applicable:

**Premises area**: "What is the total common area in m²?"

Use SAME value_zone as apartment. Set: `is_utility_room=True`, `is_residential_premises=False`

#### For Undivided Share (C):

**Shares owned**: "How many shares does this owner own?"

**Total shares**: "What is the total number of shares?"

#### For Land (D):

**Land purpose** (map user response to code):
- "How many floors in the building?"
  - Undeveloped individual house land → `'PR600'`
  - Individual house → `'PR601'`
  - Undeveloped multi-apartment land → `'PR700'`
  - 1-2 floors → `'PR701'`
  - 3-5 floors → `'PR702'`
  - 6-16 floors → `'PR703'`
  - 17+ floors → `'PR704'`

**Value zone**: Use SAME value_zone as apartment

**Land area**: "What is the land area in m²?" (convert ha if needed: 1 ha = 10,000 m²)

**Encumbrance area** (optional): "Is there any encumbrance area? If yes, area in m²?"

**Contaminated area** (optional): "Is there any contaminated area? If yes, area in m²?"

### Step 3: Create and Execute Python Script

First, ensure required packages are installed:

```bash
pip install geopandas pyarrow --break-system-packages
```

Then create the calculation script:

```python
from skills_kadastrs import (
    undivided_share,
    land_fiscal_cadastral_value_city,
    group_premises_fiscal_cadastral_value_city
)

# Calculate A (apartment premises)
A = group_premises_fiscal_cadastral_value_city(
    usage_type='UT1122',  # Use gathered value
    value_zone='3-0010000-010',  # Use gathered value
    premises_area=75,
    outdoor_area=5,
    is_residential_premises=True,
    floor=3,
    is_sewer=True,
    is_sanitary_unit=True,
    is_heating=True
)

# Calculate B (common areas) - if applicable
B = group_premises_fiscal_cadastral_value_city(
    usage_type='UT1122',
    value_zone='3-0010000-010',
    premises_area=200,
    is_utility_room=True
)

# Calculate C (undivided share)
C = undivided_share(shares_owned=50, total_shares=500)

# Calculate D (land)
D = land_fiscal_cadastral_value_city(
    land_purpose_in_city='PR702',
    value_zone='3-0010000-010',
    land_area=1500,
    encumbrance_area=0,
    contaminated_area=0
)

# Final calculation
cadastral_value = A + B * C + D * C

print(f"A (Apartment): {A:.2f} EUR")
print(f"B (Common areas): {B:.2f} EUR")
print(f"C (Share): {C}")
print(f"D (Land): {D:.2f} EUR")
print(f"\nTotal cadastral value: {cadastral_value:.2f} EUR")
```

### Step 4: Present Results

Format output as:

```
APARTMENT PROPERTY CADASTRAL VALUE
===================================

Input Data:
-----------
[List all gathered parameters]

Calculation Results:
-------------------
A. Apartment premises: X,XXX.XX EUR
B. Common areas: X,XXX.XX EUR
C. Undivided share: 0.XX
D. Land: X,XXX.XX EUR

TOTAL CADASTRAL VALUE: XX,XXX.XX EUR
=====================================
Formula: A + B × C + D × C = [detailed calculation]
```

## Code Mapping Reference

When user describes in natural language, map to correct codes:

**Usage type codes:**
- 1 apartment → `'UT1110'`
- 2 apartments → `'UT1121'`
- 3+ apartments → `'UT1122'`

**Land purpose codes:**
- 1-2 floors / vienstāva/divstāvu → `'PR701'`
- 3-5 floors / trīs-piecu stāvu → `'PR702'`
- 6-16 floors / sešu-sešpadsmit stāvu → `'PR703'`
- 17+ floors / septiņpadsmit+ stāvu → `'PR704'`

## Unit Conversions

Convert automatically:
- 1 ha = 10,000 m²
- 1 km² = 1,000,000 m²
- 1 a = 100 m²

## Validation Checklist

Before calculating, verify:
- ✓ All required parameters gathered
- ✓ Same value_zone used for A, B, D calculations
- ✓ All areas in m²
- ✓ Codes correctly mapped
- ✓ Encumbrance/contaminated areas ≤ land area

## Special Cases

**Land only**: Use `land_fiscal_cadastral_value_city` only

**Premises only**: Use `group_premises_fiscal_cadastral_value_city` only

**100% ownership**: Set C = 1.0 (no undivided_share calculation needed)
