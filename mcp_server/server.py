#!/usr/bin/env python3
"""
LubeLogger Model Context Protocol (MCP) Server
Implements MCP over stdio (JSON-RPC 2.0) with zero external dependencies.
Compatible with Antigravity, Claude Desktop, Cursor, and any MCP client.
"""

import sys
import os
import json
import argparse
from typing import Any, Dict, List, Optional

# Ensure client module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_server.client import LubeLoggerClient, load_dotenv

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "lubelogger-mcp"
SERVER_VERSION = "1.0.0"

# Tool Definitions
TOOLS = [
    {
        "name": "lubelogger_test_connection",
        "description": "Test connectivity, credentials, and API version against the configured LubeLogger instance.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "lubelogger_list_vehicles",
        "description": "List all vehicles the user has access to, including vehicle ID, year, make, model, license plate, and tags.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "lubelogger_get_vehicle_info",
        "description": "Get detailed information, specs, and settings for a specific vehicle or all vehicles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "integer",
                    "description": "Optional ID of the vehicle. If omitted, returns details for all vehicles.",
                }
            },
        },
    },
    {
        "name": "lubelogger_get_latest_odometer",
        "description": "Get the most recent odometer mileage reading recorded for a specific vehicle.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "integer",
                    "description": "Vehicle ID to query.",
                }
            },
            "required": ["vehicle_id"],
        },
    },
    {
        "name": "lubelogger_get_records",
        "description": "Retrieve records of a specific type (e.g., gas, service, repair, odometer, reminder, note, plan, upgrade) for a vehicle or across all vehicles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "record_type": {
                    "type": "string",
                    "description": "Type of record to fetch: 'gas', 'service', 'repair', 'odometer', 'reminder', 'note', 'plan', 'upgrade', 'supply', 'tax'.",
                    "enum": ["gas", "service", "repair", "odometer", "reminder", "note", "plan", "upgrade", "supply", "tax"],
                },
                "vehicle_id": {
                    "type": "integer",
                    "description": "Vehicle ID to query. If omitted, queries across all vehicles.",
                },
                "all_vehicles": {
                    "type": "boolean",
                    "description": "Set to true to query across all vehicles regardless of vehicle_id.",
                    "default": False,
                },
            },
            "required": ["record_type"],
        },
    },
    {
        "name": "lubelogger_get_reminders",
        "description": "Retrieve active maintenance reminders (due date, due odometer, urgency) for a specific vehicle or all vehicles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "integer",
                    "description": "Optional vehicle ID. If omitted, returns reminders across all vehicles.",
                }
            },
        },
    },
    {
        "name": "lubelogger_add_gas_record",
        "description": "Add a fuel fill-up or EV charging record for a vehicle.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "integer",
                    "description": "ID of the vehicle.",
                },
                "date": {
                    "type": "string",
                    "description": "Date of fill-up in YYYY-MM-DD or MM/DD/YYYY format.",
                },
                "odometer": {
                    "type": ["integer", "string"],
                    "description": "Current odometer mileage at time of fuel up.",
                },
                "fuel_consumed": {
                    "type": ["number", "string"],
                    "description": "Units of fuel consumed (gallons or liters, or kWh for EV).",
                },
                "cost": {
                    "type": ["number", "string"],
                    "description": "Total monetary cost of the fuel purchase.",
                },
                "is_fill_to_full": {
                    "type": "boolean",
                    "description": "Whether the tank was filled to full capacity (default: true). Set false for partial fills.",
                    "default": True,
                },
                "missed_fuel_up": {
                    "type": "boolean",
                    "description": "Whether a prior fuel-up between the previous log and this one was missed.",
                    "default": False,
                },
                "notes": {
                    "type": "string",
                    "description": "Optional notes (e.g. gas station brand, octane rating, fuel price per gallon).",
                    "default": "",
                },
                "tags": {
                    "type": "string",
                    "description": "Optional space-separated tags (e.g. 'shell premium roadtrip').",
                    "default": "",
                },
                "starting_soc": {
                    "type": "integer",
                    "description": "Optional starting battery state of charge (EV only).",
                },
                "ending_soc": {
                    "type": "integer",
                    "description": "Optional ending battery state of charge (EV only).",
                },
            },
            "required": ["vehicle_id", "date", "odometer", "fuel_consumed", "cost"],
        },
    },
    {
        "name": "lubelogger_add_service_record",
        "description": "Add a scheduled/routine maintenance record (e.g., oil change, tire rotation, transmission flush, brake pads) for a vehicle.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "integer",
                    "description": "ID of the vehicle.",
                },
                "date": {
                    "type": "string",
                    "description": "Date of service in YYYY-MM-DD or MM/DD/YYYY format.",
                },
                "odometer": {
                    "type": ["integer", "string"],
                    "description": "Odometer mileage at time of service.",
                },
                "description": {
                    "type": "string",
                    "description": "Summary description of work performed (e.g. 'Oil Change and Filter', 'Tire Rotation').",
                },
                "cost": {
                    "type": ["number", "string"],
                    "description": "Total cost of service (parts + labor).",
                },
                "notes": {
                    "type": "string",
                    "description": "Detailed notes, part numbers, oil brand/weight, service shop name, or invoice details.",
                    "default": "",
                },
                "tags": {
                    "type": "string",
                    "description": "Optional space-separated tags (e.g. 'diy synthetic dealer').",
                    "default": "",
                },
            },
            "required": ["vehicle_id", "date", "odometer", "description", "cost"],
        },
    },
    {
        "name": "lubelogger_add_repair_record",
        "description": "Add an unscheduled repair record (e.g., alternator replacement, flat tire repair, radiator leak) for a vehicle.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "integer",
                    "description": "ID of the vehicle.",
                },
                "date": {
                    "type": "string",
                    "description": "Date of repair in YYYY-MM-DD or MM/DD/YYYY format.",
                },
                "odometer": {
                    "type": ["integer", "string"],
                    "description": "Odometer mileage at time of repair.",
                },
                "description": {
                    "type": "string",
                    "description": "Description of repair work performed.",
                },
                "cost": {
                    "type": ["number", "string"],
                    "description": "Total cost of repair.",
                },
                "notes": {
                    "type": "string",
                    "description": "Detailed notes on diagnosis, parts replaced, or mechanic notes.",
                    "default": "",
                },
                "tags": {
                    "type": "string",
                    "description": "Optional space-separated tags.",
                    "default": "",
                },
            },
            "required": ["vehicle_id", "date", "odometer", "description", "cost"],
        },
    },
    {
        "name": "lubelogger_add_odometer_record",
        "description": "Record an odometer reading checkpoint for a vehicle without adding a fuel or service log.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "integer",
                    "description": "ID of the vehicle.",
                },
                "date": {
                    "type": "string",
                    "description": "Date of reading in YYYY-MM-DD or MM/DD/YYYY format.",
                },
                "odometer": {
                    "type": ["integer", "string"],
                    "description": "Current odometer reading.",
                },
                "initial_odometer": {
                    "type": ["integer", "string"],
                    "description": "Optional initial odometer reading. If omitted, uses the last recorded odometer.",
                },
                "notes": {
                    "type": "string",
                    "description": "Optional notes.",
                    "default": "",
                },
                "tags": {
                    "type": "string",
                    "description": "Optional space-separated tags.",
                    "default": "",
                },
            },
            "required": ["vehicle_id", "date", "odometer"],
        },
    },
    {
        "name": "lubelogger_add_reminder",
        "description": "Add a maintenance reminder based on Due Date, Due Odometer, or Both for a vehicle.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "integer",
                    "description": "ID of the vehicle.",
                },
                "description": {
                    "type": "string",
                    "description": "Description of reminder (e.g. 'Tire Rotation', 'Brake Fluid Flush').",
                },
                "metric": {
                    "type": "string",
                    "description": "Reminder trigger metric: 'Date', 'Odometer', or 'Both'.",
                    "enum": ["Date", "Odometer", "Both"],
                    "default": "Both",
                },
                "due_date": {
                    "type": "string",
                    "description": "Target due date (required if metric is Date or Both), format YYYY-MM-DD.",
                },
                "due_odometer": {
                    "type": ["integer", "string"],
                    "description": "Target due odometer mileage (required if metric is Odometer or Both).",
                },
                "notes": {
                    "type": "string",
                    "description": "Optional notes for the reminder.",
                    "default": "",
                },
                "tags": {
                    "type": "string",
                    "description": "Optional tags.",
                    "default": "",
                },
            },
            "required": ["vehicle_id", "description", "metric"],
        },
    },
    {
        "name": "lubelogger_add_note",
        "description": "Add a text note or memo (optionally pinned to dashboard) for a vehicle.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "integer",
                    "description": "ID of the vehicle.",
                },
                "description": {
                    "type": "string",
                    "description": "Title or subject of the note.",
                },
                "note_text": {
                    "type": "string",
                    "description": "Full body text of the note.",
                },
                "pinned": {
                    "type": "boolean",
                    "description": "Whether to pin this note to the top of the vehicle page (default: false).",
                    "default": False,
                },
                "tags": {
                    "type": "string",
                    "description": "Optional space-separated tags.",
                    "default": "",
                },
            },
            "required": ["vehicle_id", "description", "note_text"],
        },
    },
    {
        "name": "lubelogger_add_plan_record",
        "description": "Add a planned maintenance, upgrade, or repair task to the vehicle planner backlog.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vehicle_id": {
                    "type": "integer",
                    "description": "ID of the vehicle.",
                },
                "description": {
                    "type": "string",
                    "description": "Description of the planned task.",
                },
                "cost": {
                    "type": ["number", "string"],
                    "description": "Estimated cost.",
                    "default": 0.0,
                },
                "type": {
                    "type": "string",
                    "description": "Record target type: 'ServiceRecord', 'RepairRecord', 'UpgradeRecord'.",
                    "default": "ServiceRecord",
                },
                "priority": {
                    "type": "string",
                    "description": "Priority level: 'Critical', 'Normal', 'Low'.",
                    "default": "Normal",
                },
                "progress": {
                    "type": "string",
                    "description": "Progress state: 'Backlog', 'InProgress', 'Testing', 'Done'.",
                    "default": "Backlog",
                },
                "notes": {
                    "type": "string",
                    "description": "Optional notes.",
                    "default": "",
                },
            },
            "required": ["vehicle_id", "description"],
        },
    },
    {
        "name": "lubelogger_update_record",
        "description": "Update an existing record of any type (gas, service, repair, odometer, reminder, note, etc.). The record_data object must contain 'id'.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "record_type": {
                    "type": "string",
                    "description": "Type of record to update ('gas', 'service', 'repair', 'odometer', 'reminder', 'note', 'plan', 'upgrade').",
                    "enum": ["gas", "service", "repair", "odometer", "reminder", "note", "plan", "upgrade"],
                },
                "record_data": {
                    "type": "object",
                    "description": "Object containing the updated fields and the required 'id' of the record.",
                },
            },
            "required": ["record_type", "record_data"],
        },
    },
    {
        "name": "lubelogger_delete_record",
        "description": "Delete a record from LubeLogger by record type and record ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "record_type": {
                    "type": "string",
                    "description": "Type of record: 'gas', 'service', 'repair', 'odometer', 'reminder', 'note', 'plan', 'upgrade', 'supply', 'tax'.",
                    "enum": ["gas", "service", "repair", "odometer", "reminder", "note", "plan", "upgrade", "supply", "tax"],
                },
                "record_id": {
                    "type": "integer",
                    "description": "ID of the record to delete.",
                },
            },
            "required": ["record_type", "record_id"],
        },
    },
]


def execute_tool(client: LubeLoggerClient, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Dispatches a tool call to the client."""
    if tool_name == "lubelogger_test_connection":
        return client.test_connection()

    elif tool_name == "lubelogger_list_vehicles":
        return client.list_vehicles()

    elif tool_name == "lubelogger_get_vehicle_info":
        return client.get_vehicle_info(arguments.get("vehicle_id"))

    elif tool_name == "lubelogger_get_latest_odometer":
        return client.get_latest_odometer(arguments["vehicle_id"])

    elif tool_name == "lubelogger_get_records":
        return client.get_records(
            record_type=arguments["record_type"],
            vehicle_id=arguments.get("vehicle_id"),
            all_vehicles=arguments.get("all_vehicles", False),
        )

    elif tool_name == "lubelogger_get_reminders":
        return client.get_reminders(arguments.get("vehicle_id"))

    elif tool_name == "lubelogger_add_gas_record":
        return client.add_gas_record(
            vehicle_id=arguments["vehicle_id"],
            date=arguments["date"],
            odometer=arguments["odometer"],
            fuel_consumed=arguments["fuel_consumed"],
            cost=arguments["cost"],
            is_fill_to_full=arguments.get("is_fill_to_full", True),
            missed_fuel_up=arguments.get("missed_fuel_up", False),
            notes=arguments.get("notes", ""),
            tags=arguments.get("tags", ""),
            starting_soc=arguments.get("starting_soc"),
            ending_soc=arguments.get("ending_soc"),
        )

    elif tool_name == "lubelogger_add_service_record":
        return client.add_service_record(
            vehicle_id=arguments["vehicle_id"],
            date=arguments["date"],
            odometer=arguments["odometer"],
            description=arguments["description"],
            cost=arguments["cost"],
            notes=arguments.get("notes", ""),
            tags=arguments.get("tags", ""),
        )

    elif tool_name == "lubelogger_add_repair_record":
        return client.add_repair_record(
            vehicle_id=arguments["vehicle_id"],
            date=arguments["date"],
            odometer=arguments["odometer"],
            description=arguments["description"],
            cost=arguments["cost"],
            notes=arguments.get("notes", ""),
            tags=arguments.get("tags", ""),
        )

    elif tool_name == "lubelogger_add_odometer_record":
        return client.add_odometer_record(
            vehicle_id=arguments["vehicle_id"],
            date=arguments["date"],
            odometer=arguments["odometer"],
            initial_odometer=arguments.get("initial_odometer"),
            notes=arguments.get("notes", ""),
            tags=arguments.get("tags", ""),
        )

    elif tool_name == "lubelogger_add_reminder":
        return client.add_reminder(
            vehicle_id=arguments["vehicle_id"],
            description=arguments["description"],
            metric=arguments.get("metric", "Both"),
            due_date=arguments.get("due_date"),
            due_odometer=arguments.get("due_odometer"),
            notes=arguments.get("notes", ""),
            tags=arguments.get("tags", ""),
        )

    elif tool_name == "lubelogger_add_note":
        return client.add_note(
            vehicle_id=arguments["vehicle_id"],
            description=arguments["description"],
            note_text=arguments["note_text"],
            pinned=arguments.get("pinned", False),
            tags=arguments.get("tags", ""),
        )

    elif tool_name == "lubelogger_add_plan_record":
        return client.add_plan_record(
            vehicle_id=arguments["vehicle_id"],
            description=arguments["description"],
            cost=arguments.get("cost", 0.0),
            type=arguments.get("type", "ServiceRecord"),
            priority=arguments.get("priority", "Normal"),
            progress=arguments.get("progress", "Backlog"),
            notes=arguments.get("notes", ""),
        )

    elif tool_name == "lubelogger_update_record":
        return client.update_record(
            record_type=arguments["record_type"],
            record_data=arguments["record_data"],
        )

    elif tool_name == "lubelogger_delete_record":
        return client.delete_record(
            record_type=arguments["record_type"],
            record_id=arguments["record_id"],
        )

    else:
        raise ValueError(f"Unknown tool: '{tool_name}'")


def run_stdio_server(client: LubeLoggerClient):
    """Run JSON-RPC 2.0 stdio loop for MCP protocol."""
    # Ensure stdout is unbuffered UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            try:
                req = json.loads(line)
            except json.JSONDecodeError as err:
                sys.stderr.write(f"Invalid JSON: {err}\n")
                continue

            msg_id = req.get("id")
            method = req.get("method", "")
            params = req.get("params", {})

            # Notification handling (no reply required)
            if method == "notifications/initialized":
                continue

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {
                            "tools": {},
                        },
                        "serverInfo": {
                            "name": SERVER_NAME,
                            "version": SERVER_VERSION,
                        },
                    },
                }
            elif method == "ping":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {},
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": TOOLS,
                    },
                }
            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                try:
                    result = execute_tool(client, tool_name, tool_args)
                    formatted_text = json.dumps(result, indent=2, default=str) if not isinstance(result, str) else result
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": formatted_text,
                                }
                            ],
                            "isError": False,
                        },
                    }
                except Exception as ex:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error executing tool '{tool_name}': {str(ex)}",
                                }
                            ],
                            "isError": True,
                        },
                    }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found",
                    },
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        except Exception as e:
            sys.stderr.write(f"MCP Server error: {e}\n")
            sys.stderr.flush()


def main():
    parser = argparse.ArgumentParser(description="LubeLogger MCP Server")
    parser.add_argument("--url", help="LubeLogger base URL (overrides LUBELOGGER_URL)")
    parser.add_argument("--api-key", help="LubeLogger API Key (overrides LUBELOGGER_API_KEY)")
    parser.add_argument("--username", help="LubeLogger Username for Basic Auth")
    parser.add_argument("--password", help="LubeLogger Password for Basic Auth")
    parser.add_argument("--no-verify-ssl", action="store_true", help="Disable SSL verification")
    parser.add_argument("--test", action="store_true", help="Test connection and exit")
    parser.add_argument("--list-tools", action="store_true", help="Print available tools and exit")

    args = parser.parse_args()

    client = LubeLoggerClient(
        base_url=args.url,
        api_key=args.api_key,
        username=args.username,
        password=args.password,
        verify_ssl=not args.no_verify_ssl,
    )

    if args.list_tools:
        print(json.dumps(TOOLS, indent=2))
        return

    if args.test:
        res = client.test_connection()
        print(json.dumps(res, indent=2))
        sys.exit(0 if res.get("success") else 1)

    run_stdio_server(client)


if __name__ == "__main__":
    main()
