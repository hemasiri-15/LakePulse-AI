"""
LakePulse AI — Complete Database Seed Script
=============================================
Run this ONCE to populate your live Railway database with:
  - All 48 lakes
  - Realistic sensor readings (90 days of history per pilot lake)
  - AI predictions for each lake
  - Sample citizen reports
  - Sample alerts

USAGE:
  # Against Railway (production):
  DATABASE_URL="postgresql+asyncpg://USER:PASS@HOST:PORT/DB" python seed.py

  # Or set it from Railway's dashboard (Settings → Variables → DATABASE_URL)
  # Railway gives you a postgres:// URL — the script converts it automatically

  # Locally with docker compose running:
  python seed.py

HOW TO GET YOUR RAILWAY DATABASE_URL:
  1. Go to https://railway.app/project/YOUR_PROJECT
  2. Click your PostgreSQL service
  3. Click "Connect" tab
  4. Copy the "Postgres Connection URL"
  5. Run: DATABASE_URL="postgres://..." python seed.py
"""

import asyncio
import os
import math
import random
from datetime import datetime, timedelta

# Convert Railway's postgres:// → postgresql+asyncpg://
raw_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://lakepulse:lakepulse@localhost:5432/lakepulse"
)
DB_URL = raw_url.replace("postgres://", "postgresql+asyncpg://").replace("postgresql://", "postgresql+asyncpg://")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, select

engine = create_async_engine(DB_URL, echo=False)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ── ALL 48 LAKES ──────────────────────────────────────────────────────────────
ALL_LAKES = [
    # PILOT LAKES (IoT enabled)
    {"id":"hussain_sagar",   "name":"Hussain Sagar",        "city":"Hyderabad",   "state":"Telangana",       "lat":17.424,"lng":78.474,"area_km2":5.7,  "depth_m":8.2, "lake_type":"freshwater","category":"urban",     "is_pilot":True, "cpcb_station":"TG_HYD_003","health_score":42,"status":"critical","trend":"stable",   "do":3.2,"ph":8.1,"temp":29,"tds":890, "turb":34,"chl":54,"bloom":0.71,"mosq":0.65},
    {"id":"pragathi_nagar",  "name":"Pragathi Nagar Lake",  "city":"Hyderabad",   "state":"Telangana",       "lat":17.52, "lng":78.39, "area_km2":1.9,  "depth_m":3.1, "lake_type":"freshwater","category":"urban",     "is_pilot":True, "cpcb_station":"TG_HYD_012","health_score":28,"status":"critical","trend":"declining","do":1.6,"ph":8.7,"temp":31,"tds":1240,"turb":65,"chl":78,"bloom":0.88,"mosq":0.82},
    {"id":"bellandur",       "name":"Bellandur Lake",        "city":"Bengaluru",   "state":"Karnataka",       "lat":12.921,"lng":77.670,"area_km2":3.6,  "depth_m":2.4, "lake_type":"freshwater","category":"urban",     "is_pilot":True, "cpcb_station":"KA_BLRU_001","health_score":18,"status":"critical","trend":"declining","do":0.9,"ph":9.2,"temp":27,"tds":2100,"turb":92,"chl":91,"bloom":0.92,"mosq":0.74},
    {"id":"dal",             "name":"Dal Lake",              "city":"Srinagar",    "state":"J&K",             "lat":34.090,"lng":74.850,"area_km2":18.0, "depth_m":6.0, "lake_type":"freshwater","category":"highland",  "is_pilot":True, "cpcb_station":"JK_SRG_001","health_score":44,"status":"critical","trend":"declining","do":4.1,"ph":7.9,"temp":16,"tds":720, "turb":28,"chl":46,"bloom":0.56,"mosq":0.50},
    {"id":"deepor_beel",     "name":"Deepor Beel",           "city":"Guwahati",    "state":"Assam",           "lat":26.080,"lng":91.630,"area_km2":4.1,  "depth_m":2.8, "lake_type":"freshwater","category":"wetland",   "is_pilot":True, "cpcb_station":None,         "health_score":36,"status":"critical","trend":"declining","do":3.2,"ph":8.4,"temp":27,"tds":1100,"turb":54,"chl":70,"bloom":0.78,"mosq":0.75},
    # SOUTH INDIA
    {"id":"vembanad",        "name":"Vembanad Lake",         "city":"Kochi",       "state":"Kerala",          "lat":9.600, "lng":76.400,"area_km2":2033, "depth_m":11.8,"lake_type":"brackish",  "category":"brackish",  "is_pilot":False,"cpcb_station":"KL_KOC_001","health_score":71,"status":"good",    "trend":"improving","do":7.2,"ph":7.1,"temp":27,"tds":310, "turb":8, "chl":18,"bloom":0.22,"mosq":0.18},
    {"id":"ashtamudi",       "name":"Ashtamudi Lake",        "city":"Kollam",      "state":"Kerala",          "lat":8.950, "lng":76.600,"area_km2":614,  "depth_m":7.2, "lake_type":"brackish",  "category":"brackish",  "is_pilot":False,"cpcb_station":None,         "health_score":66,"status":"good",    "trend":"stable",   "do":6.8,"ph":7.3,"temp":28,"tds":290, "turb":9, "chl":14,"bloom":0.19,"mosq":0.15},
    {"id":"sasthamkotta",    "name":"Sasthamkotta Lake",     "city":"Kollam",      "state":"Kerala",          "lat":9.050, "lng":76.640,"area_km2":3.8,  "depth_m":9.1, "lake_type":"freshwater","category":"ecological", "is_pilot":False,"cpcb_station":None,         "health_score":74,"status":"good",    "trend":"stable",   "do":7.6,"ph":7.0,"temp":27,"tds":260, "turb":5, "chl":10,"bloom":0.12,"mosq":0.10},
    {"id":"kolleru",         "name":"Kolleru Lake",          "city":"Krishna",     "state":"Andhra Pradesh",  "lat":16.600,"lng":81.150,"area_km2":901,  "depth_m":4.6, "lake_type":"freshwater","category":"wetland",   "is_pilot":False,"cpcb_station":None,         "health_score":52,"status":"moderate","trend":"stable",   "do":4.9,"ph":7.8,"temp":29,"tds":510, "turb":21,"chl":38,"bloom":0.52,"mosq":0.48},
    {"id":"nagarjuna_sagar", "name":"Nagarjuna Sagar",       "city":"Nalgonda",    "state":"Telangana",       "lat":16.570,"lng":79.310,"area_km2":285,  "depth_m":26,  "lake_type":"freshwater","category":"reservoir",  "is_pilot":False,"cpcb_station":None,         "health_score":58,"status":"moderate","trend":"stable",   "do":5.8,"ph":7.5,"temp":30,"tds":420, "turb":15,"chl":28,"bloom":0.39,"mosq":0.35},
    {"id":"pulicat",         "name":"Pulicat Lake",          "city":"Nellore",     "state":"Andhra Pradesh",  "lat":13.600,"lng":80.200,"area_km2":759,  "depth_m":3.8, "lake_type":"brackish",  "category":"brackish",  "is_pilot":False,"cpcb_station":None,         "health_score":63,"status":"good",    "trend":"declining","do":6.2,"ph":7.4,"temp":28,"tds":380, "turb":12,"chl":22,"bloom":0.31,"mosq":0.27},
    {"id":"kaliveli",        "name":"Kaliveli Lake",         "city":"Puducherry",  "state":"Tamil Nadu",      "lat":11.920,"lng":79.670,"area_km2":61,   "depth_m":2.5, "lake_type":"brackish",  "category":"brackish",  "is_pilot":False,"cpcb_station":None,         "health_score":49,"status":"moderate","trend":"declining","do":4.6,"ph":7.9,"temp":29,"tds":620, "turb":24,"chl":42,"bloom":0.55,"mosq":0.51},
    {"id":"chembarambakkam", "name":"Chembarambakkam Lake",  "city":"Chennai",     "state":"Tamil Nadu",      "lat":12.970,"lng":80.050,"area_km2":52,   "depth_m":6.0, "lake_type":"freshwater","category":"reservoir",  "is_pilot":False,"cpcb_station":None,         "health_score":55,"status":"moderate","trend":"stable",   "do":5.3,"ph":7.6,"temp":28,"tds":480, "turb":18,"chl":31,"bloom":0.44,"mosq":0.40},
    {"id":"ulsoor",          "name":"Ulsoor Lake",           "city":"Bengaluru",   "state":"Karnataka",       "lat":12.982,"lng":77.619,"area_km2":1.2,  "depth_m":6.7, "lake_type":"freshwater","category":"urban",     "is_pilot":False,"cpcb_station":None,         "health_score":55,"status":"moderate","trend":"stable",   "do":5.4,"ph":7.6,"temp":26,"tds":510, "turb":18,"chl":34,"bloom":0.44,"mosq":0.42},
    {"id":"chilika",         "name":"Chilika Lake",          "city":"Puri",        "state":"Odisha",          "lat":19.720,"lng":85.320,"area_km2":1100, "depth_m":4.2, "lake_type":"brackish",  "category":"brackish",  "is_pilot":False,"cpcb_station":None,         "health_score":76,"status":"good",    "trend":"stable",   "do":7.8,"ph":7.2,"temp":26,"tds":280, "turb":6, "chl":10,"bloom":0.14,"mosq":0.10},
    # MAHARASHTRA
    {"id":"lonar",           "name":"Lonar Lake",            "city":"Buldhana",    "state":"Maharashtra",     "lat":19.970,"lng":76.510,"area_km2":1.1,  "depth_m":6.1, "lake_type":"saline",    "category":"saline",    "is_pilot":False,"cpcb_station":None,         "health_score":61,"status":"good",    "trend":"stable",   "do":6.1,"ph":7.4,"temp":27,"tds":440, "turb":13,"chl":24,"bloom":0.34,"mosq":0.28},
    {"id":"shivsagar",       "name":"Shivsagar Lake",        "city":"Satara",      "state":"Maharashtra",     "lat":17.850,"lng":73.750,"area_km2":891,  "depth_m":44,  "lake_type":"freshwater","category":"reservoir",  "is_pilot":False,"cpcb_station":None,         "health_score":67,"status":"good",    "trend":"stable",   "do":6.7,"ph":7.2,"temp":26,"tds":320, "turb":10,"chl":18,"bloom":0.24,"mosq":0.20},
    {"id":"powai",           "name":"Powai Lake",            "city":"Mumbai",      "state":"Maharashtra",     "lat":19.127,"lng":72.905,"area_km2":2.2,  "depth_m":12.4,"lake_type":"freshwater","category":"urban",     "is_pilot":False,"cpcb_station":None,         "health_score":61,"status":"moderate","trend":"improving", "do":6.1,"ph":7.4,"temp":28,"tds":420, "turb":14,"chl":24,"bloom":0.34,"mosq":0.32},
    {"id":"rankala",         "name":"Rankala Lake",          "city":"Kolhapur",    "state":"Maharashtra",     "lat":16.693,"lng":74.228,"area_km2":1.8,  "depth_m":4.1, "lake_type":"freshwater","category":"urban",     "is_pilot":False,"cpcb_station":None,         "health_score":49,"status":"moderate","trend":"stable",   "do":4.8,"ph":7.7,"temp":27,"tds":680, "turb":22,"chl":40,"bloom":0.53,"mosq":0.47},
    # RAJASTHAN / GUJARAT
    {"id":"sambhar",         "name":"Sambhar Lake",          "city":"Jaipur",      "state":"Rajasthan",       "lat":26.970,"lng":75.150,"area_km2":230,  "depth_m":3.0, "lake_type":"saline",    "category":"saline",    "is_pilot":False,"cpcb_station":None,         "health_score":76,"status":"good",    "trend":"stable",   "do":7.4,"ph":7.1,"temp":26,"tds":280, "turb":6, "chl":9, "bloom":0.12,"mosq":0.10},
    {"id":"nakki",           "name":"Nakki Lake",            "city":"Mount Abu",   "state":"Rajasthan",       "lat":24.600,"lng":72.720,"area_km2":0.3,  "depth_m":11,  "lake_type":"freshwater","category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":68,"status":"good",    "trend":"stable",   "do":7.0,"ph":7.3,"temp":22,"tds":340, "turb":9, "chl":16,"bloom":0.21,"mosq":0.16},
    {"id":"rajsamand",       "name":"Rajsamand Lake",        "city":"Rajsamand",   "state":"Rajasthan",       "lat":25.070,"lng":73.880,"area_km2":6.5,  "depth_m":12.5,"lake_type":"freshwater","category":"reservoir",  "is_pilot":False,"cpcb_station":None,         "health_score":62,"status":"good",    "trend":"stable",   "do":6.2,"ph":7.5,"temp":25,"tds":460, "turb":16,"chl":26,"bloom":0.35,"mosq":0.30},
    {"id":"pichola",         "name":"Lake Pichola",          "city":"Udaipur",     "state":"Rajasthan",       "lat":24.570,"lng":73.680,"area_km2":4.4,  "depth_m":8.5, "lake_type":"freshwater","category":"urban",     "is_pilot":False,"cpcb_station":None,         "health_score":57,"status":"moderate","trend":"declining", "do":5.7,"ph":7.6,"temp":24,"tds":530, "turb":20,"chl":34,"bloom":0.45,"mosq":0.39},
    {"id":"pushkar",         "name":"Pushkar Lake",          "city":"Pushkar",     "state":"Rajasthan",       "lat":26.490,"lng":74.550,"area_km2":0.2,  "depth_m":3.0, "lake_type":"saline",    "category":"saline",    "is_pilot":False,"cpcb_station":None,         "health_score":46,"status":"moderate","trend":"declining", "do":4.4,"ph":8.0,"temp":26,"tds":720, "turb":28,"chl":46,"bloom":0.58,"mosq":0.52},
    {"id":"sardar_sarovar",  "name":"Sardar Sarovar",        "city":"Kevadiya",    "state":"Gujarat",         "lat":21.830,"lng":73.740,"area_km2":370,  "depth_m":138, "lake_type":"freshwater","category":"reservoir",  "is_pilot":False,"cpcb_station":None,         "health_score":69,"status":"good",    "trend":"stable",   "do":6.9,"ph":7.3,"temp":27,"tds":350, "turb":11,"chl":19,"bloom":0.26,"mosq":0.21},
    {"id":"nal",             "name":"Nal Lake",              "city":"Kachchh",     "state":"Gujarat",         "lat":23.260,"lng":68.830,"area_km2":120,  "depth_m":1.5, "lake_type":"saline",    "category":"saline",    "is_pilot":False,"cpcb_station":None,         "health_score":72,"status":"good",    "trend":"stable",   "do":7.2,"ph":7.2,"temp":28,"tds":310, "turb":7, "chl":11,"bloom":0.15,"mosq":0.12},
    {"id":"salim_ali",       "name":"Salim Ali Lake",        "city":"Panaji",      "state":"Goa",             "lat":15.490,"lng":73.840,"area_km2":0.6,  "depth_m":3.2, "lake_type":"freshwater","category":"ecological", "is_pilot":False,"cpcb_station":None,         "health_score":71,"status":"good",    "trend":"improving", "do":7.1,"ph":7.2,"temp":27,"tds":300, "turb":7, "chl":12,"bloom":0.18,"mosq":0.14},
    # NORTH INDIA
    {"id":"wular",           "name":"Wular Lake",            "city":"Bandipora",   "state":"J&K",             "lat":34.350,"lng":74.550,"area_km2":189,  "depth_m":5.8, "lake_type":"freshwater","category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":58,"status":"moderate","trend":"declining", "do":5.8,"ph":7.5,"temp":14,"tds":410, "turb":14,"chl":22,"bloom":0.30,"mosq":0.24},
    {"id":"pangong",         "name":"Pangong Tso",           "city":"Leh",         "state":"Ladakh",          "lat":33.720,"lng":78.650,"area_km2":700,  "depth_m":100, "lake_type":"saline",    "category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":88,"status":"good",    "trend":"stable",   "do":8.8,"ph":7.0,"temp":8, "tds":190, "turb":3, "chl":4, "bloom":0.04,"mosq":0.02},
    {"id":"tso_moriri",      "name":"Tso Moriri",            "city":"Leh",         "state":"Ladakh",          "lat":32.900,"lng":78.300,"area_km2":120,  "depth_m":120, "lake_type":"saline",    "category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":86,"status":"good",    "trend":"stable",   "do":8.6,"ph":7.1,"temp":7, "tds":210, "turb":3, "chl":5, "bloom":0.05,"mosq":0.02},
    {"id":"nainital",        "name":"Naini Lake",            "city":"Nainital",    "state":"Uttarakhand",     "lat":29.380,"lng":79.460,"area_km2":0.5,  "depth_m":27.3,"lake_type":"freshwater","category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":64,"status":"good",    "trend":"declining","do":7.5,"ph":7.0,"temp":18,"tds":290, "turb":9, "chl":15,"bloom":0.20,"mosq":0.14},
    {"id":"bhimtal",         "name":"Bhimtal Lake",          "city":"Nainital",    "state":"Uttarakhand",     "lat":29.340,"lng":79.560,"area_km2":0.5,  "depth_m":26,  "lake_type":"freshwater","category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":69,"status":"good",    "trend":"stable",   "do":6.9,"ph":7.2,"temp":19,"tds":320, "turb":10,"chl":17,"bloom":0.22,"mosq":0.16},
    {"id":"roopkund",        "name":"Roopkund Lake",         "city":"Chamoli",     "state":"Uttarakhand",     "lat":30.240,"lng":79.720,"area_km2":0.04, "depth_m":5.0, "lake_type":"freshwater","category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":91,"status":"good",    "trend":"stable",   "do":9.1,"ph":6.8,"temp":4, "tds":160, "turb":2, "chl":3, "bloom":0.03,"mosq":0.01},
    {"id":"chandra_taal",    "name":"Chandra Taal",          "city":"Lahaul",      "state":"Himachal Pradesh","lat":32.490,"lng":77.620,"area_km2":2.6,  "depth_m":35,  "lake_type":"freshwater","category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":89,"status":"good",    "trend":"stable",   "do":8.9,"ph":6.9,"temp":5, "tds":180, "turb":2, "chl":4, "bloom":0.04,"mosq":0.01},
    {"id":"gobind_sagar",    "name":"Gobind Sagar",          "city":"Bilaspur",    "state":"Himachal Pradesh","lat":31.450,"lng":76.420,"area_km2":168,  "depth_m":90,  "lake_type":"freshwater","category":"reservoir",  "is_pilot":False,"cpcb_station":None,         "health_score":65,"status":"good",    "trend":"stable",   "do":6.5,"ph":7.4,"temp":22,"tds":380, "turb":12,"chl":20,"bloom":0.27,"mosq":0.22},
    {"id":"renuka",          "name":"Renuka Lake",           "city":"Sirmaur",     "state":"Himachal Pradesh","lat":30.610,"lng":77.460,"area_km2":0.2,  "depth_m":6.5, "lake_type":"freshwater","category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":72,"status":"good",    "trend":"stable",   "do":7.2,"ph":7.1,"temp":20,"tds":300, "turb":7, "chl":12,"bloom":0.16,"mosq":0.11},
    {"id":"maharana_pratap", "name":"Maharana Pratap Sagar", "city":"Kangra",      "state":"Himachal Pradesh","lat":32.060,"lng":75.960,"area_km2":23,   "depth_m":65,  "lake_type":"freshwater","category":"reservoir",  "is_pilot":False,"cpcb_station":None,         "health_score":67,"status":"good",    "trend":"stable",   "do":6.7,"ph":7.3,"temp":21,"tds":360, "turb":11,"chl":18,"bloom":0.24,"mosq":0.18},
    {"id":"brahma_sarovar",  "name":"Brahma Sarovar",        "city":"Kurukshetra", "state":"Haryana",         "lat":29.970,"lng":76.820,"area_km2":0.2,  "depth_m":2.5, "lake_type":"freshwater","category":"urban",     "is_pilot":False,"cpcb_station":None,         "health_score":53,"status":"moderate","trend":"stable",   "do":5.2,"ph":7.7,"temp":25,"tds":570, "turb":19,"chl":32,"bloom":0.42,"mosq":0.37},
    {"id":"harike",          "name":"Harike Lake",           "city":"Ferozepur",   "state":"Punjab",          "lat":31.150,"lng":74.940,"area_km2":86,   "depth_m":4.0, "lake_type":"freshwater","category":"wetland",   "is_pilot":False,"cpcb_station":None,         "health_score":59,"status":"moderate","trend":"stable",   "do":5.9,"ph":7.6,"temp":23,"tds":450, "turb":16,"chl":27,"bloom":0.36,"mosq":0.31},
    {"id":"kanjli",          "name":"Kanjli Lake",           "city":"Kapurthala",  "state":"Punjab",          "lat":31.370,"lng":75.370,"area_km2":1.8,  "depth_m":3.5, "lake_type":"freshwater","category":"wetland",   "is_pilot":False,"cpcb_station":None,         "health_score":56,"status":"moderate","trend":"stable",   "do":5.5,"ph":7.6,"temp":24,"tds":490, "turb":17,"chl":29,"bloom":0.39,"mosq":0.33},
    {"id":"indira_sagar",    "name":"Indira Sagar Lake",     "city":"Khandwa",     "state":"Madhya Pradesh",  "lat":22.300,"lng":76.460,"area_km2":913,  "depth_m":92,  "lake_type":"freshwater","category":"reservoir",  "is_pilot":False,"cpcb_station":None,         "health_score":63,"status":"good",    "trend":"stable",   "do":6.3,"ph":7.4,"temp":27,"tds":400, "turb":13,"chl":21,"bloom":0.28,"mosq":0.23},
    {"id":"bhojtal",         "name":"Bhojtal Lake",          "city":"Bhopal",      "state":"Madhya Pradesh",  "lat":23.240,"lng":77.350,"area_km2":31,   "depth_m":5.5, "lake_type":"freshwater","category":"urban",     "is_pilot":False,"cpcb_station":None,         "health_score":48,"status":"moderate","trend":"declining", "do":4.6,"ph":8.0,"temp":27,"tds":670, "turb":26,"chl":44,"bloom":0.56,"mosq":0.50},
    {"id":"gbp_sagar",       "name":"Govind Ballabh Pant Sagar","city":"Sonbhadra","state":"Uttar Pradesh",   "lat":24.170,"lng":82.570,"area_km2":466,  "depth_m":73,  "lake_type":"freshwater","category":"reservoir",  "is_pilot":False,"cpcb_station":None,         "health_score":61,"status":"good",    "trend":"stable",   "do":6.1,"ph":7.5,"temp":27,"tds":430, "turb":14,"chl":22,"bloom":0.30,"mosq":0.24},
    {"id":"kanwar_taal",     "name":"Kanwar Taal",           "city":"Begusarai",   "state":"Bihar",           "lat":25.730,"lng":86.110,"area_km2":67,   "depth_m":3.0, "lake_type":"freshwater","category":"wetland",   "is_pilot":False,"cpcb_station":None,         "health_score":39,"status":"critical","trend":"declining", "do":3.6,"ph":8.3,"temp":28,"tds":980, "turb":48,"chl":64,"bloom":0.74,"mosq":0.70},
    # NORTH EAST
    {"id":"loktak",          "name":"Loktak Lake",           "city":"Imphal",      "state":"Manipur",         "lat":24.500,"lng":93.800,"area_km2":287,  "depth_m":3.8, "lake_type":"freshwater","category":"wetland",   "is_pilot":False,"cpcb_station":None,         "health_score":57,"status":"moderate","trend":"declining", "do":5.8,"ph":7.2,"temp":22,"tds":380, "turb":12,"chl":21,"bloom":0.29,"mosq":0.24},
    {"id":"cholamu",         "name":"Cholamu Lake",          "city":"Gangtok",     "state":"Sikkim",          "lat":27.990,"lng":88.550,"area_km2":1.3,  "depth_m":20,  "lake_type":"freshwater","category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":87,"status":"good",    "trend":"stable",   "do":8.7,"ph":6.8,"temp":4, "tds":170, "turb":2, "chl":3, "bloom":0.03,"mosq":0.01},
    {"id":"tsomgo",          "name":"Tsomgo Lake",           "city":"Gangtok",     "state":"Sikkim",          "lat":27.370,"lng":88.760,"area_km2":1.7,  "depth_m":15,  "lake_type":"freshwater","category":"highland",  "is_pilot":False,"cpcb_station":None,         "health_score":85,"status":"good",    "trend":"stable",   "do":8.5,"ph":6.9,"temp":5, "tds":185, "turb":2, "chl":4, "bloom":0.04,"mosq":0.01},
]

SAMPLE_REPORTS = [
    {"lake_id":"pragathi_nagar","reporter_name":"Ravi Kumar","issue_type":"Illegal Dumping","description":"Large construction debris near north inlet gate. Blocking water flow.","status":"Escalated","escalated_to":"GHMC / Municipal Corporation"},
    {"lake_id":"bellandur","reporter_name":"Ananya Mehta","issue_type":"Foam Formation","description":"Thick toxic foam covering approximately 40% of lake surface, strong smell.","status":"Under Review","escalated_to":"KSPCB / State PCB"},
    {"lake_id":"hussain_sagar","reporter_name":"Suresh Patel","issue_type":"Dead Fish","description":"Hundreds of dead fish washing up on eastern shore since morning.","status":"Action Taken","escalated_to":"State Fisheries Dept + TSPCB"},
    {"lake_id":"dal","reporter_name":"Farhan Ahmed","issue_type":"Sewage Discharge","description":"Dark discharge from storm drain near south bank, strong odour.","status":"Escalated","escalated_to":"TSPCB / Municipal Corp"},
    {"lake_id":"deepor_beel","reporter_name":"Priya Nath","issue_type":"Illegal Dumping","description":"Municipal solid waste being dumped along western boundary daily.","status":"Logged","escalated_to":"GHMC / Municipal Corporation"},
    {"lake_id":"loktak","reporter_name":"Thoibi Devi","issue_type":"Algal Bloom","description":"Green algal mat covering phumdis area, fish kills visible.","status":"Logged","escalated_to":"Lake Development Authority + TSPCB"},
    {"lake_id":"bhojtal","reporter_name":"Ramesh Verma","issue_type":"Sewage Discharge","description":"Untreated sewage entering lake from colony drain near Bhopal road.","status":"Escalated","escalated_to":"TSPCB / Municipal Corp"},
]

SAMPLE_ALERTS = [
    {"lake_id":"pragathi_nagar","severity":"critical","category":"Oxygenation","parameter":"do_mgl","value":1.6,"threshold":2.0,"message":"DO critically low: 1.6 mg/L — hypoxic conditions","action":"Deploy surface aerators immediately","agency":"TSPCB / GHMC","timeline":"Within 24 hours"},
    {"lake_id":"pragathi_nagar","severity":"critical","category":"Algal Bloom Control","parameter":"bloom_risk","value":0.88,"threshold":0.85,"message":"Bloom risk 88% with Chl-a 78 μg/L — cyanobacteria bloom imminent","action":"Apply copper sulfate at 0.5–1 ppm","agency":"State Fisheries + TSPCB","timeline":"Within 48 hours"},
    {"lake_id":"bellandur","severity":"critical","category":"Oxygenation","parameter":"do_mgl","value":0.9,"threshold":2.0,"message":"DO at 0.9 mg/L — near anoxic. Mass fish kill risk.","action":"Emergency aeration + block sewage inflows","agency":"KSPCB / BBMP","timeline":"Within 24 hours"},
    {"lake_id":"bellandur","severity":"critical","category":"Chemical Balance","parameter":"ph","value":9.2,"threshold":9.0,"message":"pH 9.2 indicates severe algal bloom in progress","action":"CO₂ aeration to lower pH below 8.5","agency":"KSPCB","timeline":"Within 48 hours"},
    {"lake_id":"hussain_sagar","severity":"high","category":"Algal Bloom Control","parameter":"bloom_risk","value":0.71,"threshold":0.70,"message":"Bloom probability 71% — pre-bloom stage","action":"Deploy barley straw bales, increase sampling to daily","agency":"Lake Development Authority","timeline":"Within 72 hours"},
    {"lake_id":"dal","severity":"high","category":"Waste Management","parameter":"turb_ntu","value":28,"threshold":25,"message":"Turbidity elevated at 28 NTU from houseboat waste","action":"Install silt curtains, enforce houseboat waste regulations","agency":"JK Pollution Control Committee","timeline":"Within 1 week"},
    {"lake_id":"kanwar_taal","severity":"critical","category":"Algal Bloom Control","parameter":"bloom_risk","value":0.74,"threshold":0.70,"message":"Critical bloom risk 74% in Ramsar wetland site","action":"Coordinate with Ramsar authority for emergency intervention","agency":"State PCB / Forest Dept","timeline":"Within 48 hours"},
]


async def seed():
    async with engine.begin() as conn:
        # Create all tables
        from sqlalchemy import text as t
        print("Creating tables...")

        await conn.execute(t("""
            CREATE TABLE IF NOT EXISTS lakes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT, state TEXT,
                lat FLOAT, lng FLOAT,
                area_km2 FLOAT, depth_m FLOAT,
                lake_type TEXT, category TEXT,
                is_pilot BOOLEAN DEFAULT FALSE,
                cpcb_station TEXT,
                health_score INTEGER DEFAULT 50,
                status TEXT DEFAULT 'moderate',
                trend TEXT DEFAULT 'stable',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """))

        await conn.execute(t("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id SERIAL PRIMARY KEY,
                lake_id TEXT REFERENCES lakes(id),
                node_id TEXT DEFAULT 'unknown',
                timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
                do_mgl FLOAT, ph FLOAT, temp_c FLOAT,
                tds_ppm FLOAT, turb_ntu FLOAT,
                source TEXT DEFAULT 'iot'
            )
        """))
        await conn.execute(t("CREATE INDEX IF NOT EXISTS idx_sensor_lake_time ON sensor_readings (lake_id, timestamp)"))

        await conn.execute(t("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                lake_id TEXT REFERENCES lakes(id),
                predicted_at TIMESTAMP DEFAULT NOW(),
                horizon_days INTEGER DEFAULT 7,
                do_mean FLOAT, do_std FLOAT, do_ci_low FLOAT, do_ci_high FLOAT,
                ph_mean FLOAT, temp_mean FLOAT, turbidity_mean FLOAT,
                chl_a_mean FLOAT, bloom_risk FLOAT, mosquito_risk FLOAT,
                attention_weights JSONB, model_version TEXT DEFAULT 'v2',
                latency_ms FLOAT
            )
        """))

        await conn.execute(t("""
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                lake_id TEXT REFERENCES lakes(id),
                created_at TIMESTAMP DEFAULT NOW(),
                severity TEXT, category TEXT, parameter TEXT,
                value FLOAT, threshold FLOAT,
                message TEXT, action TEXT, agency TEXT, timeline TEXT,
                is_resolved BOOLEAN DEFAULT FALSE,
                resolved_at TIMESTAMP
            )
        """))

        await conn.execute(t("""
            CREATE TABLE IF NOT EXISTS citizen_reports (
                id SERIAL PRIMARY KEY,
                lake_id TEXT REFERENCES lakes(id),
                submitted_at TIMESTAMP DEFAULT NOW(),
                reporter_name TEXT, issue_type TEXT,
                description TEXT, lat FLOAT, lng FLOAT,
                photo_url TEXT,
                status TEXT DEFAULT 'Logged',
                escalated_to TEXT, escalated_at TIMESTAMP
            )
        """))

        await conn.execute(t("""
            CREATE TABLE IF NOT EXISTS satellite_analyses (
                id SERIAL PRIMARY KEY,
                lake_id TEXT REFERENCES lakes(id),
                analyzed_at TIMESTAMP DEFAULT NOW(),
                water_area_km2 FLOAT, area_change_pct FLOAT,
                chl_a_ug_l FLOAT, bloom_detected BOOLEAN DEFAULT FALSE,
                lst_celsius FLOAT, thermal_anomaly_c FLOAT,
                encroachment_pct FLOAT, encroachment_risk TEXT,
                ndwi_series JSONB, chl_series JSONB, raw_report JSONB
            )
        """))

        await conn.execute(t("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_pw TEXT NOT NULL,
                role TEXT DEFAULT 'citizen',
                state TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                is_active BOOLEAN DEFAULT TRUE
            )
        """))

    print("✓ Tables created")

    async with Session() as db:

        # ── 1. SEED LAKES ─────────────────────────────────────────────────
        print(f"\nSeeding {len(ALL_LAKES)} lakes...")
        for lake_data in ALL_LAKES:
            do = lake_data.pop("do"); ph = lake_data.pop("ph"); temp = lake_data.pop("temp")
            tds = lake_data.pop("tds"); turb = lake_data.pop("turb")
            chl = lake_data.pop("chl"); bloom = lake_data.pop("bloom"); mosq = lake_data.pop("mosq")

            from sqlalchemy import text as t
            await db.execute(t("""
                INSERT INTO lakes (id,name,city,state,lat,lng,area_km2,depth_m,lake_type,category,
                                   is_pilot,cpcb_station,health_score,status,trend)
                VALUES (:id,:name,:city,:state,:lat,:lng,:area_km2,:depth_m,:lake_type,:category,
                        :is_pilot,:cpcb_station,:health_score,:status,:trend)
                ON CONFLICT (id) DO UPDATE SET
                    health_score=EXCLUDED.health_score, status=EXCLUDED.status, trend=EXCLUDED.trend
            """), lake_data)

            # Store sensor baseline back for readings
            lake_data.update({"do":do,"ph":ph,"temp":temp,"tds":tds,"turb":turb,
                              "chl":chl,"bloom":bloom,"mosq":mosq})

        await db.commit()
        print("✓ 48 lakes seeded")

        # ── 2. SEED 90 DAYS SENSOR HISTORY (pilot lakes only) ─────────────
        print("\nSeeding 90 days sensor history for 5 pilot lakes...")
        pilot_lakes = [l for l in ALL_LAKES if l.get("is_pilot")]
        readings_inserted = 0

        for lake in pilot_lakes:
            lid = lake["id"]
            base_do = lake["do"]; base_ph = lake["ph"]; base_temp = lake["temp"]
            base_tds = lake["tds"]; base_turb = lake["turb"]

            # One reading every 6 hours for 90 days = 360 readings per lake
            for day in range(90, 0, -1):
                for hour in [0, 6, 12, 18]:
                    ts = datetime.utcnow() - timedelta(days=day, hours=hour)
                    progress = (90 - day) / 90  # slight trend over time

                    do_val   = max(0.1, base_do   + random.gauss(0, 0.2) - progress * (0.3 if base_do < 3 else 0))
                    ph_val   = base_ph   + random.gauss(0, 0.05)
                    temp_val = base_temp + random.gauss(0, 0.5) + 2 * math.sin(2 * math.pi * (day/90))
                    tds_val  = max(10, base_tds  + random.gauss(0, 30))
                    turb_val = max(0, base_turb + random.gauss(0, 3))

                    await db.execute(text("""
                        INSERT INTO sensor_readings (lake_id, node_id, timestamp, do_mgl, ph, temp_c, tds_ppm, turb_ntu, source)
                        VALUES (:lid, :node, :ts, :do, :ph, :temp, :tds, :turb, :src)
                    """), {"lid":lid,"node":"node_001","ts":ts,
                           "do":round(do_val,2),"ph":round(ph_val,2),
                           "temp":round(temp_val,1),"tds":round(tds_val,0),
                           "turb":round(turb_val,1),"src":"synthetic_seed"})
                    readings_inserted += 1

        await db.commit()
        print(f"✓ {readings_inserted} sensor readings inserted")

        # ── 3. SEED PREDICTIONS ──────────────────────────────────────────
        print("\nSeeding predictions...")
        import json
        for lake in ALL_LAKES:
            lid = lake["id"]
            b = lake["do"] / 14.0
            w = [round(0.01 + i/29*0.08 + random.gauss(0,0.004), 3) for i in range(30)]

            await db.execute(text("""
                INSERT INTO predictions (lake_id, horizon_days, do_mean, do_std, do_ci_low, do_ci_high,
                                         ph_mean, temp_mean, turbidity_mean, chl_a_mean,
                                         bloom_risk, mosquito_risk, attention_weights, model_version, latency_ms)
                VALUES (:lid, 7, :do_m, :do_s, :do_lo, :do_hi, :ph, :temp, :turb, :chl,
                        :bloom, :mosq, CAST(:attn AS jsonb), 'v2', :lat_ms)
            """), {
                "lid":lid,
                "do_m":lake["do"], "do_s":round(0.3*(1.2-b),3),
                "do_lo":round(lake["do"]*0.82,2), "do_hi":round(lake["do"]*1.18,2),
                "ph":lake["ph"], "temp":lake["temp"], "turb":lake["turb"], "chl":lake["chl"],
                "bloom":lake["bloom"], "mosq":lake["mosq"],
                "attn":json.dumps(w), "lat_ms":round(10+random.random()*8,1)
            })
        await db.commit()
        print(f"✓ {len(ALL_LAKES)} predictions inserted")

        # ── 4. SEED ALERTS ───────────────────────────────────────────────
        print("\nSeeding alerts...")
        for a in SAMPLE_ALERTS:
            await db.execute(text("""
                INSERT INTO alerts (lake_id, severity, category, parameter, value, threshold,
                                    message, action, agency, timeline, is_resolved)
                VALUES (:lid, :sev, :cat, :param, :val, :thresh, :msg, :act, :agency, :tl, false)
            """), {"lid":a["lake_id"],"sev":a["severity"],"cat":a["category"],
                   "param":a["parameter"],"val":a["value"],"thresh":a["threshold"],
                   "msg":a["message"],"act":a["action"],"agency":a["agency"],"tl":a["timeline"]})
        await db.commit()
        print(f"✓ {len(SAMPLE_ALERTS)} alerts inserted")

        # ── 5. SEED CITIZEN REPORTS ──────────────────────────────────────
        print("\nSeeding citizen reports...")
        for r in SAMPLE_REPORTS:
            ts = datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            await db.execute(text("""
                INSERT INTO citizen_reports (lake_id, submitted_at, reporter_name, issue_type,
                                             description, status, escalated_to)
                VALUES (:lid, :ts, :name, :issue, :desc, :status, :esc)
            """), {"lid":r["lake_id"],"ts":ts,"name":r["reporter_name"],
                   "issue":r["issue_type"],"desc":r["description"],
                   "status":r["status"],"esc":r["escalated_to"]})
        await db.commit()
        print(f"✓ {len(SAMPLE_REPORTS)} citizen reports inserted")

        # ── 6. SEED SATELLITE ANALYSES ───────────────────────────────────
        print("\nSeeding satellite analysis data...")
        SAT = {
            "pragathi_nagar":{"area":1.59,"change":-18.5,"chl":72.4,"bloom":True, "lst":32.1,"anom":2.3,"enc_pct":12.1,"enc":"high"},
            "hussain_sagar":  {"area":4.91,"change":-14.8,"chl":54.0,"bloom":True, "lst":30.2,"anom":1.8,"enc_pct":8.3, "enc":"moderate"},
            "bellandur":      {"area":2.98,"change":-22.1,"chl":91.0,"bloom":True, "lst":28.9,"anom":1.4,"enc_pct":18.7,"enc":"high"},
            "dal":            {"area":14.8,"change":-19.3,"chl":46.0,"bloom":True, "lst":18.2,"anom":1.1,"enc_pct":9.2, "enc":"moderate"},
            "vembanad":       {"area":1981,"change":-2.6, "chl":18.0,"bloom":False,"lst":27.8,"anom":0.3,"enc_pct":1.2, "enc":"low"},
        }
        for lid, s in SAT.items():
            await db.execute(text("""
                INSERT INTO satellite_analyses
                    (lake_id, water_area_km2, area_change_pct, chl_a_ug_l, bloom_detected,
                     lst_celsius, thermal_anomaly_c, encroachment_pct, encroachment_risk)
                VALUES (:lid,:area,:change,:chl,:bloom,:lst,:anom,:enc_pct,:enc)
            """), {"lid":lid,"area":s["area"],"change":s["change"],"chl":s["chl"],
                   "bloom":s["bloom"],"lst":s["lst"],"anom":s["anom"],
                   "enc_pct":s["enc_pct"],"enc":s["enc"]})
        await db.commit()
        print("✓ Satellite data inserted")

    print("\n" + "="*50)
    print("✅  DATABASE FULLY SEEDED!")
    print("="*50)
    print(f"  Lakes:            {len(ALL_LAKES)}")
    print(f"  Sensor readings:  {readings_inserted}")
    print(f"  Predictions:      {len(ALL_LAKES)}")
    print(f"  Alerts:           {len(SAMPLE_ALERTS)}")
    print(f"  Citizen reports:  {len(SAMPLE_REPORTS)}")
    print(f"  Satellite:        {len(SAT)}")
    print("\nNow visit your /docs and test any endpoint!")


if __name__ == "__main__":
    asyncio.run(seed())
