import pandas as pd
df_filtered = pd.read_parquet(
    "../data/uSoccer_dataset.parquet",
    filters=[('league', 'in', ['ENG-Premier League', 'ESP-La Liga'])]
)
print(df_filtered["type_id"].value_counts())
