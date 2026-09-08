#!/usr/bin/env python3
"""Build WTGPT vehicle catalogs from the community War Thunder Vehicles API."""
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
AIRCRAFT_OUT = ROOT / "aircraft.json"
LIMIT = 200

NATION_MAP = {"usa":"Estados Unidos","us":"Estados Unidos","united states":"Estados Unidos","ussr":"URSS","soviet union":"URSS","russia":"URSS","germany":"Alemania","germ":"Alemania","frg":"Alemania","gdr":"Alemania","britain":"Gran Bretaña","great britain":"Gran Bretaña","uk":"Gran Bretaña","japan":"Japón","china":"China","italy":"Italia","france":"Francia","sweden":"Suecia","israel":"Israel"}
ROLE_MAP = {"fighter":"Caza","jet fighter":"Caza a reacción","bomber":"Bombardero","strike aircraft":"Avión de ataque","medium tank":"Tanque medio","light tank":"Tanque ligero","heavy tank":"Tanque pesado","tank destroyer":"Cazacarros","spaa":"Antiaéreo","atgm vehicle":"Vehículo ATGM","attack helicopter":"Helicóptero de ataque","utility helicopter":"Helicóptero utilitario","destroyer":"Destructor","light cruiser":"Crucero ligero","heavy cruiser":"Crucero pesado","battleship":"Acorazado","battlecruiser":"Crucero de batalla","frigate":"Fragata","boat":"Embarcación","torpedo boat":"Lancha torpedera"}
AIRCRAFT_HINTS = ("aircraft","fighter","bomber","strike","attacker","interceptor","reconnaissance","recon","naval aircraft","flying boat","floatplane","seaplane","glider","torpedo bomber","heavy fighter","light bomber","medium bomber","frontline bomber","assault aircraft","jet fighter")
HELICOPTER_HINTS = ("helicopter","rotorcraft")
GROUND_HINTS = ("tank","spaa","atgm","anti-aircraft","vehicle","artillery")
NAVAL_HINTS = ("destroyer","cruiser","battleship","battlecruiser","frigate","boat","ship","submarine")

# API identifiers commonly use nation prefixes. They are identifiers, not display names.
ID_PREFIXES = ("germ_","us_","usa_","ussr_","ru_","uk_","brit_","jp_","jpn_","cn_","ita_","it_","fr_","sw_","swe_","isr_","il_")

def norm(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip()).lower()

def first(obj: Any, keys: set[str]) -> Any:
    if isinstance(obj, dict):
        for k,v in obj.items():
            if norm(k) in keys and v not in (None,"",[],{}): return v
        for v in obj.values():
            found=first(v,keys)
            if found not in (None,"",[],{}): return found
    elif isinstance(obj,list):
        for v in obj:
            found=first(v,keys)
            if found not in (None,"",[],{}): return found
    return None

def number(value: Any) -> float|None:
    if isinstance(value,(int,float)) and not isinstance(value,bool): return float(value)
    if isinstance(value,str):
        m=re.search(r"\d+(?:\.\d+)?",value.replace(",","."))
        if m:return float(m.group())
    return None

def clean_number(value: float|None)->int|float|None:
    if value is None:return None
    return int(value) if value.is_integer() else value

def extract_br(row:dict[str,Any],mode:str)->float|None:
    keys={"rb":{"rb","realistic","realistic battle","realistic battles","realisticbattles","br_rb","rb_br","realistic_br"},"ab":{"ab","arcade","arcade battle","arcade battles","br_ab","ab_br","arcade_br"},"sb":{"sb","simulator","simulator battle","simulator battles","br_sb","sb_br","simulator_br"}}[mode]
    direct=first(row,keys); n=number(direct)
    if n is not None and 0<n<20:return n
    generic=first(row,{"br","battle rating","battlerating","battle_rating","rating"})
    if isinstance(generic,dict):
        for k,v in generic.items():
            if norm(k) in keys:
                n=number(v)
                if n is not None and 0<n<20:return n
    n=number(generic)
    return n if n is not None and 0<n<20 else None

def clean_identifier(value: str)->str:
    """Turn an internal ID into a readable fallback without exposing nation prefixes."""
    text=value.strip()
    lowered=text.lower()
    for prefix in ID_PREFIXES:
        if lowered.startswith(prefix):
            text=text[len(prefix):]
            break
    text=re.sub(r"_+"," ",text)
    text=re.sub(r"\s+"," ",text).strip()
    return text

def extract_name(row:dict[str,Any])->str:
    value=first(row,{"name","display_name","displayname","title","common_name","commonname","vehicle_name"})
    if isinstance(value,dict): value=next((v for v in value.values() if isinstance(v,str) and v.strip()),None)
    if isinstance(value,str) and value.strip(): return value.strip()
    raw=str(row.get("id") or row.get("identifier") or "Vehículo desconocido").strip()
    return clean_identifier(raw)

def extract_nation(row:dict[str,Any])->str:
    value=first(row,{"country","nation","nation_name","country_name","tree","operator"})
    if isinstance(value,dict): value=next((v for v in value.values() if isinstance(v,str) and v.strip()),None)
    return NATION_MAP.get(norm(value),str(value or "Desconocida").strip())

def extract_rank(row:dict[str,Any])->int|None:
    n=number(first(row,{"rank","tier","economic_rank","economicrank","era"}))
    return int(n) if n is not None and 1<=n<=10 else None

def extract_type(row:dict[str,Any])->str:
    value=first(row,{"type","vehicle_type","vehicletype","class","role","main_role","mainrole"})
    if isinstance(value,dict): value=next((v for v in value.values() if isinstance(v,str) and v.strip()),None)
    return str(value or "Desconocido").strip()

def role_name(raw:str)->str:
    key=norm(raw)
    for known,label in ROLE_MAP.items():
        if known in key:return label
    return raw or "Desconocido"

def category_name(raw_type:str)->str:
    key=norm(raw_type)
    if any(h in key for h in HELICOPTER_HINTS):return "helicopter"
    if any(h in key for h in NAVAL_HINTS):return "naval"
    if any(h in key for h in GROUND_HINTS):return "ground"
    if any(h in key for h in AIRCRAFT_HINTS):return "aircraft"
    return "unknown"

def extract_status(row:dict[str,Any])->str:
    text=norm(first(row,{"availability","availability_status","status","vehicle_status","purchasestatus"}))
    if "premium" in text:return "premium"
    if "squadron" in text:return "escuadrón"
    if "event" in text:return "evento"
    if "battle pass" in text or "battlepass" in text:return "Battle Pass"
    if "removed" in text or "retired" in text or "unavailable" in text:return "retirado"
    return "regular"

def row_id(row:dict[str,Any])->str:
    return str(row.get("identifier") or row.get("id") or row.get("vehicle_id") or row.get("gameId") or "").strip()

def fetch_all()->list[dict[str,Any]]:
    rows=[];seen=set();session=requests.Session();session.headers.update({"User-Agent":"WTGPT vehicle database synchronizer"})
    for page in range(100):
        response=session.get(API_URL,params={"limit":LIMIT,"page":page},timeout=30);response.raise_for_status();payload=response.json()
        if isinstance(payload,list):items=payload
        elif isinstance(payload,dict):items=next((payload[k] for k in ("data","items","results","vehicles") if isinstance(payload.get(k),list)),[])
        else:items=[]
        if not items:break
        added=0
        for row in items:
            if not isinstance(row,dict):continue
            ident=row_id(row)
            if ident and ident not in seen:seen.add(ident);rows.append(row);added+=1
        print(f"Página {page}: {len(items)} recibidos, {added} nuevos")
        if len(items)<LIMIT or added==0:break
    if len(rows)<100:raise RuntimeError(f"La API devolvió solo {len(rows)} vehículos; se cancela para evitar reemplazar la base con datos incompletos.")
    return rows

def load_manual()->dict[str,dict[str,Any]]:
    if not OUT.exists():return {}
    data=json.loads(OUT.read_text(encoding="utf-8"));return {norm(v.get("name")):v for v in data.get("vehicles",[]) }

def rank_sort_value(value:Any)->int:
    n=number(value)
    if n is not None and 1<=n<=10:return int(n)
    return {"i":1,"ii":2,"iii":3,"iv":4,"v":5,"vi":6,"vii":7,"viii":8,"ix":9,"x":10}.get(norm(value),99)

def main()->int:
    manual=load_manual();rows=fetch_all();vehicles={}
    for row in rows:
        name=extract_name(row);key=norm(name);existing=manual.get(key,{}) ;raw_type=extract_type(row)
        entry={"name":name,"nation":extract_nation(row),"type":raw_type,"category":category_name(raw_type),"rank":extract_rank(row),"br":clean_number(extract_br(row,"rb")),"br_ab":clean_number(extract_br(row,"ab")),"br_sb":clean_number(extract_br(row,"sb")),"role":role_name(raw_type),"availability":existing.get("availability") or extract_status(row),"source":"WT Vehicles API","source_id":row_id(row)}
        for field in ("nation","type","category","rank","br","br_ab","br_sb","role"):
            if entry[field] in (None,"","Desconocida","Desconocido","unknown") and existing.get(field) not in (None,""):entry[field]=existing[field]
        vehicles[key]=entry
    for key,entry in manual.items():
        if key not in vehicles:
            entry=dict(entry);entry.setdefault("source","manual-curation");entry.setdefault("category",category_name(str(entry.get("type",""))));vehicles[key]=entry
    output=sorted(vehicles.values(),key=lambda v:(str(v.get("nation")),rank_sort_value(v.get("rank")),str(v.get("name"))))
    aircraft=[v for v in output if v.get("category")=="aircraft"]
    AIRCRAFT_OUT.write_text(json.dumps({"vehicles":aircraft},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    OUT.write_text(json.dumps({"vehicles":output},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"WTGPT: {len(output)} vehículos escritos en {OUT}");print(f"WTGPT: {len(aircraft)} aviones escritos en {AIRCRAFT_OUT}");return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:print(f"ERROR: {exc}",file=sys.stderr);raise
