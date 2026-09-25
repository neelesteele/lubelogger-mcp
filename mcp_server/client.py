"""
LubeLogger REST API Client
Provides standard HTTP operations for communicating with a self-hosted LubeLogger instance.
"""

import os
import sys
import json
import base64
import ssl
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, List, Optional, Union


def load_dotenv(dotenv_path: Optional[str] = None):
    """Simple .env file loader that does not require external packages."""
    if not dotenv_path:
        candidates = [
            os.path.join(os.getcwd(), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        ]
        for c in candidates:
            if os.path.exists(c):
                dotenv_path = c
                break

    if dotenv_path and os.path.exists(dotenv_path):
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val


class LubeLoggerClient:
    """Client for LubeLogger REST API."""

    RECORD_ENDPOINTS = {
        "gas": "gasrecords",
        "gasrecords": "gasrecords",
        "service": "servicerecords",
        "servicerecords": "servicerecords",
        "repair": "repairrecords",
        "repairrecords": "repairrecords",
        "odometer": "odometerrecords",
        "odometerrecords": "odometerrecords",
        "reminder": "reminders",
        "reminders": "reminders",
        "note": "notes",
        "notes": "notes",
        "upgrade": "upgraderecords",
        "upgraderecords": "upgraderecords",
        "supply": "supplyrecords",
        "supplyrecords": "supplyrecords",
        "tax": "taxrecords",
        "taxrecords": "taxrecords",
        "plan": "planrecords",
        "planrecords": "planrecords",
        "equipment": "equipmentrecords",
        "equipmentrecords": "equipmentrecords",
    }

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: int = 20,
    ):
        load_dotenv()
        self.base_url = (base_url or os.getenv("LUBELOGGER_URL", "http://localhost:5000")).rstrip("/")
        self.api_key = api_key or os.getenv("LUBELOGGER_API_KEY", "")
        self.username = username or os.getenv("LUBELOGGER_USERNAME", "")
        self.password = password or os.getenv("LUBELOGGER_PASSWORD", "")
        verify_ssl_env = os.getenv("LUBELOGGER_VERIFY_SSL", "true").lower()
        self.verify_ssl = verify_ssl and (verify_ssl_env not in ("false", "0", "no"))
        self.timeout = timeout

        self.ssl_context = None
        if not self.verify_ssl:
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

    def _get_headers(self, has_body: bool = False) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "User-Agent": "LubeLogger-MCP-Client/1.0",
            "Accept": "application/json",
        }
        if has_body:
            headers["Content-Type"] = "application/json"

        if self.api_key:
            headers["x-api-key"] = self.api_key
        elif self.username and self.password:
            creds = f"{self.username}:{self.password}"
            b64_creds = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {b64_creds}"

        return headers

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Union[Dict[str, Any], List[Any]]] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            filtered_params = {k: v for k, v in params.items() if v is not None}
            if filtered_params:
                url += "?" + urllib.parse.urlencode(filtered_params)

        has_body = body is not None
        data = None
        if has_body:
            data = json.dumps(body).encode("utf-8")

        headers = self._get_headers(has_body=has_body)
        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())

        try:
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=self.timeout) as resp:
                status = resp.status
                content_type = resp.headers.get("Content-Type", "")
                raw = resp.read().decode("utf-8")
                if "application/json" in content_type or raw.startswith(("{", "[")):
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError:
                        return raw
                # Could be a plain number or string (e.g. latest odometer)
                try:
                    return json.loads(raw)
                except Exception:
                    return raw.strip()
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            try:
                err_json = json.loads(err_body)
                msg = err_json.get("message") or err_json.get("error") or err_body
            except Exception:
                msg = err_body
            raise RuntimeError(f"LubeLogger API error {e.code} ({e.reason}): {msg}") from e
        except urllib.error.URLError as e:
            try:
                return self._request_curl(method, url, headers, data)
            except RuntimeError as r_err:
                if "LubeLogger API error" in str(r_err):
                    raise
                raise RuntimeError(f"Failed to connect to LubeLogger at {self.base_url}: {e.reason}") from r_err
            except Exception as curl_err:
                raise RuntimeError(f"Failed to connect to LubeLogger at {self.base_url}: {e.reason}") from curl_err

    def _request_curl(self, method: str, url: str, headers: Dict[str, str], data: Optional[bytes]) -> Any:
        cmd = ["curl", "-s", "-w", "\n%{http_code}", "-X", method.upper(), url]
        if not self.verify_ssl:
            cmd.append("-k")
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
        if data:
            cmd.extend(["--data", data.decode("utf-8")])
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
        if res.returncode != 0:
            raise RuntimeError(f"curl failed: {res.stderr}")

        output = res.stdout
        if "\n" in output:
            body_text, status_str = output.rsplit("\n", 1)
        else:
            body_text, status_str = output, "200"

        status_code = int(status_str.strip()) if status_str.strip().isdigit() else 200
        if status_code >= 400:
            raise RuntimeError(f"LubeLogger API error {status_code}: {body_text}")

        raw = body_text.strip()
        if raw.startswith(("{", "[")):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
        try:
            return json.loads(raw)
        except Exception:
            return raw

    # --- Diagnostics & Metadata ---

    def test_connection(self) -> Dict[str, Any]:
        """Test API connectivity and authentication against the server."""
        try:
            version_info = self._request("GET", "/api/version")
            whoami = None
            try:
                whoami = self._request("GET", "/api/whoami")
            except Exception:
                pass
            return {
                "success": True,
                "url": self.base_url,
                "version": version_info,
                "whoami": whoami,
            }
        except Exception as e:
            return {
                "success": False,
                "url": self.base_url,
                "error": str(e),
            }

    # --- Vehicles ---

    def list_vehicles(self) -> List[Dict[str, Any]]:
        """List all vehicles accessible to the user."""
        res = self._request("GET", "/api/vehicles")
        if isinstance(res, list):
            return res
        return []

    def get_vehicle_info(self, vehicle_id: Optional[int] = None) -> Any:
        """Get details for all vehicles or a specific vehicle."""
        params = {"vehicleId": vehicle_id} if vehicle_id else {}
        return self._request("GET", "/api/vehicle/info", params=params)

    # --- Odometer & Readings ---

    def get_latest_odometer(self, vehicle_id: int) -> Union[int, Dict[str, Any]]:
        """Get the latest odometer reading for a vehicle."""
        res = self._request("GET", "/api/vehicle/odometerrecords/latest", params={"vehicleId": vehicle_id})
        try:
            return int(res)
        except (ValueError, TypeError):
            return res

    def get_adjusted_odometer(self, vehicle_id: int, odometer: int) -> Any:
        """Get odometer reading with adjustments applied."""
        return self._request(
            "GET",
            "/api/vehicle/adjustedodometer",
            params={"vehicleId": vehicle_id, "odometer": odometer},
        )

    # --- Generic Records Query ---

    def get_records(
        self,
        record_type: str,
        vehicle_id: Optional[int] = None,
        all_vehicles: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Query records for a specific vehicle or all vehicles.
        record_type: gas, service, repair, odometer, reminder, note, upgrade, supply, tax, plan, equipment
        """
        endpoint = self.RECORD_ENDPOINTS.get(record_type.lower())
        if not endpoint:
            raise ValueError(f"Unknown record type '{record_type}'. Supported: {list(self.RECORD_ENDPOINTS.keys())}")

        if all_vehicles or not vehicle_id:
            path = f"/api/vehicle/{endpoint}/all"
            res = self._request("GET", path)
        else:
            path = f"/api/vehicle/{endpoint}"
            res = self._request("GET", path, params={"vehicleId": vehicle_id})

        return res if isinstance(res, list) else []

    # --- Add Records ---

    def add_gas_record(
        self,
        vehicle_id: int,
        date: str,
        odometer: Union[int, str],
        fuel_consumed: Union[float, str],
        cost: Union[float, str],
        is_fill_to_full: bool = True,
        missed_fuel_up: bool = False,
        notes: str = "",
        tags: str = "",
        starting_soc: Optional[int] = None,
        ending_soc: Optional[int] = None,
        extra_fields: Optional[List[Dict[str, str]]] = None,
        files: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Add a gas/fuel record for a vehicle."""
        payload: Dict[str, Any] = {
            "date": str(date),
            "odometer": str(odometer),
            "fuelConsumed": str(fuel_consumed),
            "cost": str(cost),
            "isFillToFull": "true" if is_fill_to_full else "false",
            "missedFuelUp": "true" if missed_fuel_up else "false",
            "notes": notes or "",
            "tags": tags or "",
            "extraFields": extra_fields or [],
            "files": files or [],
        }
        if starting_soc is not None:
            payload["startingSoc"] = str(starting_soc)
        if ending_soc is not None:
            payload["endingSoc"] = str(ending_soc)

        return self._request("POST", "/api/vehicle/gasrecords/add", params={"vehicleId": vehicle_id}, body=payload)

    def add_service_record(
        self,
        vehicle_id: int,
        date: str,
        odometer: Union[int, str],
        description: str,
        cost: Union[float, str],
        notes: str = "",
        tags: str = "",
        extra_fields: Optional[List[Dict[str, str]]] = None,
        files: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Add a scheduled/routine service record for a vehicle."""
        payload = {
            "date": str(date),
            "odometer": str(odometer),
            "description": description,
            "cost": str(cost),
            "notes": notes or "",
            "tags": tags or "",
            "extraFields": extra_fields or [],
            "files": files or [],
        }
        return self._request("POST", "/api/vehicle/servicerecords/add", params={"vehicleId": vehicle_id}, body=payload)

    def add_repair_record(
        self,
        vehicle_id: int,
        date: str,
        odometer: Union[int, str],
        description: str,
        cost: Union[float, str],
        notes: str = "",
        tags: str = "",
        extra_fields: Optional[List[Dict[str, str]]] = None,
        files: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Add an unscheduled repair record for a vehicle."""
        payload = {
            "date": str(date),
            "odometer": str(odometer),
            "description": description,
            "cost": str(cost),
            "notes": notes or "",
            "tags": tags or "",
            "extraFields": extra_fields or [],
            "files": files or [],
        }
        return self._request("POST", "/api/vehicle/repairrecords/add", params={"vehicleId": vehicle_id}, body=payload)

    def add_odometer_record(
        self,
        vehicle_id: int,
        date: str,
        odometer: Union[int, str],
        initial_odometer: Optional[Union[int, str]] = None,
        notes: str = "",
        tags: str = "",
        extra_fields: Optional[List[Dict[str, str]]] = None,
        files: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Add an odometer log record for a vehicle."""
        payload: Dict[str, Any] = {
            "date": str(date),
            "odometer": str(odometer),
            "notes": notes or "",
            "tags": tags or "",
            "extraFields": extra_fields or [],
            "files": files or [],
        }
        if initial_odometer is not None:
            payload["initialOdometer"] = str(initial_odometer)

        return self._request("POST", "/api/vehicle/odometerrecords/add", params={"vehicleId": vehicle_id}, body=payload)

    def add_reminder(
        self,
        vehicle_id: int,
        description: str,
        metric: str = "Both",
        due_date: Optional[str] = None,
        due_odometer: Optional[Union[int, str]] = None,
        notes: str = "",
        tags: str = "",
    ) -> Dict[str, Any]:
        """
        Add a reminder record.
        metric: 'Date', 'Odometer', or 'Both'
        """
        normalized_metric = metric.capitalize()
        if normalized_metric not in ("Date", "Odometer", "Both"):
            normalized_metric = "Both"

        payload = {
            "description": description,
            "metric": normalized_metric,
            "dueDate": str(due_date) if due_date else "",
            "dueOdometer": str(due_odometer) if due_odometer is not None else "",
            "notes": notes or "",
            "tags": tags or "",
        }
        return self._request("POST", "/api/vehicle/reminders/add", params={"vehicleId": vehicle_id}, body=payload)

    def add_note(
        self,
        vehicle_id: int,
        description: str,
        note_text: str,
        pinned: bool = False,
        tags: str = "",
        extra_fields: Optional[List[Dict[str, str]]] = None,
        files: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Add a note for a vehicle."""
        payload = {
            "description": description,
            "noteText": note_text,
            "pinned": "true" if pinned else "false",
            "tags": tags or "",
            "extraFields": extra_fields or [],
            "files": files or [],
        }
        return self._request("POST", "/api/vehicle/notes/add", params={"vehicleId": vehicle_id}, body=payload)

    def add_plan_record(
        self,
        vehicle_id: int,
        description: str,
        cost: Union[float, str] = 0.0,
        type: str = "ServiceRecord",
        priority: str = "Normal",
        progress: str = "Backlog",
        notes: str = "",
        extra_fields: Optional[List[Dict[str, str]]] = None,
        files: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Add a planned maintenance or upgrade item."""
        payload = {
            "description": description,
            "cost": float(cost),
            "type": type,
            "priority": priority,
            "progress": progress,
            "notes": notes or "",
            "extraFields": extra_fields or [],
            "files": files or [],
        }
        return self._request("POST", "/api/vehicle/planrecords/add", params={"vehicleId": vehicle_id}, body=payload)

    def add_upgrade_record(
        self,
        vehicle_id: int,
        date: str,
        odometer: Union[int, str],
        description: str,
        cost: Union[float, str],
        notes: str = "",
        tags: str = "",
        extra_fields: Optional[List[Dict[str, str]]] = None,
        files: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Add an upgrade / modification record for a vehicle."""
        payload = {
            "date": str(date),
            "odometer": str(odometer),
            "description": description,
            "cost": str(cost),
            "notes": notes or "",
            "tags": tags or "",
            "extraFields": extra_fields or [],
            "files": files or [],
        }
        return self._request("POST", "/api/vehicle/upgraderecords/add", params={"vehicleId": vehicle_id}, body=payload)

    # --- Update & Delete Records ---

    def update_record(self, record_type: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing record of any type.
        record_data must contain 'id'.
        """
        if "id" not in record_data and "Id" not in record_data:
            raise ValueError("Record data must contain 'id' field for updates.")

        endpoint = self.RECORD_ENDPOINTS.get(record_type.lower())
        if not endpoint:
            raise ValueError(f"Unknown record type '{record_type}'.")

        # Convert fields to strings if required by LubeLogger's export model
        formatted_data = dict(record_data)
        for field in ("odometer", "cost", "fuelConsumed", "startingSoc", "endingSoc", "id"):
            if field in formatted_data and formatted_data[field] is not None:
                formatted_data[field] = str(formatted_data[field])

        path = f"/api/vehicle/{endpoint}/update"
        return self._request("PUT", path, body=formatted_data)

    def delete_record(self, record_type: str, record_id: int) -> Dict[str, Any]:
        """
        Delete a record by type and ID.
        record_type: gas, service, repair, odometer, reminder, note, upgrade, supply, tax, plan, equipment
        """
        endpoint = self.RECORD_ENDPOINTS.get(record_type.lower())
        if not endpoint:
            raise ValueError(f"Unknown record type '{record_type}'.")

        path = f"/api/vehicle/{endpoint}/delete"
        return self._request("DELETE", path, params={"id": record_id})

    # --- Reminders Helper ---

    def get_reminders(self, vehicle_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get reminders for a specific vehicle or all vehicles."""
        return self.get_records("reminder", vehicle_id=vehicle_id, all_vehicles=(vehicle_id is None))
