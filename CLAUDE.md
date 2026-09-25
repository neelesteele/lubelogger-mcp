# LubeLogger Assistant Guidelines (Claude)

This repository provides an MCP server and assistant guidelines for interacting with a self-hosted [LubeLogger](https://github.com/hargata/lubelog) instance.

When interacting with LubeLogger via the available MCP tools (`lubelogger_*`) or CLI scripts:

## Core Workflows

1. **Fuel / Gas Fill-Ups (`lubelogger_add_gas_record`)**:
   - Resolve vehicle: Call `lubelogger_list_vehicles` if vehicle is ambiguous or unspecified.
   - Odometer sanity check: Call `lubelogger_get_latest_odometer(vehicle_id)` and verify the new reading is equal or higher than the previous record.
   - Parse units: Calculate gallons if user only provided total cost and price/gal (`fuel = total / price_per_gal`).
   - Fill status: Default `is_fill_to_full=true` unless user indicates partial fill.

2. **Maintenance & Repairs (`lubelogger_add_service_record` / `lubelogger_add_repair_record`)**:
   - Routine Service: Oil changes, tire rotations, brake pad replacements, fluid flushes, inspections.
   - Repairs: Broken parts, alternator replacements, leak fixes.
   - Reminders Check: Always call `lubelogger_get_reminders(vehicle_id)` before/after logging service. If an active reminder matches the completed service, inform the user and offer to advance or update it.

3. **Updating & Deleting Records**:
   - Query existing records via `lubelogger_get_records(record_type, vehicle_id)`.
   - Update using `lubelogger_update_record(record_type, record_data)` ensuring the record's `id` is included.

4. **Receipt & Invoice Parsing**:
   - When a receipt or shop invoice is attached, extract: vendor/shop, date, odometer, line items, and total cost. Present the summary to the user before submitting.

Refer to [SKILL.md](file:///Users/neelesteele/projects/skills/lubelogger/SKILL.md) and [references/api_reference.md](file:///Users/neelesteele/projects/skills/lubelogger/references/api_reference.md) for full endpoint and schema details.
