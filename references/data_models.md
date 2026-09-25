# LubeLogger Data Models & Schemas

This document defines the data structures and JSON schemas used across LubeLogger records.

---

## 1. Vehicle Model

```json
{
  "id": 1,
  "year": 2021,
  "make": "Subaru",
  "model": "Outback",
  "licensePlate": "ABC1234",
  "purchaseDate": "2021-04-15",
  "soldDate": "",
  "purchasePrice": 32000.00,
  "soldPrice": 0.00,
  "isElectric": false,
  "isDiesel": false,
  "useHours": false,
  "odometerOptional": false,
  "tags": ["daily", "awd"],
  "extraFields": [
    {
      "name": "VIN",
      "value": "4S4BSANC3M3123456"
    },
    {
      "name": "Tire Size",
      "value": "225/65R17"
    }
  ]
}
```

---

## 2. Gas / Fuel Record Model

```json
{
  "id": 101,
  "vehicleId": 1,
  "date": "2026-09-25",
  "odometer": 54200,
  "fuelConsumed": 14.2,
  "cost": 46.50,
  "fuelEconomy": 28.5,
  "isFillToFull": true,
  "missedFuelUp": false,
  "startingSoc": 0,
  "endingSoc": 0,
  "notes": "Costco Wholesale, $3.274/gal, Regular 87",
  "tags": "costco regular highway",
  "extraFields": [],
  "files": []
}
```

---

## 3. Service Record Model

```json
{
  "id": 45,
  "vehicleId": 1,
  "date": "2026-09-20",
  "odometer": 54000,
  "description": "Oil Change & Tire Rotation",
  "cost": 65.00,
  "notes": "Mobil 1 0W-20 Advanced Fuel Economy (5.1 qts), OEM Subaru Filter 15208AA15A. Rotated front-to-rear.",
  "tags": "diy synthetic tires",
  "extraFields": [],
  "files": []
}
```

---

## 4. Repair Record Model

```json
{
  "id": 12,
  "vehicleId": 1,
  "date": "2026-08-15",
  "odometer": 52100,
  "description": "Front Passenger Brake Caliper Replacement",
  "cost": 210.50,
  "notes": "Sticking caliper caused uneven pad wear. Replaced caliper and bled brake fluid.",
  "tags": "brakes repair",
  "extraFields": [],
  "files": []
}
```

---

## 5. Reminder Model

```json
{
  "id": 8,
  "vehicleId": 1,
  "description": "Engine Oil & Filter Change",
  "metric": "Both",
  "dueDate": "2027-03-20",
  "dueOdometer": 60000,
  "urgency": "NotUrgent",
  "notes": "Interval: 6 months or 6,000 miles",
  "tags": "oil maintenance"
}
```

Urgency statuses calculated by LubeLogger:
*   `NotUrgent`: Far from due date/mileage
*   `Urgent`: Within configured warning threshold (e.g. within 500 miles or 14 days)
*   `VeryUrgent`: Overdue

---

## 6. Odometer Record Model

```json
{
  "id": 88,
  "vehicleId": 1,
  "date": "2026-09-25",
  "initialOdometer": 53500,
  "odometer": 54200,
  "distance": 700,
  "notes": "Monthly mileage check",
  "tags": "checkpoint",
  "extraFields": [],
  "files": []
}
```

---

## 7. Note Model

```json
{
  "id": 5,
  "vehicleId": 1,
  "description": "Fluids & Capacities Quick Reference",
  "noteText": "Engine Oil: 5.1 qts 0W-20\nCoolant: 8.2 qts Super Coolant\nTransmission: CVT High Torque Fluid (dealership service only)",
  "pinned": true,
  "tags": "reference fluids specs"
}
```
