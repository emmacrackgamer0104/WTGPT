"""WTGPT progression and learning intelligence.

This module does not assume that vehicle ownership equals player readiness.
It detects technological jumps (for example, squadron vehicles far above a
player's normal progression) and recommends mechanics-first tutorials.
"""
from __future__ import annotations

from typing import Any


def br_for_mode(vehicle: dict[str, Any], mode: str = "Ground RB") -> float | None:
    mode_l = mode.lower()
    key = "br"
    if "arcade" in mode_l:
        key = "br_ab"
    elif "sim" in mode_l:
        key = "br_sb"
    value = vehicle.get(key)
    return float(value) if isinstance(value, (int, float)) else None


def rank_value(value: Any) -> int | None:
    if isinstance(value, (int, float)):
        return int(value)
    roman = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10}
    return roman.get(str(value or "").strip().lower())


def is_special(vehicle: dict[str, Any]) -> bool:
    status = str(vehicle.get("availability", "")).lower()
    return any(x in status for x in ("escuadrón", "evento", "battle pass", "premium"))


def technology_jump(player_rank: int | None, player_br: float | None, vehicle: dict[str, Any], mode: str) -> dict[str, Any]:
    target_br = br_for_mode(vehicle, mode)
    target_rank = rank_value(vehicle.get("rank"))
    br_gap = round(target_br - player_br, 1) if target_br is not None and player_br is not None else None
    rank_gap = target_rank - player_rank if target_rank is not None and player_rank is not None else None

    reasons: list[str] = []
    if br_gap is not None and br_gap >= 2.0:
        reasons.append(f"BR +{br_gap:.1f} sobre tu progresión habitual")
    if rank_gap is not None and rank_gap >= 2:
        reasons.append(f"Rango +{rank_gap} sobre tu progresión habitual")
    if is_special(vehicle):
        reasons.append(f"vehículo de {vehicle.get('availability')}")

    if br_gap is None:
        level = "unknown"
    elif br_gap >= 4.0 or (rank_gap is not None and rank_gap >= 4):
        level = "critical"
    elif br_gap >= 2.0 or (rank_gap is not None and rank_gap >= 2):
        level = "high"
    elif br_gap >= 1.0:
        level = "moderate"
    else:
        level = "normal"

    return {
        "level": level,
        "target_br": target_br,
        "target_rank": target_rank,
        "br_gap": br_gap,
        "rank_gap": rank_gap,
        "reasons": reasons,
    }


TUTORIALS = {
    "air_to_ground": [
        ("Selección de objetivos terrestres", "beginner"),
        ("Cohetes y ataque en picado", "beginner"),
        ("Bombas y cálculo de lanzamiento", "beginner"),
        ("Misiles aire-tierra y tipos de guiado", "intermediate"),
        ("CCIP y CCRP", "intermediate"),
        ("TV/IR, láser y pods de designación", "advanced"),
        ("SEAD y empleo contra defensas antiaéreas", "advanced"),
    ],
    "air_to_air": [
        ("Tipos de misiles aire-aire", "beginner"),
        ("Lock, alcance y ventana de lanzamiento", "beginner"),
        ("Energía, velocidad y capacidad de giro del misil", "intermediate"),
        ("Contramedidas y cómo leer la amenaza", "intermediate"),
        ("BVR y empleo avanzado de misiles", "advanced"),
    ],
    "air_top_tier": [
        ("RWR: símbolos, amenazas y prioridad", "beginner"),
        ("Radar: búsqueda, alcance y contactos", "beginner"),
        ("ACM, STT y TWS", "intermediate"),
        ("RWR + radar + datalink", "intermediate"),
        ("BVR y lectura del espacio aéreo", "advanced"),
        ("Radar vs IRST y gestión de emisiones", "advanced"),
    ],
    "ground_top_tier": [
        ("LWS: lectura y reacción", "beginner"),
        ("Telémetro láser y tiro de primer disparo", "beginner"),
        ("Termales y reconocimiento de objetivos", "beginner"),
        ("Óptica del comandante", "intermediate"),
        ("Hunter-killer y adquisición de objetivos", "intermediate"),
        ("Radar SPAA y seguimiento de blancos", "advanced"),
    ],
    "ground_uptier": [
        ("Identificación de puntos débiles", "beginner"),
        ("APFSDS y selección de munición", "beginner"),
        ("Cómo combatir MBT superiores en uptier", "intermediate"),
        ("Posicionamiento y supervivencia contra vehículos modernos", "advanced"),
    ],
}


def _categories(vehicle: dict[str, Any], mode: str) -> list[str]:
    text = f"{vehicle.get('category', '')} {vehicle.get('type', '')} {vehicle.get('role', '')}".lower()
    categories: list[str] = []
    if "air" in mode.lower() or vehicle.get("category") == "aircraft":
        categories += ["air_to_air", "air_to_ground"]
        if (br_for_mode(vehicle, mode) or 0) >= 14.0:
            categories.append("air_top_tier")
    elif "ground" in mode.lower() or vehicle.get("category") == "ground":
        if (br_for_mode(vehicle, mode) or 0) >= 12.7:
            categories.append("ground_top_tier")
        categories.append("ground_uptier")
    if "helicopter" in text:
        categories.append("air_to_ground")
    return list(dict.fromkeys(categories))


def recommend_tutorials(vehicle: dict[str, Any], mode: str, limit: int = 6) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for category in _categories(vehicle, mode):
        for title, level in TUTORIALS[category]:
            selected.append({"title": title, "level": level, "category": category})
            if len(selected) >= limit:
                return selected
    return selected


def readiness_report(player_rank: int | None, player_br: float | None, vehicle: dict[str, Any], mode: str = "Ground RB") -> dict[str, Any]:
    jump = technology_jump(player_rank, player_br, vehicle, mode)
    tutorials = recommend_tutorials(vehicle, mode)
    return {
        "vehicle": vehicle.get("name"),
        "mode": mode,
        "jump": jump,
        "tutorials": tutorials,
        "warning": jump["level"] in {"critical", "high"},
    }
