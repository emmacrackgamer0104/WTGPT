"""WTGPT lineup recommendation engine.

Deterministic intelligence layer for recommending coherent War Thunder
lineups from the vehicle database. It deliberately refuses to invent BRs.
"""


def normalizar_texto(texto):
    return " ".join(str(texto).strip().lower().split())


def buscar_vehiculo(vehiculos, nombre):
    objetivo = normalizar_texto(nombre)
    for vehiculo in vehiculos:
        if normalizar_texto(vehiculo.get("name", "")) == objetivo:
            return vehiculo
    return None


def br_numerico(vehiculo):
    br = vehiculo.get("br")
    return br if isinstance(br, (int, float)) else None


def clasificar_rol(vehiculo):
    texto = normalizar_texto(
        f"{vehiculo.get('role', '')} {vehiculo.get('type', '')}"
    )

    if any(x in texto for x in ("antiaéreo", "antiaereo", "spaa", "aa")):
        return "antiaereo"
    if any(x in texto for x in ("atgm", "antitanque", "anti-tanque", "cazacarros")):
        return "antitanque"
    if any(x in texto for x in ("explorador", "recon", "vehículo ligero", "vehiculo ligero")):
        return "recon"
    if "helicóptero" in texto or "helicoptero" in texto:
        return "helicoptero"
    if "avión" in texto or "avion" in texto:
        return "aire"
    return "principal"


def compatibilidad_nacion(vehiculo, nacion):
    return normalizar_texto(vehiculo.get("nation", "")) == normalizar_texto(nacion)


def generar_lineup(vehiculos, vehiculo_base=None, nacion=None, target_br=None, modo="Ground RB", max_vehiculos=5):
    """Genera un lineup coherente sin inventar datos faltantes.

    Puede partir de un vehículo concreto (incluidos eventos, Pase de Batalla
    y vehículos retirados) o de una nación + BR.
    """
    if vehiculo_base:
        base = buscar_vehiculo(vehiculos, vehiculo_base)
        if not base:
            return {"status": "not_found", "message": "Vehículo no encontrado en la base de datos."}
        nacion = base.get("nation")
    else:
        base = None

    candidatos = [v for v in vehiculos if not nacion or compatibilidad_nacion(v, nacion)]

    if target_br is not None:
        candidatos = [
            v for v in candidatos
            if br_numerico(v) is not None and abs(br_numerico(v) - target_br) <= 0.7
        ]

    if base and br_numerico(base) is None:
        return {
            "status": "insufficient_data",
            "base": base,
            "message": (
                f"{base.get('name')} fue encontrado, pero su BR actual no está verificado "
                "en la base de datos. No se generará un lineup inventando datos."
            ),
        }

    if target_br is not None and not candidatos:
        return {
            "status": "insufficient_data",
            "message": "No hay suficientes vehículos con BR verificado para construir el lineup."
        }

    if not base and target_br is None:
        return {
            "status": "insufficient_data",
            "message": "Indica un vehículo base o una nación y un BR objetivo."
        }

    if base:
        base_br = br_numerico(base)
        candidatos = [
            v for v in candidatos
            if normalizar_texto(v.get("name", "")) != normalizar_texto(base.get("name", ""))
            and br_numerico(v) is not None
            and abs(br_numerico(v) - base_br) <= 0.7
        ]
    else:
        base_br = target_br

    seleccionados = [base] if base else []
    roles = set()

    candidatos.sort(key=lambda v: abs(br_numerico(v) - base_br))

    for candidato in candidatos:
        rol = clasificar_rol(candidato)
        if rol not in roles or len(seleccionados) < 2:
            seleccionados.append(candidato)
            roles.add(rol)
        if len(seleccionados) >= max_vehiculos:
            break

    return {
        "status": "ok",
        "base": base,
        "nation": nacion,
        "mode": modo,
        "target_br": base_br,
        "lineup": seleccionados,
    }
