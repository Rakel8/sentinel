import os
import psutil
import asyncio
import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from database import SessionLocal, LogSensor, engine, Base

Base.metadata.create_all(bind=engine)
print("Tabel database dipastikan siap!")

app = FastAPI()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def kirim_discord(judul, pesan, warna):
    # Warna Decimal: 
    # Merah = 15548997
    # Hijau = 5763719
    # Kuning = 16705372

    payload = {
        "embeds": [
            {
                "title": judul,
                "description": pesan,
                "color": warna,
                "footer": {
                    "text": "Sentinel Monitoring System • By Rakel"
                }
            }
        ]
    }
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Gagal kirim ke Discord: {e}")

def catat_ke_memori(cpu, ram, bat):
    db = SessionLocal() 
    try:
        
        catatan_baru = LogSensor(cpu=cpu, ram=ram, battery=bat)
        db.add(catatan_baru)
        db.commit() 
        print(f"Tercatat: CPU {cpu}%, RAM {ram}%") #diaktifkan kalau mau lihat lognya
    except Exception as e:
        print(f"Gagal mencatat: {e}")
    finally:
        db.close()

async def satpam_otomatis():
    print("SATPAM SENTINEL MULAI BERJAGA & MENCATAT...")
    
    while True:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        bat_percent = battery.percent if battery else 0
        
        catat_ke_memori(cpu, ram, bat_percent)
        
        if cpu > 80:
            kirim_discord("CPU ALERT", f"CPU Load: {cpu}%", 15548997)
            await asyncio.sleep(300)
            
        if battery is not None and battery.percent < 40:
            kirim_discord("BATTERY ALERT", f"Battery Percent: {battery.percent}%", 15548997)
            await asyncio.sleep(300)

        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(satpam_otomatis())


@app.get("/api/history")
def ambil_sejarah():
    db = SessionLocal() 
    try:
        logs = db.query(LogSensor).order_by(LogSensor.id.desc()).limit(30).all()
        
        hasil = []
        for log in reversed(logs): 
            hasil.append({
                "waktu": log.timestamp.strftime("%H:%M:%S"), # Format jam:menit:detik
                "cpu": log.cpu,
                "ram": log.ram,
                "baterai": log.battery
            })
        
        return hasil
    finally:
        db.close()

@app.get("/me")
def about_me():
    return {"role": "System Engineer", "skill": "Python"}

@app.get("/monitor")
def monitor():
    cpu_now = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    ram_used_gb = round(ram.used / (1024**3), 1)

    return {
        "Sentinel": "CPU and RAM Usage",
        "CPU": f"{cpu_now}%",
        "RAM": f"{ram.percent}% ({ram_used_gb} GB)" 
    }

#individual chekcing feature
@app.get("/monitor/{nama_fitur}")
def cek_fitur(nama_fitur: str):

    if nama_fitur == "cpu":
        cpu_now = psutil.cpu_percent()
        return {"CPU": f"{cpu_now}%"}
    elif nama_fitur == "ram":
        ram = psutil.virtual_memory()
        ram_used_gb = round(ram.used / (1024**3), 1)
        return {"RAM": f"{ram.percent}% ({ram_used_gb} GB)" }
    elif nama_fitur == "battery":
        battery = psutil.sensors_battery()
        return {"Battery": f"{battery.percent}%"}
    else:
        return {"error": "Fitur tidak ditemukan"}
    
@app.get("/action/sleep")
def sleep_mode():
    os.system("systemctl suspend") #sleep atau suspend command di linux omarchy
    return {"status": "Laptop sedang sare..."}

@app.get("/action/shutdown")
def shutdown_laptop():
    os.system("systemctl poweroff") #shutdown command untuk linux omarchy
    return {"message": "Laptop dimatikan..."}

app.mount("/", StaticFiles(directory="static", html=True), name="static")