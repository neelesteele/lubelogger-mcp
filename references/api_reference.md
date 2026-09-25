# LubeLogger REST API Reference

This document provides a comprehensive reference for the REST API endpoints in [LubeLogger](https://github.com/hargata/lubelog).

---

## 1. Authentication

LubeLogger supports two authentication mechanisms:

### API Keys (Recommended)
Generate an API key in the LubeLogger web UI (**Settings > API Keys**) with appropriate permissions (`Viewer`, `Editor`, or `Manager`).
- **Header:** `x-api-key: YOUR_API_KEY`
- **Query Parameter:** `?apiKey=YOUR_API_KEY`

### HTTP Basic Auth
Pass a base64-encoded `username:password` string in the standard Authorization header:
- **Header:** `Authorization: Basic <base64_encoded_credentials>`

---

## 2. API Endpoints Overview

| Method | Endpoint | Description | Key Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/version` | Get server version info | None |
| `GET` | `/api/whoami` | Get info for authenticated user | None |
| `GET` | `/api/vehicles` | List all vehicles user has access to | None |
| `GET` | `/api/vehicle/info` | Vehicle details and metrics | `vehicleId` (optional) |
| `GET` | `/api/vehicle/odometerrecords/latest` | Latest odometer mileage | `vehicleId` (required) |
| `GET` | `/api/vehicle/adjustedodometer` | Mileage with adjustments | `vehicleId`, `odometer` |
| `POST` | `/api/vehicles/add` | Add a vehicle | JSON body |
| `PUT` | `/api/vehicles/update` | Update vehicle | JSON body (with `id`) |
| `DELETE`| `/api/vehicles/delete` | Delete vehicle | `id` |

### Records Query Endpoints

For each record type (`gasrecords`, `servicerecords`, `repairrecords`, `odometerrecords`, `reminders`, `notes`, `upgraderecords`, `supplyrecords`, `taxrecords`, `planrecords`, `equipmentrecords`):

*   **Vehicle Records:** `GET /api/vehicle/{category}?vehicleId={id}`
*   **All Vehicles:** `GET /api/vehicle/{category}/all`
*   **Add Record:** `POST /api/vehicle/{category}/add?vehicleId={id}` (JSON body)
*   **Update Record:** `PUT /api/vehicle/{category}/update` (JSON body containing `"id"`)
*   **Delete Record:** `DELETE /api/vehicle/{category}/delete?id={recordId}`

---

## 3. Record Add & Update Details

### Gas Records (`/api/vehicle/gasrecords/add?vehicleId={id}`)
- **Method:** `POST`
- **Required Body Fields:**
  - `date`: String date (`YYYY-MM-DD` or `MM/DD/YYYY`)
  - `odometer`: Current odometer reading (int or string)
  - `fuelConsumed`: Amount of fuel consumed (decimal or string)
  - `cost`: Total cost of fuel purchase (decimal or string)
  - `isFillToFull`: `"true"` (full tank) or `"false"` (partial fill)
  - `missedFuelUp`: `"true"` or `"false"`
- **Optional Body Fields:**
  - `notes`: Text notes (station, octane, price/gal)
  - `tags`: Space-separated tags
  - `startingSoc`, `endingSoc`: Integer SOC percentages (EV only)
  - `extraFields`: Array of `{"name": "...", "value": "..."}`
  - `files`: Array of attachments

### Service Records (`/api/vehicle/servicerecords/add?vehicleId={id}`)
- **Method:** `POST`
- **Required Body Fields:**
  - `date`: Service date
  - `odometer`: Mileage at service
  - `description`: Work description (e.g., "Synthetic Oil & Filter Change")
  - `cost`: Total cost
- **Optional Body Fields:**
  - `notes`: Parts used, oil viscosity, shop name
  - `tags`: Space-separated tags

### Repair Records (`/api/vehicle/repairrecords/add?vehicleId={id}`)
- **Method:** `POST`
- **Required Body Fields:**
  - `date`: Repair date
  - `odometer`: Mileage at repair
  - `description`: Work description (e.g., "Replaced Alternator")
  - `cost`: Total cost
- **Optional Body Fields:**
  - `notes`: Diagnosis notes, failure cause, warranty info
  - `tags`: Space-separated tags

### Odometer Records (`/api/vehicle/odometerrecords/add?vehicleId={id}`)
- **Method:** `POST`
- **Required Body Fields:**
  - `date`: Reading date
  - `odometer`: Odometer reading
- **Optional Body Fields:**
  - `initialOdometer`: Previous reading (auto-detected if omitted)
  - `notes`: Notes
  - `tags`: Space-separated tags

### Reminders (`/api/vehicle/reminders/add?vehicleId={id}`)
- **Method:** `POST`
- **Required Body Fields:**
  - `description`: Name of reminder
  - `metric`: `"Date"`, `"Odometer"`, or `"Both"`
  - `dueDate`: Required if metric is `Date` or `Both` (`YYYY-MM-DD`)
  - `dueOdometer`: Required if metric is `Odometer` or `Both`
- **Optional Body Fields:**
  - `notes`: Text notes
  - `tags`: Space-separated tags

### Notes (`/api/vehicle/notes/add?vehicleId={id}`)
- **Method:** `POST`
- **Required Body Fields:**
  - `description`: Note title/subject
  - `noteText`: Body text
- **Optional Body Fields:**
  - `pinned`: `"true"` or `"false"`
  - `tags`: Space-separated tags

---

## 4. Response Format

Successful responses typically return JSON with:
```json
{
  "success": true,
  "message": "Gas Record Added",
  "data": {
    "recordId": 42
  }
}
```

Error responses return HTTP 400/403/500 with:
```json
{
  "success": false,
  "message": "Input object invalid, Date, Odometer, FuelConsumed, IsFillToFull, MissedFuelUp, and Cost cannot be empty."
}
```
