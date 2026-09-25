---
name: lubelogger
description: >-
  Use this skill when the user wants to interact with a LubeLogger instance (self-hosted vehicle
  maintenance and fuel tracking system). Enables the agent to query vehicles, record gas/fuel fill-ups,
  log scheduled service and repairs, update odometer readings, check and manage maintenance reminders,
  add notes, and parse maintenance receipts or fuel pump photos.
---

# LubeLogger AI Assistant Skill

This skill guides AI agents in interacting with [LubeLogger](https://github.com/hargata/lubelog) to view, add, and update vehicle maintenance, fuel, odometer, and reminder records.

## Tool Capabilities & Execution Modes

Agents can interact with LubeLogger through two primary interfaces provided in this workspace:

1.  **MCP Server Tools (Recommended)**: When the LubeLogger MCP server is active in the environment:
    *   `lubelogger_list_vehicles`: List all vehicles in user's garage.
    *   `lubelogger_get_vehicle_info`: Get specifications and settings.
    *   `lubelogger_get_latest_odometer`: Fetch current odometer mileage.
    *   `lubelogger_get_records`: Retrieve logs (`gas`, `service`, `repair`, `odometer`, `reminder`, `note`, `plan`).
    *   `lubelogger_get_reminders`: Query upcoming/due maintenance reminders.
    *   `lubelogger_add_gas_record`: Record fuel or EV charging.
    *   `lubelogger_add_service_record`: Record scheduled routine service.
    *   `lubelogger_add_repair_record`: Record unscheduled repairs.
    *   `lubelogger_add_odometer_record`: Log an odometer checkpoint.
    *   `lubelogger_add_reminder`: Schedule a date/mileage reminder.
    *   `lubelogger_add_note`: Attach notes to a vehicle.
    *   `lubelogger_add_plan_record`: Add a task to the maintenance planner backlog.
    *   `lubelogger_update_record`: Update existing records.
    *   `lubelogger_delete_record`: Delete a record by ID.
2.  **CLI Helper Scripts**: When running in a terminal or scripting workflow:
    *   `python3 scripts/lubelogger_cli.py <command>`
    *   `python3 scripts/test_connection.py`

Detailed documentation:
*   [REST API Reference](./references/api_reference.md)
*   [Data Models & Schemas](./references/data_models.md)
*   [Conversation Flows & Examples](./examples/conversation_flows.md)

---

## Standard Workflows & Procedures

### Workflow 1: Logging Fuel / Gas Fill-Ups

When a user mentions buying gas, charging, or filling up a vehicle:

1.  **Identify Vehicle:**
    *   If vehicle name, nickname, or plate is mentioned (e.g. "Civic", "Jeep", "truck"), match against `lubelogger_list_vehicles()`.
    *   If only one vehicle exists in the garage, automatically select it.
    *   If multiple vehicles exist and none is specified, prompt the user to clarify.
2.  **Odometer Verification:**
    *   Call `lubelogger_get_latest_odometer(vehicle_id)`.
    *   Compare the new reading against the latest recorded reading.
    *   If the new reading is lower than the previous odometer, confirm with the user before writing (to prevent typos).
3.  **Field Extraction & Normalization:**
    *   `date`: Default to today's date in `YYYY-MM-DD` unless the user specifies otherwise ("yesterday", "Sunday").
    *   `fuel_consumed`: Number of gallons/liters. If user provides price-per-gallon and total cost instead (e.g., "$40 total at $3.25/gal"), calculate `fuel_consumed = 40 / 3.25 = 12.31`.
    *   `cost`: Total dollar amount paid.
    *   `is_fill_to_full`: Set `True` unless user explicitly notes a partial fill ("put in $15", "half tank").
    *   `missed_fuel_up`: Set `False` by default; set `True` if user says they forgot to log the previous tank.
4.  **Execute:** Call `lubelogger_add_gas_record()`.
5.  **Confirm:** Present a concise confirmation showing date, odometer, gallons, total cost, and calculated MPG if previous odometer was available.

---

### Workflow 2: Logging Scheduled Maintenance vs. Unscheduled Repairs

1.  **Distinguish Category:**
    *   **Routine / Scheduled Service** (`lubelogger_add_service_record`): Oil change, filter replacement, tire rotation, brake pad replacement, scheduled interval inspection, fluid flush.
    *   **Unscheduled Repair** (`lubelogger_add_repair_record`): Alternator failure, water pump leak, puncture patch, sensor replacement, collision repair.
2.  **Check for Active Reminders:**
    *   Call `lubelogger_get_reminders(vehicle_id)`.
    *   Check if an active reminder exists for the completed service (e.g., "Oil Change", "Tire Rotation").
    *   After adding the service record, inform the user about the existing reminder and offer to advance or update its due date/mileage.
3.  **Execute Record Addition:**
    *   `date`: Service date (`YYYY-MM-DD`).
    *   `odometer`: Current mileage.
    *   `description`: Clear summary of the work.
    *   `cost`: Parts + labor total cost.
    *   `notes`: Specific part numbers, oil grade/spec (e.g., "5.1 qts 0W-20, OEM filter"), shop name, or invoice numbers.
4.  **Confirm:** Summarize the logged service and any reminder adjustments.

---

### Workflow 3: Updating Existing Records

When a user asks to correct or update a previous entry:
1.  Query recent records of that type using `lubelogger_get_records(record_type, vehicle_id)`.
2.  Identify the target record by matching date, description, or mileage.
3.  Merge the user's updates with existing fields, ensuring the record's `"id"` is preserved.
4.  Call `lubelogger_update_record(record_type, record_data)`.
5.  Confirm the updated values with the user.

---

### Workflow 4: Ingesting Receipts & Maintenance Invoices

When the user uploads or pastes a receipt, service ticket, or fuel pump summary:
1.  **Extract Key Fields:**
    *   Vendor / Shop Name (e.g., "Valvoline Instant Oil Change", "Discount Tire")
    *   Date of service
    *   Vehicle odometer (often printed on the ticket)
    *   Line items & descriptions
    *   Subtotal, taxes, and total cost
2.  **Pre-Flight Verification:**
    *   Show the user the extracted fields before committing, especially if multiple vehicles or high-dollar services are involved.
3.  **Record Creation:**
    *   Log as Service or Repair record.
    *   Include itemized parts and fluid specifications in `notes`.

---

### Workflow 5: Managing Reminders

1.  **Querying Reminders:**
    *   Call `lubelogger_get_reminders(vehicle_id)`.
    *   Report status clearly: indicate whether items are `NotUrgent`, `Urgent` (approaching due threshold), or `VeryUrgent` (past due date or mileage).
2.  **Creating a Reminder:**
    *   Determine metric: `"Date"`, `"Odometer"`, or `"Both"`.
    *   Calculate targets (e.g. "remind me in 5,000 miles" -> current odometer + 5,000; "remind me in 6 months" -> current date + 180 days).
    *   Call `lubelogger_add_reminder()`.

---

## Best Practices & Guidelines

*   **Never invent vehicle IDs**: Always call `lubelogger_list_vehicles` first to retrieve real vehicle IDs and names.
*   **Sanity-check odometers**: If a new entry's odometer is lower than the last recorded reading, explicitly alert the user to prevent corrupted fuel economy calculations.
*   **Keep notes informative**: Include oil viscosities, filter part numbers, tire rotation patterns, and shop names in `notes` for future reference.
*   **Currency & Units**: Respect the user's local units (gallons vs. liters, miles vs. kilometers, USD/EUR/CAD) as configured in their LubeLogger instance.
