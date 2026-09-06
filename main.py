import json
import os

from lineup_engine import generar_lineup
from progression_intelligence import readiness_report

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ORANGE = "\033[38;5;208m"
LIGHT = "\033[97m"
GRAY = "\033[90m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"

LOGO = f"""{ORANGE}{BOLD}
██╗    ██╗████████╗ ██████╗ ██████╗ ████████╗
██║    ██║╚══██╔══╝██╔════╝ ██╔══██╗╚══██╔╝
██║ █╗ ██║   ██║   ██║  ███╗██████╔╝   ██║
██║███╗██║   ██║   ██║   ██║██╔═══╝    ██║
╚███╔███╔╝   ██║   ╚██████╔╝██║        ██║
 ╚══╝╚══╝    ╚═╝    ╚═════╝ ╚═╝        ╚═╝
{RESET}"""


def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def cargar_vehiculos():
    ruta = os.path.join(os.path.dirname(__file__), "vehicles.json")
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo).get("vehicles", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def buscar_vehiculo(vehiculos, nombre):
    objetivo = " ".join(nombre.strip().lower().split())
    return next((v for v in vehiculos if " ".join(str(v.get("name", "")).lower().split()) == objetivo), None)


def mostrar_encabezado():
    print(LOGO)
    print(f"{GRAY}  WAR THUNDER INTELLIGENCE & ANALYTICS{RESET}")
    print(f"{GRAY}  ─────────────────────────────────────{RESET}\n")


def mostrar_menu():
    print(f"{ORANGE}{BOLD}┌──────────────────────────────────────┐{RESET}")
    print(f"{ORANGE}{BOLD}│{RESET} {LIGHT}{BOLD}WTGPT CONTROL PANEL{RESET}               {ORANGE}{BOLD}│{RESET}")
    print(f"{ORANGE}{BOLD}├──────────────────────────────────────┤{RESET}")
    print(f"{ORANGE}{BOLD}│{RESET}  {ORANGE}1{RESET}  Analizar vehículo              {ORANGE}{BOLD}│{RESET}")
    print(f"{ORANGE}{BOLD}│{RESET}  {ORANGE}2{RESET}  Comparar vehículos             {ORANGE}{BOLD}│{RESET}")
    print(f"{ORANGE}{BOLD}│{RESET}  {ORANGE}3{RESET}  Economía                        {ORANGE}{BOLD}│{RESET}")
    print(f"{ORANGE}{BOLD}│{RESET}  {ORANGE}4{RESET}  Estadísticas                    {ORANGE}{BOLD}│{RESET}")
    print(f"{ORANGE}{BOLD}│{RESET}  {ORANGE}5{RESET}  Recomendar lineup               {ORANGE}{BOLD}│{RESET}")
    print(f"{ORANGE}{BOLD}│{RESET}  {ORANGE}6{RESET}  Preparación / salto tecnológico {ORANGE}{BOLD}│{RESET}")
    print(f"{ORANGE}{BOLD}│{RESET}  {ORANGE}7{RESET}  Salir                           {ORANGE}{BOLD}│{RESET}")
    print(f"{ORANGE}{BOLD}└──────────────────────────────────────┘{RESET}")


def analizar_vehiculo(vehiculos):
    nombre = input(f"\n{ORANGE}WTGPT>{RESET} Introduce el nombre del vehículo: ").strip().lower()
    encontrado = buscar_vehiculo(vehiculos, nombre)
    if not encontrado:
        print(f"\n{RED}✖ Vehículo no encontrado en la base de datos.{RESET}\n")
        return
    print(f"\n{ORANGE}{BOLD}┌── ANÁLISIS DE VEHÍCULO ─────────────────┐{RESET}")
    print(f"{LIGHT}  Nombre :{RESET} {encontrado.get('name', 'N/D')}")
    print(f"{LIGHT}  Nación :{RESET} {encontrado.get('nation', 'N/D')}")
    print(f"{LIGHT}  Tipo   :{RESET} {encontrado.get('type', 'N/D')}")
    print(f"{LIGHT}  Rol    :{RESET} {encontrado.get('role', 'N/D')}")
    print(f"{LIGHT}  BR RB  :{RESET} {encontrado.get('br') if encontrado.get('br') is not None else 'Pendiente'}")
    print(f"{LIGHT}  BR AB  :{RESET} {encontrado.get('br_ab') if encontrado.get('br_ab') is not None else 'Pendiente'}")
    print(f"{LIGHT}  Estado :{RESET} {encontrado.get('availability', 'N/D')}")
    print(f"{ORANGE}{BOLD}└──────────────────────────────────────────┘{RESET}\n")


def recomendar_lineup(vehiculos):
    print(f"\n{ORANGE}{BOLD}┌── LINEUP INTELLIGENCE ──────────────────┐{RESET}")
    nombre = input(f"{LIGHT}  Vehículo base (ENTER para usar BR):{RESET} ").strip()
    modo = input(f"{LIGHT}  Modo (ej. Ground RB):{RESET} ").strip() or "Ground RB"
    if nombre:
        resultado = generar_lineup(vehiculos, vehiculo_base=nombre, modo=modo)
    else:
        nacion = input(f"{LIGHT}  Nación:{RESET} ").strip()
        br_texto = input(f"{LIGHT}  BR objetivo:{RESET} ").strip()
        try:
            br = float(br_texto)
        except ValueError:
            print(f"\n{RED}✖ BR no válido.{RESET}\n")
            return
        resultado = generar_lineup(vehiculos, nacion=nacion, target_br=br, modo=modo)
    print(f"{ORANGE}{BOLD}└──────────────────────────────────────────┘{RESET}")
    if resultado["status"] != "ok":
        print(f"\n{RED}✖ {resultado['message']}{RESET}\n")
        if resultado.get("base"):
            base = resultado["base"]
            print(f"{DIM}Vehículo detectado: {base.get('name')} | Estado: {base.get('availability', 'no indicado')}{RESET}\n")
        return
    print(f"\n{GREEN}{BOLD}✓ LINEUP RECOMENDADO{RESET}")
    print(f"{DIM}Modo: {resultado['mode']} | Nación: {resultado['nation']} | BR de referencia: {resultado['target_br']}{RESET}\n")
    for numero, vehiculo in enumerate(resultado["lineup"], start=1):
        marca = " ← BASE" if resultado.get("base") is vehiculo else ""
        print(f"{ORANGE}{numero}.{RESET} {LIGHT}{vehiculo.get('name', 'N/D')}{RESET} — {vehiculo.get('role', 'Rol no indicado')}" + marca)
    print()


def analizar_preparacion(vehiculos):
    print(f"\n{ORANGE}{BOLD}┌── TECHNOLOGY JUMP / READINESS ─────────┐{RESET}")
    nombre = input(f"{LIGHT}  Vehículo a evaluar:{RESET} ").strip()
    vehiculo = buscar_vehiculo(vehiculos, nombre)
    if not vehiculo:
        print(f"\n{RED}✖ Vehículo no encontrado. No se inventará información.{RESET}\n")
        return
    modo = input(f"{LIGHT}  Modo (ej. Air RB / Ground RB):{RESET} ").strip() or "Ground RB"
    rango_texto = input(f"{LIGHT}  Tu rango habitual (I-X, opcional):{RESET} ").strip()
    br_texto = input(f"{LIGHT}  Tu BR habitual (opcional):{RESET} ").strip()
    try:
        rango = int(rango_texto) if rango_texto else None
        if rango is not None and not 1 <= rango <= 10:
            raise ValueError
    except ValueError:
        print(f"\n{RED}✖ Rango no válido.{RESET}\n")
        return
    try:
        br = float(br_texto) if br_texto else None
    except ValueError:
        print(f"\n{RED}✖ BR no válido.{RESET}\n")
        return

    reporte = readiness_report(rango, br, vehiculo, modo)
    salto = reporte["jump"]
    nivel = salto["level"]
    etiqueta = {"critical": "CRÍTICO", "high": "ALTO", "moderate": "MODERADO", "normal": "NORMAL", "unknown": "SIN DATOS"}[nivel]
    print(f"\n{YELLOW if reporte['warning'] else GREEN}{BOLD}● SALTO TECNOLÓGICO: {etiqueta}{RESET}")
    print(f"  Vehículo: {vehiculo.get('name')} | BR objetivo: {salto.get('target_br') or 'Pendiente'} | Rango: {salto.get('target_rank') or 'Pendiente'}")
    if salto["br_gap"] is not None:
        print(f"  Diferencia de BR: {salto['br_gap']:+.1f}")
    if salto["rank_gap"] is not None:
        print(f"  Diferencia de rango: {salto['rank_gap']:+d}")
    for reason in salto["reasons"]:
        print(f"  ⚠ {reason}")

    print(f"\n{ORANGE}{BOLD}TUTORIALES PRIORITARIOS{RESET}")
    for i, tutorial in enumerate(reporte["tutorials"], 1):
        print(f"  {i}. [{tutorial['level'].upper()}] {tutorial['title']}")
    print()


def ejecutar():
    vehiculos = cargar_vehiculos()
    while True:
        limpiar_pantalla()
        mostrar_encabezado()
        mostrar_menu()
        print(f"\n{DIM}Base de datos: {len(vehiculos)} vehículos cargados{RESET}")
        opcion = input(f"\n{ORANGE}{BOLD}WTGPT>{RESET} Selecciona una opción: ").strip()
        if opcion == "1":
            analizar_vehiculo(vehiculos)
            input(f"{DIM}Pulsa ENTER para volver al menú...{RESET}")
        elif opcion == "2":
            print(f"\n{ORANGE}[WTGPT]{RESET} Comparación de vehículos: próximamente.\n")
            input(f"{DIM}Pulsa ENTER para volver al menú...{RESET}")
        elif opcion == "3":
            print(f"\n{ORANGE}[WTGPT]{RESET} Módulo de economía: próximamente.\n")
            input(f"{DIM}Pulsa ENTER para volver al menú...{RESET}")
        elif opcion == "4":
            print(f"\n{ORANGE}[WTGPT]{RESET} Estadísticas: próximamente.\n")
            input(f"{DIM}Pulsa ENTER para volver al menú...{RESET}")
        elif opcion == "5":
            recomendar_lineup(vehiculos)
            input(f"{DIM}Pulsa ENTER para volver al menú...{RESET}")
        elif opcion == "6":
            analizar_preparacion(vehiculos)
            input(f"{DIM}Pulsa ENTER para volver al menú...{RESET}")
        elif opcion == "7":
            limpiar_pantalla()
            print(f"\n{ORANGE}{BOLD}WTGPT{RESET} cerrado. ¡Nos vemos en el campo de batalla! 🎮\n")
            break
        else:
            print(f"\n{RED}✖ Opción no válida. Inténtalo de nuevo.{RESET}")
            input(f"{DIM}Pulsa ENTER para continuar...")


if __name__ == "__main__":
    ejecutar()
