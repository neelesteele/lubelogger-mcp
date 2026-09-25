#!/usr/bin/env python3
"""
LubeLogger CLI Tool
Command-line interface for managing LubeLogger vehicles, records, reminders, and notes.
"""

import sys
import os
import json
import argparse
from datetime import date as dt_date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_server.client import LubeLoggerClient, load_dotenv


def get_client() -> LubeLoggerClient:
    load_dotenv()
    return LubeLoggerClient()


def main():
    parser = argparse.ArgumentParser(description="LubeLogger CLI Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # test
    subparsers.add_parser("test", help="Test connection to LubeLogger")

    # vehicles
    subparsers.add_parser("vehicles", help="List all vehicles")

    # vehicle info
    p_vinfo = subparsers.add_parser("vehicle", help="Get detailed info for a vehicle")
    p_vinfo.add_argument("vehicle_id", type=int, help="Vehicle ID")

    # latest odometer
    p_odo = subparsers.add_parser("odometer", help="Get latest odometer for a vehicle")
    p_odo.add_argument("vehicle_id", type=int, help="Vehicle ID")

    # query records
    p_records = subparsers.add_parser("records", help="List records of a given type")
    p_records.add_argument("type", choices=["gas", "service", "repair", "odometer", "reminder", "note", "plan", "upgrade", "supply", "tax"])
    p_records.add_argument("--vehicle-id", type=int, help="Vehicle ID (optional)")
    p_records.add_argument("--all", action="store_true", help="Fetch across all vehicles")

    # add gas
    p_gas = subparsers.add_parser("add-gas", help="Add a gas/fuel record")
    p_gas.add_argument("--vehicle-id", type=int, required=True, help="Vehicle ID")
    p_gas.add_argument("--date", default=dt_date.today().isoformat(), help="Date (YYYY-MM-DD), default: today")
    p_gas.add_argument("--odometer", required=True, help="Odometer mileage")
    p_gas.add_argument("--fuel", required=True, help="Fuel consumed (gallons/liters)")
    p_gas.add_argument("--cost", required=True, help="Total cost ($)")
    p_gas.add_argument("--partial", action="store_true", help="Tank was not filled to full")
    p_gas.add_argument("--notes", default="", help="Optional notes")
    p_gas.add_argument("--tags", default="", help="Space-separated tags")

    # add service
    p_svc = subparsers.add_parser("add-service", help="Add a scheduled service record")
    p_svc.add_argument("--vehicle-id", type=int, required=True, help="Vehicle ID")
    p_svc.add_argument("--date", default=dt_date.today().isoformat(), help="Date (YYYY-MM-DD), default: today")
    p_svc.add_argument("--odometer", required=True, help="Odometer mileage")
    p_svc.add_argument("--desc", required=True, help="Description of service (e.g. 'Oil Change')")
    p_svc.add_argument("--cost", required=True, help="Total cost ($)")
    p_svc.add_argument("--notes", default="", help="Optional notes")
    p_svc.add_argument("--tags", default="", help="Space-separated tags")

    # add repair
    p_rep = subparsers.add_parser("add-repair", help="Add an unscheduled repair record")
    p_rep.add_argument("--vehicle-id", type=int, required=True, help="Vehicle ID")
    p_rep.add_argument("--date", default=dt_date.today().isoformat(), help="Date (YYYY-MM-DD), default: today")
    p_rep.add_argument("--odometer", required=True, help="Odometer mileage")
    p_rep.add_argument("--desc", required=True, help="Description of repair")
    p_rep.add_argument("--cost", required=True, help="Total cost ($)")
    p_rep.add_argument("--notes", default="", help="Optional notes")
    p_rep.add_argument("--tags", default="", help="Space-separated tags")

    # add odometer reading
    p_odolog = subparsers.add_parser("add-odometer", help="Log an odometer reading")
    p_odolog.add_argument("--vehicle-id", type=int, required=True, help="Vehicle ID")
    p_odolog.add_argument("--date", default=dt_date.today().isoformat(), help="Date (YYYY-MM-DD)")
    p_odolog.add_argument("--odometer", required=True, help="Odometer reading")
    p_odolog.add_argument("--notes", default="", help="Notes")

    # reminders
    p_rem = subparsers.add_parser("reminders", help="List reminders")
    p_rem.add_argument("--vehicle-id", type=int, help="Optional vehicle ID")

    # add reminder
    p_addrem = subparsers.add_parser("add-reminder", help="Add a reminder")
    p_addrem.add_argument("--vehicle-id", type=int, required=True, help="Vehicle ID")
    p_addrem.add_argument("--desc", required=True, help="Description")
    p_addrem.add_argument("--metric", choices=["Date", "Odometer", "Both"], default="Both", help="Trigger metric")
    p_addrem.add_argument("--due-date", help="Due date (YYYY-MM-DD)")
    p_addrem.add_argument("--due-odo", help="Due odometer reading")
    p_addrem.add_argument("--notes", default="", help="Notes")

    # add note
    p_note = subparsers.add_parser("add-note", help="Add a vehicle note")
    p_note.add_argument("--vehicle-id", type=int, required=True, help="Vehicle ID")
    p_note.add_argument("--desc", required=True, help="Title / Subject")
    p_note.add_argument("--text", required=True, help="Body text")
    p_note.add_argument("--pinned", action="store_true", help="Pin to dashboard")

    # delete
    p_del = subparsers.add_parser("delete", help="Delete a record")
    p_del.add_argument("--type", required=True, choices=["gas", "service", "repair", "odometer", "reminder", "note", "plan", "upgrade", "supply", "tax"])
    p_del.add_argument("--id", type=int, required=True, help="Record ID to delete")

    args = parser.parse_args()
    client = get_client()

    try:
        if args.command == "test":
            res = client.test_connection()
            print(json.dumps(res, indent=2))

        elif args.command == "vehicles":
            vehicles = client.list_vehicles()
            print(f"Found {len(vehicles)} vehicle(s):")
            for v in vehicles:
                print(f"  [{v.get('id')}] {v.get('year')} {v.get('make')} {v.get('model')} | Plate: {v.get('licensePlate')} | Tags: {v.get('tags')}")

        elif args.command == "vehicle":
            info = client.get_vehicle_info(args.vehicle_id)
            print(json.dumps(info, indent=2))

        elif args.command == "odometer":
            odo = client.get_latest_odometer(args.vehicle_id)
            print(f"Latest Odometer for Vehicle #{args.vehicle_id}: {odo}")

        elif args.command == "records":
            records = client.get_records(args.type, vehicle_id=args.vehicle_id, all_vehicles=args.all or (args.vehicle_id is None))
            print(json.dumps(records, indent=2))

        elif args.command == "add-gas":
            res = client.add_gas_record(
                vehicle_id=args.vehicle_id,
                date=args.date,
                odometer=args.odometer,
                fuel_consumed=args.fuel,
                cost=args.cost,
                is_fill_to_full=not args.partial,
                notes=args.notes,
                tags=args.tags,
            )
            print("Gas record added successfully:")
            print(json.dumps(res, indent=2))

        elif args.command == "add-service":
            res = client.add_service_record(
                vehicle_id=args.vehicle_id,
                date=args.date,
                odometer=args.odometer,
                description=args.desc,
                cost=args.cost,
                notes=args.notes,
                tags=args.tags,
            )
            print("Service record added successfully:")
            print(json.dumps(res, indent=2))

        elif args.command == "add-repair":
            res = client.add_repair_record(
                vehicle_id=args.vehicle_id,
                date=args.date,
                odometer=args.odometer,
                description=args.desc,
                cost=args.cost,
                notes=args.notes,
                tags=args.tags,
            )
            print("Repair record added successfully:")
            print(json.dumps(res, indent=2))

        elif args.command == "add-odometer":
            res = client.add_odometer_record(
                vehicle_id=args.vehicle_id,
                date=args.date,
                odometer=args.odometer,
                notes=args.notes,
            )
            print("Odometer record added successfully:")
            print(json.dumps(res, indent=2))

        elif args.command == "reminders":
            reminders = client.get_reminders(args.vehicle_id)
            print(json.dumps(reminders, indent=2))

        elif args.command == "add-reminder":
            res = client.add_reminder(
                vehicle_id=args.vehicle_id,
                description=args.desc,
                metric=args.metric,
                due_date=args.due_date,
                due_odometer=args.due_odo,
                notes=args.notes,
            )
            print("Reminder added successfully:")
            print(json.dumps(res, indent=2))

        elif args.command == "add-note":
            res = client.add_note(
                vehicle_id=args.vehicle_id,
                description=args.desc,
                note_text=args.text,
                pinned=args.pinned,
            )
            print("Note added successfully:")
            print(json.dumps(res, indent=2))

        elif args.command == "delete":
            res = client.delete_record(args.type, args.id)
            print(json.dumps(res, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
