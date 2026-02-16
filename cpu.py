import time
import psutil
from rich.live import Live
from rich.table import Table
from rich.console import Console

# --- BAGIAN 1: DAPUR (Fungsi Membuat Tampilan) ---
# Kita ubah fungsi ini biar menerima "Bahan Masakan" (Data) dari luar
def generate_dashboard(cpu_pct, ram_pct, ram_used_gb, ram_total_gb, net_speed_kb):
    
    # 1. Bikin Tabel Kosong
    table = Table(title="🔥 Sentinel System Monitor (Level 2)")
    
    # 2. Tambah Kolom (Header)
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    # 3. Logika Warna (Visual Logic)
    # Kalau CPU > 50% jadi Merah, kalau aman jadi Hijau
    cpu_color = "[red]" if cpu_pct > 50 else "[green]"
    
    # Kalau Internet ngebut (> 1000 KB/s), warnanya kuning
    net_color = "[yellow]" if net_speed_kb > 1000 else "[blue]"

    # 4. Masukkan Data ke Baris
    table.add_row("CPU Core", f"{cpu_color}{cpu_pct}%")
    table.add_row("RAM Usage", f"{ram_pct}% ({ram_used_gb} GB / {ram_total_gb} GB)")
    table.add_row("Net Speed", f"{net_color}⬇ {net_speed_kb:.2f} KB/s")
    
    return table

# --- BAGIAN 2: MESIN UTAMA (Execution) ---
if __name__ == "__main__":
    console = Console()
    console.print("[yellow]Menghitung kecepatan awal...[/yellow]")
    
    # [LOGIKA MATEMATIKA 1] Ambil data internet PERTAMA kali (Titik A)
    last_received = psutil.net_io_counters().bytes_recv
    
    # Masuk ke mode Live Dashboard
    # Kita panggil generate_dashboard dengan angka 0 dulu untuk tampilan awal
    with Live(generate_dashboard(0, 0, 0, 0, 0), refresh_per_second=1) as live:
        
        while True:
            # Tunggu 1 detik (Wajib ada biar bisa hitung selisih waktu)
            time.sleep(1)
            
            # --- MULAI MENGHITUNG DATA (LOGIC) ---
            
            # 1. Ambil Data CPU & RAM
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            
            # Format RAM biar jadi GB (Gigabytes) dan ambil 1 angka belakang koma
            ram_used = round(ram.used / (1024**3), 1)
            ram_total = round(ram.total / (1024**3), 1)
            
            # 2. Hitung Kecepatan Internet (Delta Logic)
            # Ambil data internet SEKARANG (Titik B)
            current_received = psutil.net_io_counters().bytes_recv
            
            # Rumus: Kecepatan = (Titik B - Titik A)
            speed_bytes = current_received - last_received
            
            # Konversi Bytes ke Kilobytes (KB) biar enak dibaca
            speed_kb = speed_bytes / 1024
            
            # [PENTING] Update Titik A jadi Titik B untuk detik berikutnya
            last_received = current_received
            
            # --- UPDATE TAMPILAN ---
            # Kirim semua data matang tadi ke fungsi generate_dashboard
            table_baru = generate_dashboard(cpu, ram.percent, ram_used, ram_total, speed_kb)
            live.update(table_baru)