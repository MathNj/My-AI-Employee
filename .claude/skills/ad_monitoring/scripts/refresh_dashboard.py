#!/usr/bin/env python3
"""
Refresh Dashboard Data

Triggers dashboard data refresh by checking if dashboard is running
and displaying status information.

Usage:
    python refresh_dashboard.py
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def refresh_dashboard() -> dict:
    """
    Trigger dashboard data refresh by sending request to reload data.

    Returns:
        {
            "status": str,
            "url": str,
            "last_update": str,
            "note": str
        }
    """
    dashboard_url = "http://localhost:8501"

    # Check if dashboard is running
    is_running = False
    try:
        import requests
        response = requests.get(dashboard_url, timeout=5)
        is_running = response.status_code == 200
    except:
        is_running = False
        import subprocess
        # Try to find if process is running
        try:
            # Check if uvicorn process is running
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe"],
                capture_output=True,
                text=True
            )
            if "dashboard.py" in result.stdout:
                is_running = True
        except:
            pass

    if not is_running:
        return {
            "status": "Dashboard not running",
            "url": dashboard_url,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "Start dashboard with: python ad_management/dashboard.py",
            "action_required": "Start dashboard server"
        }

    # Trigger refresh by making request
    try:
        import requests
        response = requests.get(f"{dashboard_url}/?refresh=true", timeout=10)
        if response.status_code == 200:
            return {
                "status": "Dashboard refreshed",
                "url": dashboard_url,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": "Data updates every 15 minutes automatically"
            }
    except Exception as e:
        return {
            "status": f"Refresh failed: {e}",
            "url": dashboard_url,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "Manual refresh failed"
        }


def main():
    parser = argparse.ArgumentParser(
        description="Refresh dashboard data"
    )

    parser.add_argument(
        "--url",
        default="http://localhost:8501",
        help="Dashboard URL (default: http://localhost:8501)"
    )

    args = parser.parse_args()

    # Refresh dashboard
    result = refresh_dashboard()

    # Output JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
