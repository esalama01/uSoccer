import pandas as pd

df = pd.read_parquet("../data/uSoccer_dataset.parquet")
print(df['league'].value_counts())
