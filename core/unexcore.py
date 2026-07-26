import os
import sys
import sqlite3
import configparser
import subprocess
import shutil
from colorama import Fore, Style, init

init(autoreset=True)

DEFAULT_CONFIG_PATH = "unex.conf"

def load_config(config_file=DEFAULT_CONFIG_PATH):
    """Yapılandırma dosyasını (unex.conf) yükler."""
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
    else:
        config['Paths'] = {
            'prefix': os.path.expanduser('~/unex'),
            'tools_dir': 'tools',
            'db_file': 'unex.db'
        }
        config['Options'] = {
            'batch_mode': 'false'
        }
    return config

def get_db_connection(db_file="unex.db"):
    """Veritabanı bağlantısı oluşturur."""
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_file="unex.db"):
    """Veritabanı tablolarını oluşturur ve varsayılan verileri ekler."""
    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY,
        category_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        url TEXT,
        installed BOOLEAN DEFAULT 0,
        version TEXT,
        installed_at DATETIME,
        updated_at DATETIME,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    );
    """)
    
    conn.commit()
    prepopulate_db(conn)
    conn.close()

def prepopulate_db(conn):
    """Kategorileri ve araçları varsayılan olarak veritabanına ekler."""
    cursor = conn.cursor()
    
    categories = [
        "Bilgi Toplama",
        "Zafiyet Analizi",
        "Web Sızma Testleri",
        "Veritabanı Değerlendirme",
        "Parola Saldırıları",
        "Kablosuz Ağ Saldırıları",
        "Tersine Mühendislik",
        "Istismar Araçları",
        "Ağ Dinleme ve Yanıltma",
        "Raporlama Araçları",
        "Adli Bilişim Araçları",
        "Stres Testleri",
        "Linux Dağıtımı Kurulumu",
        "Termux Araçları",
        "Özel Araçlar"
    ]
    
    for cat in categories:
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))
    
    conn.commit()
    
    cat_map = {}
    for row in cursor.execute("SELECT id, name FROM categories"):
        cat_map[row['name']] = row['id']
        
    tools_list = [
        ("nmap", "Ağ keşfi ve zafiyet tarama aracı", "https://github.com/nmap/nmap", "Bilgi Toplama"),
        ("sqlmap", "Otomatik SQL enjeksiyonu ve veritabanı ele geçirme aracı", "https://github.com/sqlmapproject/sqlmap", "Bilgi Toplama"),
        ("redhawk", "Hepsi bir arada bilgi toplama ve zafiyet tarayıcı", "https://github.com/Tuhinshubhra/RED_HAWK", "Bilgi Toplama"),
        ("recon-ng", "Python ile yazılmış gelişmiş web bilgi toplama çerçevesi", "https://github.com/lanmaster53/recon-ng", "Bilgi Toplama"),
        ("theharvester", "E-posta, alt alan adı ve kullanıcı adı toplama aracı", "https://github.com/laramies/theHarvester", "Bilgi Toplama"),
        ("sherlock", "Sosyal medya platformlarında kullanıcı adı arama aracı", "https://github.com/sherlock-project/sherlock", "Bilgi Toplama"),
        ("phoneinfoga", "Telefon numaraları için gelişmiş bilgi toplama aracı", "https://github.com/sundowndev/phoneinfoga", "Bilgi Toplama"),
        ("maigret", "Sadece kullanıcı adı üzerinden detaylı profil toplama aracı", "https://github.com/soxoj/maigret", "Bilgi Toplama"),
        ("sublist3r", "Hızlı alt alan adı tespit etme aracı", "https://github.com/aboul3la/Sublist3r", "Bilgi Toplama"),
        ("dnsrecon", "DNS tespit ve analiz betiği", "https://github.com/darkoperator/dnsrecon", "Bilgi Toplama"),
        
        ("xsstrike", "Gelişmiş XSS tespit ve analiz paketi", "https://github.com/s0md3v/XSStrike", "Web Sızma Testleri"),
        ("wpscan", "WordPress güvenlik tarayıcısı", "https://github.com/wpscantech/wpscan", "Web Sızma Testleri"),
        ("cmseek", "CMS tespit ve istismar paketi", "https://github.com/Tuhinshubhra/CMSeeK", "Web Sızma Testleri"),
        ("nikto", "Web sunucusu güvenlik tarayıcısı", "https://github.com/sullo/nikto", "Web Sızma Testleri"),
        ("gobuster", "Go ile yazılmış dizin, dosya ve DNS kaba kuvvet aracı", "https://github.com/OJ/gobuster", "Web Sızma Testleri"),
        ("commix", "Otomatik komut enjeksiyonu ve istismar aracı", "https://github.com/commixproject/commix", "Web Sızma Testleri"),
        
        ("hydra", "Çoklu protokol destekli ağ parola kırıcı", "https://github.com/vanhauser-thc/thc-hydra", "Parola Saldırıları"),
        ("john", "John the Ripper parola kırma aracı", "https://github.com/openwall/john", "Parola Saldırıları"),
        ("hashcat", "Dünyanın en hızlı hash parola kırıcı aracı", "https://github.com/hashcat/hashcat", "Parola Saldırıları"),
        ("crunch", "Kelime listesi (wordlist) oluşturucu", "https://github.com/crunchsec/crunch", "Parola Saldırıları"),
        ("cupp", "Kullanıcıya özel parola profili oluşturucu", "https://github.com/Mebus/cupp", "Parola Saldırıları"),
        
        ("metasploit-framework", "Gelişmiş sızma testi çerçevesi", "https://github.com/rapid7/metasploit-framework", "Istismar Araçları"),
        ("routersploit", "Gömülü cihazlar için istismar çerçevesi", "https://github.com/threat9/routersploit", "Istismar Araçları"),
        
        ("aircrack-ng", "Kablosuz ağ güvenlik denetim araç seti", "https://github.com/aircrack-ng/aircrack-ng", "Kablosuz Ağ Saldırıları"),
        ("wifite", "Otomatik kablosuz ağ saldırı aracı", "https://github.com/derv82/wifite2", "Kablosuz Ağ Saldırıları"),
        
        ("zsh", "Termux için Z kabuğu", "", "Termux Araçları"),
        ("git", "Dağıtık sürüm kontrol sistemi", "", "Termux Araçları"),
        ("wget", "HTTP/HTTPS/FTP dosya indirme aracı", "", "Termux Araçları"),
        ("curl", "URL ile veri transferi aracı", "", "Termux Araçları")
    ]
    
    for name, desc, url, cat_name in tools_list:
        cat_id = cat_map.get(cat_name)
        if cat_id:
            cursor.execute("""
            INSERT OR IGNORE INTO tools (category_id, name, description, url, version)
            VALUES (?, ?, ?, ?, '1.0.0')
            """, (cat_id, name, desc, url))
            
    conn.commit()

def banner():
    """ASCII başlığı gösterir."""
    art = r"""
  _   _ _  _ _____  __
 | | | | \| | ____|\ \/ /
 | | | |  ` |  _|   \  / 
 | |_| | |\  | |___  /  \ 
  \___/|_| \_|_____/_/\_\  v1.0
  [ United Exploit Toolkit for Termux ]
    """
    print(f"{Fore.CYAN}{Style.BRIGHT}{art}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Team Unex Tarafından Geliştirildi{Style.RESET_ALL}\n")

def is_tool_installed(tool_name, config):
    """Bir aracın yüklü olup olmadığını kontrol eder."""
    tools_dir = config.get('Paths', 'tools_dir', fallback='tools')
    tool_path = os.path.join(tools_dir, tool_name)
    
    if os.path.exists(tool_path):
        return True
        
    result = subprocess.run(["which", tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        return True
        
    return False

def update_all_tools(config):
    """Yüklü git depolarını ve paketleri günceller."""
    print(f"\n{Fore.YELLOW}[*] Yüklü araçlar güncelleniyor...{Style.RESET_ALL}")
    tools_dir = config.get('Paths', 'tools_dir', fallback='tools')
    db_file = config.get('Paths', 'db_file', fallback='unex.db')
    
    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    
    if os.path.exists(tools_dir):
        for tool_folder in os.listdir(tools_dir):
            tool_path = os.path.join(tools_dir, tool_folder)
            if os.path.isdir(tool_path) and os.path.exists(os.path.join(tool_path, ".git")):
                print(f"{Fore.CYAN}[->] Güncelleniyor: {tool_folder}...{Style.RESET_ALL}")
                try:
                    subprocess.run(["git", "-C", tool_path, "pull"], check=False)
                    cursor.execute("UPDATE tools SET updated_at = CURRENT_TIMESTAMP WHERE name = ?", (tool_folder,))
                except Exception as e:
                    print(f"{Fore.RED}[!] {tool_folder} güncellenemedi: {e}{Style.RESET_ALL}")

    conn.commit()
    conn.close()
    print(f"{Fore.GREEN}[✓] Otomatik güncelleme tamamlandı.{Style.RESET_ALL}\n")

def install_tool(tool_id, config):
    """Verilen tool_id'ye sahip aracı kurar."""
    db_file = config.get('Paths', 'db_file', fallback='unex.db')
    tools_dir = config.get('Paths', 'tools_dir', fallback='tools')
    
    if not os.path.exists(tools_dir):
        os.makedirs(tools_dir)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tools WHERE id = ?", (tool_id,))
    tool = cursor.fetchone()

    if not tool:
        print(f"{Fore.RED}[!] Araç bulunamadı (ID: {tool_id}){Style.RESET_ALL}")
        conn.close()
        return

    name = tool['name']
    url = tool['url']

    print(f"\n{Fore.YELLOW}[*] Yükleniyor: {name}...{Style.RESET_ALL}")

    pkg_tools = ["nmap", "hydra", "john", "hashcat", "crunch", "aircrack-ng", "zsh", "git", "wget", "curl", "metasploit-framework"]
    
    try:
        if name in pkg_tools:
            subprocess.run(["pkg", "install", "-y", name], check=True)
        elif url and url.startswith("http"):
            target_path = os.path.join(tools_dir, name)
            if not os.path.exists(target_path):
                subprocess.run(["git", "clone", url, target_path], check=True)
                req_path = os.path.join(target_path, "requirements.txt")
                if os.path.exists(req_path):
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_path], check=True)
            else:
                print(f"{Fore.BLUE}[I] {name} zaten klonlanmış.{Style.RESET_ALL}")

        cursor.execute("UPDATE tools SET installed = 1, installed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (tool_id,))
        conn.commit()
        print(f"{Fore.GREEN}[✓] {name} başarıyla yüklendi!{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}[!] {name} yüklenirken hata oluştu: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def remove_tool(tool_id, config):
    """Verilen tool_id'ye sahip aracı sistemden/dizinden kaldırır ve veritabanını günceller."""
    db_file = config.get('Paths', 'db_file', fallback='unex.db')
    tools_dir = config.get('Paths', 'tools_dir', fallback='tools')

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tools WHERE id = ?", (tool_id,))
    tool = cursor.fetchone()

    if not tool:
        print(f"{Fore.RED}[!] Araç bulunamadı (ID: {tool_id}){Style.RESET_ALL}")
        conn.close()
        return

    name = tool['name']
    target_path = os.path.join(tools_dir, name)
    pkg_tools = ["nmap", "hydra", "john", "hashcat", "crunch", "aircrack-ng", "zsh", "git", "wget", "curl", "metasploit-framework"]

    print(f"\n{Fore.YELLOW}[*] Kaldırılıyor: {name}...{Style.RESET_ALL}")

    try:
        if name in pkg_tools:
            subprocess.run(["pkg", "uninstall", "-y", name], check=False)
        
        if os.path.exists(target_path):
            shutil.rmtree(target_path)

        cursor.execute("UPDATE tools SET installed = 0, installed_at = NULL, updated_at = NULL WHERE id = ?", (tool_id,))
        conn.commit()
        print(f"{Fore.GREEN}[✓] {name} başarıyla kaldırıldı.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] {name} kaldırılırken hata oluştu: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def get_installed_stats(config):
    """Yüklü araçlar ve son güncelleme istatistiklerini getirir."""
    db_file = config.get('Paths', 'db_file', fallback='unex.db')
    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, version, installed_at, updated_at FROM tools WHERE installed = 1")
    rows = cursor.fetchall()
    conn.close()
    return rows

def backtomenu():
    """Kullanıcıdan girdi bekleyerek menüye dönmeyi sağlar."""
    input(f"\n{Fore.CYAN}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
