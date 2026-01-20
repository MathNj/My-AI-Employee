# Download Ad Sheets
import gspread
import pandas as pd
import requests
import re
import os
import sys
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe
from datetime import datetime, date
from openpyxl.utils import column_index_from_string

# Add parent directory to path to import shared logger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import log_ad_event, flush_logs

# --- CONFIGURATION ---
SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file']
SHARED_SHEET_ID = ""
EXPORT_PATH = "Downloaded_Ads_Sheet.xlsx"
ACTIVE_AD_SHEET_PATH = "Active_Ads_List.csv"
LOG_FILE_PATH = "Ad_Status_Log.xlsx"
END_DATE_SLACK_HOOK = ""

creds = Credentials.from_service_account_file('client_secret.json', scopes=SCOPES)
gc = gspread.authorize(creds)

def download_sheet_with_gspread(sheet_id, path_to_save_xlsx):
    wb = gc.open_by_key(sheet_id)
    writer = pd.ExcelWriter(path_to_save_xlsx, engine="xlsxwriter")
    for worksheet in wb.worksheets():
        df = get_as_dataframe(worksheet, evaluate_formulas=True, dtype=str)
        safe_title = re.sub(r'[/*?:\[\]]', '', worksheet.title)[:31] 
        df.to_excel(writer, sheet_name=safe_title, index=False)
    writer.close()
    print("Saved all tabs to Excel.")

def extract_active_ads_by_tab(df, live_col, url_col, name_col, end_date_col):
    active_ads = []
    for idx, row in df.iterrows():
        live_value = str(row.get(live_col)).strip().lower()
        if live_value == 'yes':
            url = str(row.get(url_col)).strip()
            name = str(row.get(name_col)).strip()
            end_date = row.get(end_date_col)
            if pd.notna(end_date):
                try:
                    parsed = pd.to_datetime(end_date, dayfirst=True, errors='coerce') 
                    if isinstance(parsed, pd.Timestamp):
                        end_date = parsed.date()
                    else:
                        end_date = None
                except:
                    end_date = None
            active_ads.append((url, name, end_date))
    print(f"Found {len(active_ads)} active ads in tab.")
    return active_ads

def send_slack_notification(webhook_url, message):
    try:
        requests.post(webhook_url, json={"text": message})
        print("Slack notification sent.")
    except Exception as e:
        print(f"Slack error: {e}")

def notify_end_dates(ad_data):
    today = datetime.today().date()
    today_ads = []
    overdue_ads = []
    for url, name, end_date in ad_data:
        if not isinstance(end_date, date):
            continue
        if end_date == today:
            today_ads.append(f"Ad: {name}\nURL: {url}\nEnd Date: {end_date}")
            log_ad_event(name, url, "Ad Ending Today", "Notification Sent", LOG_FILE_PATH)
        elif end_date < today:
            overdue_ads.append(f"Ad: {name}\nURL: {url}\nEnd Date: {end_date}")

    if today_ads:
        msg_today = "*Ads Ending Today:*\n\n" + "\n\n".join(today_ads)
        print(msg_today)
        send_slack_notification(END_DATE_SLACK_HOOK, msg_today)

    if overdue_ads:
        msg_overdue = "*⚠️ Ads Past End Date (Still Active):*\n\n" + "\n\n".join(overdue_ads)
        print(msg_overdue)
        send_slack_notification(END_DATE_SLACK_HOOK, msg_overdue)


def get_col_name_by_letter(df, col_letter):
    col_idx = column_index_from_string(col_letter) - 1
    return df.columns[col_idx]

# === MAIN RUN ===
download_sheet_with_gspread(SHARED_SHEET_ID, EXPORT_PATH)

xls = pd.ExcelFile(EXPORT_PATH)
all_active_ads = []

TAB_CONFIGS = [
    ("1) Newness Collection Ads",     'W', 'T', 'B', 'AA'),
    ("2) Best Sellers",               'U', 'S', 'B', 'Z'),
    ("3) High Cover",                 'T', 'R', 'B', 'Y'),
    ("5) Seasonal",                   'U', 'S', 'B', 'Z')
]

for sheet_name, live_letter, url_letter, name_letter, end_letter in TAB_CONFIGS:
    try:
        df = xls.parse(sheet_name)
        live_col = get_col_name_by_letter(df, live_letter)
        url_col = get_col_name_by_letter(df, url_letter)
        name_col = get_col_name_by_letter(df, name_letter)
        end_col = get_col_name_by_letter(df, end_letter)

        ads = extract_active_ads_by_tab(df, live_col, url_col, name_col, end_col)
        all_active_ads.extend(ads)
    except Exception as e:
        print(f"Error parsing sheet {sheet_name}: {e}")

notify_end_dates(all_active_ads)

if all_active_ads:
    pd.DataFrame(all_active_ads, columns=['URL', 'Ad Name', 'End Date']).to_csv(ACTIVE_AD_SHEET_PATH, index=False)
    print("Active ads saved.")
    log_ad_event("System", "N/A", "Active Ads List Refreshed", f"{len(all_active_ads)} ads found", LOG_FILE_PATH)
else:
    no_ads_msg = "*No active ads found in any tab.*"
    print(no_ads_msg)
    send_slack_notification(END_DATE_SLACK_HOOK, no_ads_msg)

# Flush all buffered logs to disk
print("Flushing logs to disk...")
flush_logs(LOG_FILE_PATH)