import os
import sys
from colorama import Fore, Style, init

# Core modülünü içe aktarma
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.unexcore import (
    load_config,
    init_db,
    get_db_connection,
    banner,
    is_tool_installed,
    install_tool,
    remove_tool,
    update_all_tools,
    get_installed_stats,
    backtomenu
)

init(autoreset=True)

def clear_screen():
    """Ekranı temizler."""
    os.system('clear' if os.name != 'nt' else 'cls')

def show_main_menu(config):
    """Ana kategorileri listeler."""
    clear_screen()
    banner()
    
    db_file = config.get('Paths', 'db_file', fallback='unex.db')
    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM categories ORDER BY id ASC")
    categories = cursor.fetchall()
    conn.close()
    
    print(f"{Fore.WHITE}{Style.BRIGHT}=== KATEGORİLER ==={Style.RESET_ALL}\n")
    for cat in categories:
        print(f"[{cat['id']:02d}] {cat['name']}")
        
    print(f"\n[77] Araç Kaldır (Uninstall)")
    print(f"[88] Yüklü Araç İstatistiklerini Göster")
    print(f"[99] Yüklü Tüm Araçları Güncelle")
    print(f"[00] Çıkış\n")

def show_stats_menu(config):
    """Yüklü araçların versiyon ve güncelleme istatistiklerini gösterir."""
    clear_screen()
    banner()
    print(f"{Fore.WHITE}{Style.BRIGHT}=== YÜKLÜ ARAÇ İSTATİSTİKLERİ ==={Style.RESET_ALL}\n")
    
    stats = get_installed_stats(config)
    if not stats:
        print(f"{Fore.YELLOW}[i] Henüz kurulmuş bir araç bulunmamaktadır.{Style.RESET_ALL}")
    else:
        for tool in stats:
            name = tool['name']
            ver = tool['version'] or '1.0.0'
            inst_at = tool['installed_at'] or 'Bilinmiyor'
            upd_at = tool['updated_at'] or inst_at
            print(f"{Fore.GREEN}[✓] {name}{Style.RESET_ALL} (v{ver})")
            print(f"    └─ Kurulum: {inst_at} | Son Güncelleme: {upd_at}")
            
    backtomenu()

def show_remove_menu(config):
    """Yüklü araçları listeler ve kaldırılması isteneni seçtirir."""
    clear_screen()
    banner()
    print(f"{Fore.WHITE}{Style.BRIGHT}=== ARAÇ KALDIR ==={Style.RESET_ALL}\n")
    
    stats = get_installed_stats(config)
    if not stats:
        print(f"{Fore.YELLOW}[i] Kaldırılabilecek yüklü araç bulunamadı.{Style.RESET_ALL}")
        backtomenu()
        return
        
    for index, tool in enumerate(stats, start=1):
        print(f"[{index:02d}] {tool['name']}")
        
    print(f"\n[00] İptal / Ana Menüye Dön\n")
    choice = input(f"{Fore.CYAN}unex (kaldır) > {Style.RESET_ALL}").strip()
    
    if choice == "0" or choice == "00":
        return
        
    selected_indices = choice.split()
    for idx_str in selected_indices:
        if idx_str.isdigit():
            idx = int(idx_str)
            if 1 <= idx <= len(stats):
                selected_tool = stats[idx - 1]
                remove_tool(selected_tool['id'], config)
            else:
                print(f"{Fore.RED}[!] Geçersiz araç numarası: {idx_str}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[!] Girdi anlaşılamadı: {idx_str}{Style.RESET_ALL}")
            
    backtomenu()

def show_category_menu(category_id, config):
    """Seçilen kategoriye ait araçları listeler."""
    clear_screen()
    banner()
    
    db_file = config.get('Paths', 'db_file', fallback='unex.db')
    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
    cat_row = cursor.fetchone()
    if not cat_row:
        print(f"{Fore.RED}[!] Geçersiz kategori ID!{Style.RESET_ALL}")
        conn.close()
        return []
        
    category_name = cat_row['name']
    print(f"{Fore.WHITE}{Style.BRIGHT}=== {category_name.upper()} ==={Style.RESET_ALL}\n")
    
    cursor.execute("SELECT * FROM tools WHERE category_id = ? ORDER BY id ASC", (category_id,))
    tools = cursor.fetchall()
    conn.close()
    
    if not tools:
        print(f"{Fore.YELLOW}[i] Bu kategoride henüz araç bulunmuyor.{Style.RESET_ALL}")
        return []
        
    for index, tool in enumerate(tools, start=1):
        installed = is_tool_installed(tool['name'], config)
        status = f"{Fore.GREEN}[✓]{Style.RESET_ALL}" if installed else f"{Fore.RED}[ ]{Style.RESET_ALL}"
        ver_str = f" (v{tool['version']})" if tool['version'] else ""
        print(f"[{index:02d}] {status} {tool['name']}{ver_str} - {tool['description']}")
        
    print(f"\n[@] Tümünü Yükle")
    print(f"[00] Ana Menüye Dön\n")
    
    return tools

def main():
    """Ana uygulama döngüsü."""
    config = load_config()
    db_file = config.get('Paths', 'db_file', fallback='unex.db')
    
    # Veritabanını başlat
    init_db(db_file)
    
    # Açılışta otomatik güncelleme kontrolü
    update_all_tools(config)
    
    while True:
        show_main_menu(config)
        choice = input(f"{Fore.CYAN}unex > {Style.RESET_ALL}").strip()
        
        if choice == "0" or choice == "00":
            print(f"\n{Fore.GREEN}[+] unex'i kullandığınız için teşekkürler! Görüşmek üzere.{Style.RESET_ALL}")
            break
            
        if choice == "77":
            show_remove_menu(config)
            continue

        if choice == "88":
            show_stats_menu(config)
            continue

        if choice == "99":
            update_all_tools(config)
            backtomenu()
            continue
            
        if not choice.isdigit():
            print(f"{Fore.RED}[!] Lütfen geçerli bir sayı girin.{Style.RESET_ALL}")
            backtomenu()
            continue
            
        category_id = int(choice)
        
        while True:
            tools = show_category_menu(category_id, config)
            if not tools:
                backtomenu()
                break
                
            tool_choice = input(f"{Fore.CYAN}unex ({category_id}) > {Style.RESET_ALL}").strip()
            
            if tool_choice == "0" or tool_choice == "00":
                break
                
            if tool_choice == "@":
                for tool in tools:
                    install_tool(tool['id'], config)
                backtomenu()
                break
                
            selected_indices = tool_choice.split()
            valid_selection = False
            
            for idx_str in selected_indices:
                if idx_str.isdigit():
                    idx = int(idx_str)
                    if 1 <= idx <= len(tools):
                        selected_tool = tools[idx - 1]
                        install_tool(selected_tool['id'], config)
                        valid_selection = True
                    else:
                        print(f"{Fore.RED}[!] Geçersiz araç numarası: {idx_str}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[!] Girdi anlaşılamadı: {idx_str}{Style.RESET_ALL}")
                    
            if valid_selection:
                backtomenu()
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[!] İşlem kullanıcı tarafından iptal edildi. Çıkılıyor...{Style.RESET_ALL}")
        sys.exit(0)
