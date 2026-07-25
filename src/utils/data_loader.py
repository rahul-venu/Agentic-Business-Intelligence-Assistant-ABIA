import pandas as pd
import os
from src.config.settings import settings

class DataLoader:
    _dfs = {}

    @classmethod
    def load_datasets(cls):
        if not cls._dfs:
            cls._dfs["customer_data"] = pd.read_csv(os.path.join(settings.DATA_DIR, "customer_data.csv"))
            cls._dfs["product_data"] = pd.read_csv(os.path.join(settings.DATA_DIR, "product_data.csv"))
            cls._dfs["sales_data"] = pd.read_csv(os.path.join(settings.DATA_DIR, "sales_data.csv"))
        return cls._dfs

    @classmethod
    def get_dataframes(cls):
        return cls.load_datasets()


#----------------------------------------------------------------
# FOR TESTING PURPOSES
#----------------------------------------------------------------

# if __name__ == "__main__":
#     try:
#         dfs = DataLoader.get_dataframes()
#         print("Data loaded successfully!\n")
        
#         for name, df in dfs.items():
#             print(f"--- Table: {name} ---")
#             print(f"Shape: {df.shape} (Rows: {df.shape[0]}, Columns: {df.shape[1]})")
#             print(f"Columns: {list(df.columns)}")
#             print(f"Sample:\n{df.head(2)}\n")
            
#     except Exception as e:
#         print(f"Failed to load datasets: {e}")