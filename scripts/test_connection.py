#!/usr/bin/env python3
"""
Diagnostic & Health Check for LubeLogger connection.
Verifies server URL, authentication, and read permissions.
"""

import sys
import os
import json

# Ensure parent directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_server.client import LubeLoggerClient, load_dotenv


def run_diagnostics():
    load_dotenv()
    url = os.getenv("LUBELOGGER_URL", "http://localhost:5000")
    api_key = os.getenv("LUBELOGGER_API_KEY", "")
    username = os.getenv("LUBELOGGER_USERNAME", "")
    password = os.getenv("LUBELOGGER_PASSWORD", "")

    print("=" * 60)
    print(" LUBELOGGER CONNECTION DIAGNOSTICS")
    print("=" * 60)
    print(f"Target URL: {url}")
    if api_key:
        masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
        print(f"Auth Method: API Key ({masked_key})")
    elif username:
        print(f"Auth Method: Basic Auth (User: {username})")
    else:
        print("Auth Method: None configured (checking if instance is unauthenticated/public)")
    print("-" * 60)

    client = LubeLoggerClient()

    print("[1/4] Checking server reachability and API version...")
    conn = client.test_connection()
    if not conn.get("success"):
        print(f"  ❌ FAILED: {conn.get('error')}")
        print("\nTroubleshooting tips:")
        print("  1. Verify LUBELOGGER_URL is reachable (e.g. check container or network).")
        print("  2. Verify credentials in .env or environment variables.")
        print("  3. If using self-signed HTTPS, set LUBELOGGER_VERIFY_SSL=false.")
        sys.exit(1)

    version_data = conn.get("version", {})
    current_ver = version_data.get("currentVersion", "Unknown") if isinstance(version_data, dict) else version_data
    print(f"  ✅ Connected successfully! LubeLogger version: {current_ver}")

    whoami = conn.get("whoami")
    if whoami and isinstance(whoami, dict):
        print(f"  ✅ Authenticated as: {whoami.get('username', 'User')} ({whoami.get('emailAddress', 'N/A')})")

    print("[2/4] Testing vehicle list query...")
    try:
        vehicles = client.list_vehicles()
        print(f"  ✅ Found {len(vehicles)} vehicle(s):")
        for v in vehicles:
            v_id = v.get("id")
            year = v.get("year", "")
            make = v.get("make", "")
            model = v.get("model", "")
            plate = v.get("licensePlate", "No Plate")
            print(f"     - [ID: {v_id}] {year} {make} {model} (Plate: {plate})")
    except Exception as e:
        print(f"  ❌ Error fetching vehicles: {e}")
        sys.exit(1)

    if vehicles:
        first_id = vehicles[0].get("id")
        print(f"[3/4] Testing odometer query on Vehicle ID {first_id}...")
        try:
            latest_odo = client.get_latest_odometer(first_id)
            print(f"  ✅ Latest odometer reading: {latest_odo}")
        except Exception as e:
            print(f"  ⚠️ Could not fetch latest odometer: {e}")

        print(f"[4/4] Testing reminder query on Vehicle ID {first_id}...")
        try:
            reminders = client.get_reminders(first_id)
            print(f"  ✅ Found {len(reminders)} active reminder(s).")
        except Exception as e:
            print(f"  ⚠️ Could not fetch reminders: {e}")

    print("-" * 60)
    print("✅ All diagnostic checks completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_diagnostics()
