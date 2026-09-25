# LubeLogger AI Skill & MCP Server

A complete Model Context Protocol (MCP) server and Antigravity Skill for interacting with [LubeLogger](https://github.com/hargata/lubelog) — the open-source, self-hosted vehicle maintenance and fuel tracking application.

This package enables conversational AI assistants (Antigravity, Claude Desktop, Cursor, ChatGPT, etc.) to query vehicles, add and update gas logs, record routine service and repair tickets, log odometer readings, check maintenance reminders, attach notes, and parse maintenance receipts.

---

## ✨ Features

- **Zero-Dependency Python MCP Server**: Runs on standard Python 3.10+ using pure standard library (`urllib`, `json`, `sys`). No `pip install` required.
- **Full LubeLogger REST API Coverage**:
  - **Vehicles**: List vehicles, query specs, retrieve dashboard metrics.
  - **Fuel / Gas Records**: Add, update, and query fuel fill-ups (fuel amount, cost, odometer, full vs. partial tank, EV kWh support).
  - **Service Records**: Scheduled maintenance (oil changes, tire rotations, fluid flushes, inspections).
  - **Repair Records**: Unscheduled repairs (parts failures, brake fixes, alternator replacements).
  - **Odometer Readings**: Log mileage checkpoints and fetch latest odometer readings.
  - **Reminders**: Query upcoming/overdue maintenance and create new reminders by date or mileage.
  - **Notes & Planner**: Attach pinned vehicle notes and manage maintenance backlog tasks.
  - **Update & Delete**: Full update and delete support across all record types.
- **Antigravity Skill (`SKILL.md`)**: Intelligent runbook that teaches the AI agent how to extract entities from natural language, handle relative dates, sanity-check odometer readings against historical records, and cross-reference active reminders.
- **CLI Utility**: Includes `scripts/lubelogger_cli.py` for direct command-line operations and automated shell scripting.
- **Diagnostic Tool**: Includes `scripts/test_connection.py` to verify API connectivity and credentials.

---

## 📁 Directory Structure

```text
lubelogger/
├── SKILL.md                          # Antigravity Skill definition & runbook
├── plugin.json                       # Antigravity plugin manifest
├── mcp_config.example.json           # Sample MCP server configuration
├── .env.example                      # Configuration template
├── README.md                         # Documentation & setup guide
├── mcp_server/
│   ├── __init__.py
│   ├── client.py                     # LubeLogger REST API client
│   └── server.py                     # MCP stdio server (JSON-RPC 2.0)
├── scripts/
│   ├── lubelogger_cli.py             # CLI utility for command-line management
│   └── test_connection.py           # Diagnostic connectivity test script
├── references/
│   ├── api_reference.md              # Detailed REST API endpoint documentation
│   └── data_models.md                # Schema definitions for all records
└── examples/
    └── conversation_flows.md         # Multi-turn conversational flow examples
```

---

## 🚀 Quickstart

### 1. Configure Credentials

Create a `.env` file from the provided template:

```bash
cp .env.example .env
```

Edit `.env` with your instance details:

```env
LUBELOGGER_URL=http://localhost:5000
LUBELOGGER_API_KEY=your_generated_api_key
LUBELOGGER_VERIFY_SSL=true
```

> 💡 **How to generate an API key in LubeLogger:**
> 1. Log in to your LubeLogger web UI.
> 2. Click your username in the top right > **Settings** (or Admin panel).
> 3. Navigate to **API Keys** and generate a new key with `Editor` or `Manager` permissions.

### 2. Test Connection

Run the built-in diagnostic script:

```bash
python3 scripts/test_connection.py
```

Expected output:
```text
============================================================
 LUBELOGGER CONNECTION DIAGNOSTICS
============================================================
Target URL: http://localhost:5000
Auth Method: API Key (abcd...wxyz)
------------------------------------------------------------
[1/4] Checking server reachability and API version...
  ✅ Connected successfully! LubeLogger version: 1.7.3
[2/4] Testing vehicle list query...
  ✅ Found 2 vehicle(s):
     - [ID: 1] 2021 Subaru Outback (Plate: ABC1234)
     - [ID: 2] 1992 Jeep Cherokee (Plate: MOMWAGON)
[3/4] Testing odometer query on Vehicle ID 1...
  ✅ Latest odometer reading: 54200
[4/4] Testing reminder query on Vehicle ID 1...
  ✅ Found 1 active reminder(s).
------------------------------------------------------------
✅ All diagnostic checks completed successfully!
============================================================
```

---

## 🤖 Configuring with AI Clients

### 1. Antigravity IDE / CLI

#### Option A: Project Workspace (Automatic)
Keep this repository in your project directory or point your workspace to it. Copy `mcp_config.example.json` to `mcp_config.json` and adjust paths/URLs as needed. The `plugin.json` and `mcp_config.json` will be detected automatically.

#### Option B: Global MCP Configuration
Add the server entry to your global configuration file `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "lubelogger": {
      "command": "/opt/homebrew/bin/python3",
      "args": ["/Users/neelesteele/projects/skills/lubelogger/mcp_server/server.py"],
      "env": {
        "LUBELOGGER_URL": "http://localhost:5000",
        "LUBELOGGER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 2. Claude Desktop

Add the server to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lubelogger": {
      "command": "/opt/homebrew/bin/python3",
      "args": ["/Users/neelesteele/projects/skills/lubelogger/mcp_server/server.py"],
      "env": {
        "LUBELOGGER_URL": "http://localhost:5000",
        "LUBELOGGER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 3. Cursor / Continue / Other MCP Clients

Configure the stdio command:
- **Command:** `python3`
- **Arguments:** `["/path/to/lubelogger/mcp_server/server.py"]`
- **Environment:** `LUBELOGGER_URL`, `LUBELOGGER_API_KEY`

---

## 🛠️ Available MCP Tools

| Tool Name | Description |
| :--- | :--- |
| `lubelogger_test_connection` | Test connectivity, authentication, and server version. |
| `lubelogger_list_vehicles` | List all vehicles with IDs, make, model, year, and license plate. |
| `lubelogger_get_vehicle_info` | Get detailed vehicle specs and settings. |
| `lubelogger_get_latest_odometer` | Get the most recent odometer mileage for a vehicle. |
| `lubelogger_get_records` | Query records of any type (`gas`, `service`, `repair`, `odometer`, `reminder`, `note`, `plan`). |
| `lubelogger_get_reminders` | Query upcoming and overdue maintenance reminders. |
| `lubelogger_add_gas_record` | Add fuel/gas/EV charging fill-up log. |
| `lubelogger_add_service_record` | Add routine scheduled maintenance (oil change, tire rotation, etc.). |
| `lubelogger_add_repair_record` | Add unscheduled repair record. |
| `lubelogger_add_odometer_record` | Record an odometer reading checkpoint. |
| `lubelogger_add_reminder` | Create a maintenance reminder (Date, Odometer, or Both). |
| `lubelogger_add_note` | Add a text memo or reference note to a vehicle. |
| `lubelogger_add_plan_record` | Add an item to the maintenance planning backlog. |
| `lubelogger_update_record` | Update an existing record of any type by ID. |
| `lubelogger_delete_record` | Delete a record by type and ID. |

---

## 💻 CLI Usage Guide

You can also use `scripts/lubelogger_cli.py` directly from the command line:

```bash
# List all vehicles
python3 scripts/lubelogger_cli.py vehicles

# Get latest odometer
python3 scripts/lubelogger_cli.py odometer 1

# Add a gas fill-up
python3 scripts/lubelogger_cli.py add-gas --vehicle-id 1 --odometer 54520 --fuel 13.5 --cost 44.00 --notes "Shell 87"

# Add an oil change service record
python3 scripts/lubelogger_cli.py add-service --vehicle-id 1 --odometer 54520 --desc "Oil & Filter Change" --cost 38.50 --notes "Mobil 1 0W-20"

# List reminders
python3 scripts/lubelogger_cli.py reminders --vehicle-id 1

# Add a reminder for 5,000 miles ahead
python3 scripts/lubelogger_cli.py add-reminder --vehicle-id 1 --desc "Tire Rotation" --metric Odometer --due-odo 59520

# Query past gas records
python3 scripts/lubelogger_cli.py records gas --vehicle-id 1
```

---

## 🧪 Testing Against the Public Demo Instance

To test without deploying a local container:

```bash
python3 mcp_server/server.py --url https://demo.lubelogger.com --username test --password 1234 --test
```
