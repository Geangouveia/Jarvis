import os
import sys
import time
import ctypes
import datetime
import subprocess
import webbrowser
import psutil
from PIL import ImageGrab

# Windows Virtual-Key Codes
VK_LWIN = 0x5B
VK_MENU = 0x12       # Alt
VK_CONTROL = 0x11    # Ctrl
VK_SHIFT = 0x10      # Shift
VK_TAB = 0x09
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_PRIOR = 0x21      # Page Up
VK_NEXT = 0x22       # Page Down
VK_UP = 0x26
VK_DOWN = 0x28
VK_F4 = 0x73
VK_F5 = 0x74
VK_F11 = 0x7A
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3

KEYEVENTF_KEYUP = 0x0002

def _key_press(vk):
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.04)
    ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)

def _hotkey(*vks):
    for vk in vks:
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    for vk in reversed(vks):
        ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)

def _find_browser_exe():
    """Localiza o executável do Google Chrome ou Edge na máquina do usuário."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

class SystemController:
    """Controlador mestre do Windows: automação completa sem mouse e sem teclado."""

    # ==========================
    # NAVEGAÇÃO WEB & YOUTUBE
    # ==========================
    @staticmethod
    def open_url(url):
        """Abre a URL diretamente na instância ativa do navegador sem conflito de perfil."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        # Método 1: explorer.exe passa a URL diretamente para a janela ativa do Chrome
        try:
            subprocess.Popen(["explorer.exe", url])
            return f"Abrindo {url}, senhor."
        except Exception:
            pass

        # Método 2: os.startfile
        try:
            os.startfile(url)
            return f"Abrindo {url}, senhor."
        except Exception:
            pass

        # Método 3: comando cmd start
        try:
            subprocess.Popen(f'start "" "{url}"', shell=True)
            return f"Abrindo {url}, senhor."
        except Exception:
            webbrowser.open(url)
            return f"Abrindo {url}, senhor."

    @staticmethod
    def play_youtube(query):
        """Pesquisa e toca vídeo/música no YouTube diretamente."""
        import urllib.parse
        clean_query = urllib.parse.quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={clean_query}"
        SystemController.open_url(url)
        return url

    @staticmethod
    def play_spotify(query):
        """Abre o Spotify pesquisando o artista ou música desejado."""
        import urllib.parse
        encoded = urllib.parse.quote(query)
        try:
            os.system(f"start spotify:search:{encoded}")
        except Exception:
            pass
        url = f"https://open.spotify.com/search/{encoded}"
        SystemController.open_url(url)
        return url

    @staticmethod
    def search_web(query):
        """Pesquisa termos no Google."""
        import urllib.parse
        clean_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={clean_query}"
        SystemController.open_url(url)
        return url

    # ==========================
    # APLICATIVOS E PASTAS
    # ==========================
    @staticmethod
    def open_app(app_name):
        name = app_name.lower().strip()

        # Mapeamento de sites e serviços web
        web_map = {
            "youtube": "https://www.youtube.com",
            "yt": "https://www.youtube.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "github": "https://www.github.com",
            "chatgpt": "https://chatgpt.com",
            "netflix": "https://www.netflix.com",
            "twitch": "https://www.twitch.tv",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.x.com",
            "x": "https://www.x.com",
            "whatsapp web": "https://web.whatsapp.com",
            "spotify web": "https://open.spotify.com"
        }

        for k, url in web_map.items():
            if k == name or k in name:
                return SystemController.open_url(url)

        # Mapeamento de pastas do Windows
        user_home = os.path.expanduser("~")
        folder_map = {
            "downloads": os.path.join(user_home, "Downloads"),
            "documentos": os.path.join(user_home, "Documents"),
            "documents": os.path.join(user_home, "Documents"),
            "imagens": os.path.join(user_home, "Pictures"),
            "fotos": os.path.join(user_home, "Pictures"),
            "área de trabalho": os.path.join(user_home, "Desktop"),
            "area de trabalho": os.path.join(user_home, "Desktop"),
            "desktop": os.path.join(user_home, "Desktop"),
            "disco c": "C:\\",
            "meu computador": "explorer.exe",
        }

        for k, path in folder_map.items():
            if k == name or k in name:
                try:
                    os.startfile(path)
                    return f"Abrindo pasta {k}, senhor."
                except Exception as e:
                    return f"Falha ao abrir pasta: {e}"

        # Mapeamento de Programas Locais
        app_map = {
            "calc": "calc.exe",
            "calculadora": "calc.exe",
            "bloco de notas": "notepad.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe",
            "gerenciador de tarefas": "taskmgr.exe",
            "task manager": "taskmgr.exe",
            "painel de controle": "control.exe",
            "explorador": "explorer.exe",
            "cmd": "cmd.exe",
            "prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "configurações": "ms-settings:",
            "settings": "ms-settings:",
            "chrome": _find_browser_exe() or "chrome",
            "google chrome": _find_browser_exe() or "chrome",
            "navegador": _find_browser_exe() or "chrome",
            "edge": "msedge.exe",
            "spotify": "spotify:",
            "discord": "discord",
            "vscode": "code",
            "visual studio code": "code",
            "steam": "steam://open/main",
            "whatsapp": "whatsapp:"
        }

        target = app_map.get(name)
        if not target:
            for k, val in app_map.items():
                if k in name:
                    target = val
                    break

        if not target:
            target = name

        try:
            if target.startswith("ms-") or target.startswith("steam:") or target.startswith("whatsapp:") or target.startswith("spotify:"):
                os.system(f"start {target}")
            else:
                subprocess.Popen(target, shell=True)
            return f"Iniciando {app_name}, senhor."
        except Exception as e:
            return f"Não consegui iniciar {app_name}: {e}"

    # ==========================
    # CONTROLE DE JANELAS E NAVEGADOR
    # ==========================
    @staticmethod
    def close_window():
        """Fecha a janela ativa atual (Alt + F4)."""
        _hotkey(VK_MENU, VK_F4)
        return "Janela encerrada, senhor."

    @staticmethod
    def switch_window():
        """Alterna entre as janelas abertas (Alt + Tab)."""
        _hotkey(VK_MENU, VK_TAB)
        return "Alternando janela ativa."

    @staticmethod
    def maximize_window():
        """Maximiza a janela ativa (Win + Seta Cima)."""
        _hotkey(VK_LWIN, VK_UP)
        return "Janela maximizada."

    @staticmethod
    def minimize_window():
        """Minimiza a janela ativa (Win + Seta Baixo)."""
        _hotkey(VK_LWIN, VK_DOWN)
        return "Janela minimizada."

    @staticmethod
    def minimize_all_windows():
        """Minimiza tudo e exibe a Área de Trabalho (Win + D)."""
        _hotkey(VK_LWIN, 0x44) # Win + D
        return "Exibindo a área de trabalho, senhor."

    @staticmethod
    def toggle_fullscreen():
        """Coloca ou tira de tela cheia (F11)."""
        _key_press(VK_F11)
        return "Modo de tela cheia alternado."

    @staticmethod
    def new_tab():
        """Abre uma nova guia no navegador (Ctrl + T)."""
        _hotkey(VK_CONTROL, 0x54) # Ctrl + T
        return "Nova guia aberta."

    @staticmethod
    def close_tab():
        """Fecha a guia atual do navegador (Ctrl + W)."""
        _hotkey(VK_CONTROL, 0x57) # Ctrl + W
        return "Guia atual fechada."

    @staticmethod
    def refresh_page():
        """Atualiza a página atual (F5)."""
        _key_press(VK_F5)
        return "Página atualizada."

    @staticmethod
    def scroll_down():
        """Rola a página para baixo."""
        for _ in range(2):
            _key_press(VK_NEXT) # Page Down
            time.sleep(0.05)
        return "Rolando para baixo."

    @staticmethod
    def scroll_up():
        """Rola a página para cima."""
        for _ in range(2):
            _key_press(VK_PRIOR) # Page Up
            time.sleep(0.05)
        return "Rolando para cima."

    # ==========================
    # ÁUDIO E MÍDIA
    # ==========================
    @staticmethod
    def volume_up(steps=5):
        for _ in range(steps):
            _key_press(VK_VOLUME_UP)
            time.sleep(0.02)
        return f"Volume aumentado, senhor."

    @staticmethod
    def volume_down(steps=5):
        for _ in range(steps):
            _key_press(VK_VOLUME_DOWN)
            time.sleep(0.02)
        return f"Volume reduzido, senhor."

    @staticmethod
    def toggle_mute():
        _key_press(VK_VOLUME_MUTE)
        return "Áudio alternado (Mudo / Ativo)."

    @staticmethod
    def media_play_pause():
        _key_press(VK_MEDIA_PLAY_PAUSE)
        return "Mídia alternada (Play / Pause)."

    @staticmethod
    def media_next():
        _key_press(VK_MEDIA_NEXT_TRACK)
        return "Próxima faixa reproduzida."

    @staticmethod
    def media_prev():
        _key_press(VK_MEDIA_PREV_TRACK)
        return "Faixa anterior reproduzida."

    # ==========================
    # SISTEMA E SEGURANÇA
    # ==========================
    @staticmethod
    def lock_pc():
        ctypes.windll.user32.LockWorkStation()
        return "Estação de trabalho bloqueada, senhor."

    @staticmethod
    def empty_recycle_bin():
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            return "Lixeira esvaziada com êxito, senhor."
        except Exception as e:
            return f"Não foi possível esvaziar a lixeira: {e}"

    @staticmethod
    def take_screenshot():
        screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "screenshots"))
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jarvis_screen_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)

        try:
            import mss
            with mss.mss() as sct:
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=filepath)
                return {
                    "success": True,
                    "message": f"Captura de tela salva como {filename}",
                    "filename": filename,
                    "filepath": filepath
                }
        except Exception:
            try:
                screenshot = ImageGrab.grab()
                screenshot.save(filepath, "PNG")
                return {
                    "success": True,
                    "message": f"Captura de tela salva como {filename}",
                    "filename": filename,
                    "filepath": filepath
                }
            except Exception as e:
                return {"success": False, "message": f"Falha ao capturar tela: {e}"}

    @staticmethod
    def get_system_telemetry():
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_freq_current = round(cpu_freq.current / 1000, 2) if cpu_freq else None

        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')

        battery = psutil.sensors_battery()
        battery_data = None
        if battery:
            battery_data = {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "secs_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else -1
            }

        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime_delta = datetime.datetime.now() - boot_time
        hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
        mins, secs = divmod(remainder, 60)
        uptime_str = f"{hours}h {mins}m"

        return {
            "cpu": {
                "percent": cpu_percent,
                "cores": cpu_count,
                "freq_ghz": cpu_freq_current
            },
            "ram": {
                "percent": ram.percent,
                "used_gb": round(ram.used / (1024 ** 3), 1),
                "total_gb": round(ram.total / (1024 ** 3), 1)
            },
            "disk": {
                "percent": disk.percent,
                "free_gb": round(disk.free / (1024 ** 3), 1),
                "total_gb": round(disk.total / (1024 ** 3), 1)
            },
            "battery": battery_data,
            "uptime": uptime_str,
            "platform": sys.platform
        }
