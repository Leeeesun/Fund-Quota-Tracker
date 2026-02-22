import akshare as ak
import pandas as pd
import json
import os
import time

CONFIG_FILE = 'config.json'

def update_fund_list():
    print("Fetching fund list from EastMoney via akshare...")
    max_retries = 3
    retry_delay = 5
    
    df_funds = None
    for attempt in range(max_retries):
        try:
            # Fetch all fund names and codes
            df_funds = ak.fund_name_em()
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print("Failed to fetch fund list after all attempts.")
                return False

    if df_funds is None or df_funds.empty:
        print("Fetched data is empty.")
        return False

    print(f"Total funds found: {len(df_funds)}")

    # Filter funds (Case-insensitive match for 标普500, 纳斯达克, 纳指)
    # df_funds columns: ['基金代码', '拼音缩写', '基金简称', '基金类型', '拼音全称']
    keywords = ["标普500", "纳斯达克", "纳指"]
    pattern = '|'.join(keywords)
    
    # Filtering
    filtered_df = df_funds[df_funds['基金简称'].str.contains(pattern, case=False, na=False)].copy()
    
    # Focus on A class funds (often names ending in A or not containing C/E etc.)
    # However, let's keep all for now and provide a clean list.
    # The user's original config had mostly A class, but the prompt says 
    # "筛选出‘基金简称’中包含...的所有基金".
    
    new_funds = []
    for _, row in filtered_df.iterrows():
        new_funds.append({
            "code": row['基金代码'],
            "name": row['基金简称']
        })
    
    print(f"Filtered funds count: {len(new_funds)}")

    # Load existing config
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found.")
        return False

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return False

    # Update only the 'funds' field
    config['funds'] = new_funds
    
    # Preserve formatting and save back
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"Successfully updated {CONFIG_FILE} with {len(new_funds)} funds.")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

if __name__ == "__main__":
    if update_fund_list():
        print("Update process completed successfully.")
    else:
        print("Update process failed.")
        exit(1)
