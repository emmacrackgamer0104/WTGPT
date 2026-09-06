#!/usr/bin/env python3
"""Build WTGPT's vehicle catalog from the community War Thunder Vehicles API.

The catalog is generated data. WTGPT keeps a small manual overlay for special,
retired, event and legacy vehicles that may need curation beyond the API.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import requests

API_URL = "https://wtvehiclesapi.duckdns.org/api/vehicles"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "vehicles.json"
LIMIT = 200

NATION_MAP = {
    "usa": "Estados Unidos", "us": "Estados Unidos", "united states": "Estados Unidos",
    "ussr": "URSS", "soviet union": "URSS", "russia": "URSS",
    "germany": "Alemania", "germ": "Alemania", "frg": "Alemania", "gdr": "Alemania",
    "britain": "Gran Bretaña", "great britain": "Gran Bretaña", "uk": "Gran Bretaña",
    "japan": "Japón", "china": "China", "italy": "Italia", "france": "Francia",
    "sweden": "Suecia", "israel": "Israel",
}

ROLE_MAP = {
    "fighter": "Caza", "jet fighter": "Caza a reacción", "bomber": "Bombardero",
    "strike aircraft": "Avión de ataque", "medium tank": "Tanque medio", "light tank": "Tanque ligero",
    "heavy tank": "Tanque pesado", "tank destroyer": "Cazacarros", "spaa": "Antiaéreo",
    "atgm vehicle": "Vehículo ATGM", "attack helicopter": "Helicóptero de ataque",
    "utility helicopter": "Helicóptero utilitario", "destroyer": "Destructor", "light cruiser": "Crucero ligero",
    "heavy cruiser": "Crucero pesado", "battleship": "Acorazado", "battlecruiser": "Crucero de batalla",
    "frigate": "Fragata", "boat": "Embarcación", "torpedo boat": "Lancha torpedera",
}


def norm(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip()).lower()


def first(obj: Any, keys: set[str]) -> Any:
    """Find the first value whose key matches, recursively."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if norm(k) in keys and v not in (None, "", [], {}):
                return v
        for v in obj.values():
            found = first(v, keys)
            if found not in (None, "", [], {}):
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = first(v, keys)
            if found not in (None, "", [], {}):
                return found
    return None


def number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        m = re.search(r"\d+(?:\.\d+)?", value.replace(",", "."))
        if m:
            return float(m.group())
    return None


def clean_number(value: float | None) -> int | float | None:
    if value is None:
        return None
    return int(value) if value.is_integer() else value


def extract_br(row: dict[str, Any], mode: str) -> float | None:
    mode_keys = {
        "rb": {"rb", "realistic", "realistic battle", "realistic battles", "realisticbattles", "br_rb", "rb_br", "realistic_br"},
        "ab": {"ab", "arcade", "arcade battle", "arcade battles", "br_ab", "ab_br", "arcade_br"},
        "sb": {"sb", "simulator", "simulator battle", "simulator battles", "br_sb", "sb_br", "simulator_br"},
    }[mode]
    direct = first(row, mode_keys)
    n = number(direct)
    if n is not None and 0 < n < 20:
        return n
    generic = first(row, {"br", "battle rating", "battlerating", "battle_rating", "rating"})
    if isinstance(generic, dict):
        for k, v in generic.items():
            if norm(k) in mode_keys:
                n = number(v)
                if n is not None and 0 < n < 20:
                    return n
    n = number(generic)
    return n if n is not None and 0 < n < 20 else None


def extract_name(row: dict[str, Any]) -> str:
    value = first(row, {"name", "display_name", "displayname", "title", "common_name", "commonname", "vehicle_name"})
    if isinstance(value, dict):
        value = next((v for v in value.values() if isinstance(v, str) and v.strip()), None)
    return str(value or row.get("id") or row.get("identifier") or "Vehículo desconocido").strip()


def extract_nation(row: dict[str, Any]) -> str:
    value = first(row, {"country", "nation", "nation_name", "country_name", "tree", "operator"})
    if isinstance(value, dict):
        value = next((v for v in value.values() if isinstance(v, str) and v.strip()), None)
    return NATION_MAP.get(norm(value), str(value or "Desconocida").strip())


def extract_rank(row: dict[str, Any]) -> int | None:
    value = first(row, {"rank", "tier", "economic_rank", "economicrank", "era"})
    n = number(value)
    if n is None:
        return None
    return int(n) if 1 <= n <= 10 else None


def extract_type(row: dict[str, Any]) -> str:
    value = first(row, {"type", "vehicle_type", "vehicletype", "class", "role", "main_role", "mainrole"})
    if isinstance(value, dict):
        value = next((v for v in value.values() if isinstance(v, str) and v.strip()), None)
    return str(value or "Desconocido").strip()


def role_name(raw: str) -> str:
    key = norm(raw)
    for known, label in ROLE_MAP.items():
        if known in key:
            return label
    return raw or "Desconocido"


def extract_status(row: dict[str, Any]) -> str:
    value = first(row, {"availability", "availability_status", "status", "vehicle_status", "purchasestatus"})
    text = norm(value)
    if "premium" in text:
        return "premium"
    if "squadron" in text:
        return "escuadrón"
    if "event" in text:
        return "evento"
    if "battle pass" in text or "battlepass" in text:
        return "Battle Pass"
    if "removed" in text or "retired" in text or "unavailable" in text:
        return "retirado"
    return "regular"


def row_id(row: dict[str, Any]) -> str:
    return str(row.get("identifier") or row.get("id") or row.get("vehicle_id") or row.get("gameId") or "").strip()


def fetch_all() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    session = requests.Session()
    session.headers.update({"User-Agent": "WTGPT vehicle database synchronizer"})
    for page in range(100):
        response = session.get(API_URL, params={"limit": LIMIT, "page": page}, timeout=30)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            items = next((payload[k] for k in ("data", "items", "results", "vehicles") if isinstance(payload.get(k), list)), [])
        else:
            items = []
        if not items:
            break
        added = 0
        for row in items:
            if not isinstance(row, dict):
                continue
            ident = row_id(row)
            if ident and ident not in seen:
                seen.add(ident)
                rows.append(row)
                added += 1
        print(f"Página {page}: {len(items)} recibidos, {added} nuevos")
        if len(items) < LIMIT or added == 0:
            break
    if len(rows) < 100:
        raise RuntimeError(f"La API devolvió solo {len(rows)} vehículos; se cancela para evitar reemplazar la base con datos incompletos.")
    return rows


def load_manual() -> dict[str, dict[str, Any]]:
    if not OUT.exists():
        return {}
    data = json.loads(OUT.read_text(encoding="utf-8"))
    result = {}
    for v in data.get("vehicles", []):
        result[norm(v.get("name"))] = v
    return result


def main() -> int:
    manual = load_manual()
    rows = fetch_all()
    vehicles: dict[str, dict[str, Any]] = {}
    for row in rows:
        name = extract_name(row)
        key = norm(name)
        existing = manual.get(key, {})
        entry = {
            "name": name,
            "nation": extract_nation(row),
            "type": extract_type(row),
            "rank": extract_rank(row),
            "br": clean_number(extract_br(row, "rb")),
            "br_ab": clean_number(extract_br(row, "ab")),
            "br_sb": clean_number(extract_br(row, "sb")),
            "role": role_name(extract_type(row)),
            "availability": existing.get("availability") or extract_status(row),
            "source": "WT Vehicles API",
            "source_id": row_id(row),
        }
        # Keep trusted manual corrections when the API has a hole.
        for field in ("nation", "type", "rank", "br", "br_ab", "br_sb", "role"):
            if entry[field] in (None, "", "Desconocida", "Desconocido") and existing.get(field) not in (None, ""):
                entry[field] = existing[field]
        vehicles[key] = entry

    # Preserve curated vehicles absent from the API (retired/event/legacy cases).
    for key, entry in manual.items():
        if key not in vehicles:
            entry = dict(entry)
            entry.setdefault("source", "manual-curation")
            vehicles[key] = entry

    output = sorted(vehicles.values(), key=lambda v: (str(v.get("nation")), v.get("rank") is None, v.get("rank") or 99, str(v.get("name"))))
    OUT.write_text(json.dumps({"vehicles": output}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WTGPT: {len(output)} vehículos escritos en {OUT}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
