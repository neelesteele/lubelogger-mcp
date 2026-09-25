# LubeLogger AI Conversation Flows & Interaction Examples

This guide illustrates typical conversation flows between a user and an AI agent equipped with the LubeLogger skill and MCP server.

---

## Flow 1: Quick Gas Log from Natural Language

### User Prompt
> "Just filled up the Outback. 12.8 gallons for $41.50 at 64,210 miles."

### AI Agent Reasoning & Execution Steps
1.  **Vehicle Resolution:**
    *   Calls `lubelogger_list_vehicles()`.
    *   Finds matching vehicle: `2021 Subaru Outback` (Vehicle ID `1`).
2.  **Validation & Pre-flight:**
    *   Calls `lubelogger_get_latest_odometer(vehicle_id=1)`.
    *   Returns `63,890`. New reading `64,210` is +320 miles (valid).
3.  **Entity Extraction:**
    *   Date: Today's date (`2026-09-25`)
    *   Odometer: `64210`
    *   Fuel Consumed: `12.8` gallons
    *   Cost: `$41.50`
    *   Calculated price/gal: `$3.242/gal`
    *   Tank fill: Full (`is_fill_to_full=true`)
4.  **Tool Execution:**
    *   Calls `lubelogger_add_gas_record(vehicle_id=1, date="2026-09-25", odometer=64210, fuel_consumed=12.8, cost=41.50, is_fill_to_full=True)`
5.  **User Response:**
    > "✅ **Logged Gas Fill-Up for 2021 Subaru Outback:**
    > - **Date:** Sept 25, 2026
    > - **Odometer:** 64,210 mi (+320 mi since last fill-up)
    > - **Fuel:** 12.8 gal @ $3.24/gal ($41.50 total)
    > - **Calculated Economy:** ~25.0 MPG"

---

## Flow 2: Maintenance Record with Active Reminder Check

### User Prompt
> "Did an oil change and rotated tires on the Jeep yesterday at 223,000 miles. Cost $45 for oil and filter."

### AI Agent Reasoning & Execution Steps
1.  **Vehicle Resolution:** Matches "Jeep" to `1992 Jeep Cherokee` (`vehicleId: 1`).
2.  **Date Resolution:** Resolves "yesterday" using local reference date to `2026-09-24`.
3.  **Active Reminder Query:**
    *   Calls `lubelogger_get_reminders(vehicle_id=1)`.
    *   Finds reminder: `[ID: 1] Oil Change (Due at 225,000 mi)`.
4.  **Tool Execution:**
    *   Calls `lubelogger_add_service_record(vehicle_id=1, date="2026-09-24", odometer=223000, description="Oil Change & Tire Rotation", cost=45.00, notes="Oil and filter replaced. Tires rotated.")`.
5.  **User Response & Reminder Update:**
    > "✅ **Added Service Record for 1992 Jeep Cherokee:**
    > - **Service:** Oil Change & Tire Rotation
    > - **Date:** Sept 24, 2026
    > - **Odometer:** 223,000 mi
    > - **Cost:** $45.00
    >
    > 💡 *Note: You have an existing reminder for **Oil Change** due at 225,000 miles. Would you like me to update it for the next interval (e.g., at 228,000 miles)?*"

---

## Flow 3: Ingesting a Repair Receipt / Invoice

### User Prompt
> "Here is my receipt from the shop: [Attachment: invoice_firestone.pdf]
> Work done on the Civic: replaced front brake pads and rotors, total was $389.20. Mileage on ticket is 88,450."

### AI Agent Reasoning & Execution Steps
1.  **Extract Data:**
    *   Vehicle: Honda Civic
    *   Type: Repair / Service Record
    *   Description: "Front Brake Pads and Rotors Replacement"
    *   Cost: `389.20`
    *   Odometer: `88450`
    *   Vendor: Firestone Complete Auto Care
2.  **Tool Execution:**
    *   Calls `lubelogger_add_repair_record(vehicle_id=2, date="2026-09-25", odometer=88450, description="Front Brake Pads and Rotors Replacement", cost=389.20, notes="Serviced at Firestone Complete Auto Care.")`.
3.  **User Response:**
    > "✅ **Logged Repair for Honda Civic:**
    > - **Description:** Front Brake Pads and Rotors Replacement
    > - **Vendor:** Firestone Complete Auto Care
    > - **Cost:** $389.20
    > - **Mileage:** 88,450 mi"

---

## Flow 4: Maintenance Status & Upcoming Due Items

### User Prompt
> "What maintenance is coming up on my cars?"

### AI Agent Reasoning & Execution Steps
1.  **Tool Execution:**
    *   Calls `lubelogger_get_reminders()`.
    *   Calls `lubelogger_list_vehicles()`.
2.  **Aggregation:**
    *   Correlates reminders with vehicle names and latest odometers.
3.  **User Response:**
    > "Here is the current maintenance status across your garage:
    >
    > **1992 Jeep Cherokee (Plate: MOMWAGON, Current: 222,647 mi):**
    > - ⚠️ **Oil Change**: Due at 225,000 mi (~2,353 miles remaining)
    >
    > **2021 Subaru Outback (Plate: ABC1234, Current: 54,200 mi):**
    > - ✅ No immediate overdue or urgent reminders scheduled."
