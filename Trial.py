import pandas as pd

df = pd.read_csv("database/orders.csv")

# FORCE CLEAN PHONE
df["customer_number"] = (
    df["customer_number"]
    .astype(str)
    .str.replace(".0", "", regex=False)
)

# SAVE CLEAN VERSION BACK
df.to_csv("database/orders.csv", index=False)

print("CLEANED SUCCESSFULLY")