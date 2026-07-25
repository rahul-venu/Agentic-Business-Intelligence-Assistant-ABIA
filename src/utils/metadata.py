import pandas as pd
import json
from typing import Dict, Any

def extract_schema_metadata(dfs: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Generates schema metadata including column types and unique values for low-cardinality strings."""
    schema = {}
    for table_name, df in dfs.items():
        table_meta = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            col_info = {"type" : dtype}
    # For string/categorical columns, provide sample domain values for exact filtering
            if dtype == "object":
                unique_vals = df[col].dropna().unique().tolist()
                if len(unique_vals) <= 20:
                    col_info["allowed_values"] = unique_vals
                else:
                    col_info["sample_values"] = unique_vals[:5]
            table_meta[col] = col_info
        schema[table_name] = table_meta
    return schema 


#----------------------------------------------------------------
# FOR TESTING PURPOSES
#----------------------------------------------------------------

# if __name__ == "__main__":
#     from src.utils.data_loader import DataLoader
    
#     dfs = DataLoader.get_dataframes()
#     metadata = extract_schema_metadata(dfs)
    
#     print("--- Extracted Schema Metadata ---")
#     print(json.dumps(metadata, indent=2))
