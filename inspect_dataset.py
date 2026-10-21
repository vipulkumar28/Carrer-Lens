import pandas as pd

DATA_PATH = "data/test.csv"

df = pd.read_csv(DATA_PATH)

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
for column in df.columns:
    print(column)

print("\nFirst five rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum().sort_values(ascending=False))

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nUnique values:")
for column in df.columns:
    if df[column].nunique() <= 10:
        print(f"\n{column}:")
        print(df[column].unique())

print("\nStatistical summary:")
print(df.describe(include="all").transpose())