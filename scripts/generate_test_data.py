import pandas as pd
import numpy as np

def generate_legacy_data():
    data = {
        "Site Name": ["Cave A"] * 5 + ["Lake B"] * 5,
        "Lat": [45.123] * 5 + [46.456] * 5,
        "Lon": [-1.234] * 5 + [-2.345] * 5,
        "Sample_ID": [f"S-{i}" for i in range(1, 11)],
        "Material Type": ["Bone Collagen", "Bone Collagen", "Charcoal", "Tooth Enamel", "Bone Collagen",
                          "Sediment", "Wood", "Peat", "Peat", "Sediment"],
        "Taxon": ["Bos taurus", "Equus caballus", "Pinus sylvestris", "Homo sapiens", "Canis lupus",
                  "Mixed", "Quercus", "Sphagnum", "Sphagnum", "Mixed"],
        "d13C": [-21.5, -20.1, -25.4, -12.3, -19.8, -27.5, -26.1, -28.2, -29.0, -26.5],
        "d15N": [5.6, 6.1, np.nan, 9.5, 8.2, np.nan, np.nan, np.nan, np.nan, np.nan],
        "C:N": [3.2, 3.4, np.nan, np.nan, 3.1, np.nan, np.nan, np.nan, np.nan, np.nan],
        "14C BP_uncal": [2500, 2650, 4500, 12000, 5000, 8000, 9500, 10200, 10500, 11000]
    }
    df = pd.DataFrame(data)
    df.to_csv("tests/test_data/legacy_data.csv", index=False)
    print("Generated tests/test_data/legacy_data.csv")

if __name__ == "__main__":
    generate_legacy_data()
