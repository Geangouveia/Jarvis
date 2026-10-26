import os
import re
import json
import datetime
from core.system_controller import SystemController
from core.notes_manager import NotesManager

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "config.json"))

class JarvisBrain:
    def __init__(self):
        self.config = self._load_config()
        self.gemini_client = None
        self._init_gemini()

    def _load_config(self):
        default = {
            "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
            "voice": "pt-BR-AntonioNeural",
            "user_name": "junior",
            "wake_word": "jarvis"
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default.update(data)
            except Exception:
                pass
        return default

    def save_config(self, new_config: dict):
        self.config.update(new_config)
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
        self._init_gemini()
        return self.config

    def _init_gemini(self):
        api_key = self.config.get("gemini_api_key", "").strip()
        if not api_key:
            self.gemini_client = None
            return

        try:
            from google import genai
            self.gemini_client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"Erro ao inicializar Gemini: {e}")
            self.gemini_client = None

    async def process_command(self, raw_text: str) -> dict:
        """Processa comando de voz e executa ações diretas no Windows com latência zero."""
        text = raw_text.strip()
        if not text:
            return {"speech": "Às suas ordens.", "action": "none"}

        clean = text.lower()
        # Remove gatilhos de saudação ou wake words
        clean = re.sub(r'^(ei\s+|olá\s+|ola\s+|ok\s+|por favor\s+|jarvis\s*,?\s*)+', '', clean).strip()
        clean = re.sub(r'[?!.,;]+$', '', clean).strip()

        # 1. Verificação Instantânea de Comandos Nativos de PC
        direct_result = self._match_direct_command(clean, text)
        if direct_result:
            return direct_result

        # 2. Se não casou com regex simples, o Gemini interpreta a intenção e dispara a ação
        if self.gemini_client:
            return await self._process_with_gemini(text)

        # 3. Fallback inteligente
        return self._fallback_chat_response(clean)

    def _match_direct_command(self, clean: str, original: str):
        user = self.config.get("user_name", "senhor")

        # ==========================================
        # 1. YOUTUBE COM MÚSICA / ARTISTA ESPECÍFICO (PRIORITÁRIO)
        # Ex: "abra o youtube na música de Thalles Roberto", "toque Thalles Roberto no youtube"
        # ==========================================
        m_yt_spec = re.search(r'(?:abrir|abra|iniciar|inicie|coloque|coloca|toque|tocar|bota|botar|ouvir|pesquise|pesquisar)\s+(?:o\s+)?youtube\s+(?:na\s+música\s+de\s+|na\s+musica\s+de\s+|na\s+música\s+|na\s+musica\s+|no\s+vídeo\s+de\s+|no\s+video\s+de\s+|com\s+a\s+música\s+|com\s+a\s+musica\s+|com\s+|e\s+coloque\s+|e\s+toque\s+|pesquisando\s+por\s+|pesquisando\s+|de\s+)?(.+)', clean)
        if m_yt_spec:
            q = m_yt_spec.group(1).strip()
            if q and q not in ['o youtube', 'youtube', 'yt']:
                res = SystemController.play_youtube(q)
                return {
                    "speech": f"Abrindo a música de {q} no YouTube, {user}.",
                    "action": "youtube",
                    "details": f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}"
                }

        m_yt_end = re.search(r'(?:toque|tocar|ouvir|coloque|coloca|bota|botar|pesquise|buscar)\s+(?:a\s+música\s+|o\s+vídeo\s+)?(.+?)\s+no\s+youtube', clean)
        if m_yt_end:
            q = m_yt_end.group(1).strip()
            if q:
                res = SystemController.play_youtube(q)
                return {
                    "speech": f"Reproduzindo {q} no YouTube, {user}.",
                    "action": "youtube",
                    "details": f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}"
                }

        # ==========================================
        # 2. SPOTIFY COM MÚSICA / ARTISTA ESPECÍFICO (PRIORITÁRIO)
        # Ex: "abra o spotify na música de Thalles Roberto", "toque Thalles Roberto no spotify"
        # ==========================================
        m_sp_spec = re.search(r'(?:abrir|abra|iniciar|inicie|coloque|coloca|toque|tocar|bota|botar|ouvir|pesquise|pesquisar)\s+(?:o\s+)?spotify\s+(?:na\s+música\s+de\s+|na\s+musica\s+de\s+|na\s+música\s+|na\s+musica\s+|com\s+a\s+música\s+|com\s+a\s+musica\s+|com\s+|e\s+coloque\s+|e\s+toque\s+|pesquisando\s+por\s+|pesquisando\s+|de\s+)?(.+)', clean)
        if m_sp_spec:
            q = m_sp_spec.group(1).strip()
            if q and q not in ['o spotify', 'spotify']:
                res = SystemController.play_spotify(q)
                return {
                    "speech": f"Buscando {q} no Spotify, {user}.",
                    "action": "spotify",
                    "details": f"https://open.spotify.com/search/{q.replace(' ', '%20')}"
                }

        m_sp_end = re.search(r'(?:toque|tocar|ouvir|coloque|coloca|bota|botar|pesquise|buscar)\s+(?:a\s+música\s+|o\s+álbum\s+|o\s+album\s+)?(.+?)\s+no\s+spotify', clean)
        if m_sp_end:
            q = m_sp_end.group(1).strip()
            if q:
                res = SystemController.play_spotify(q)
                return {
                    "speech": f"Reproduzindo {q} no Spotify, {user}.",
                    "action": "spotify",
                    "details": f"https://open.spotify.com/search/{q.replace(' ', '%20')}"
                }

        # ==========================================
        # 3. YOUTUBE E SITES PRINCIPAIS (APENAS ABRIR PÁGINA INICIAL)
        # ==========================================
        if any(p in clean for p in ["abrir youtube", "abrir o youtube", "abre o youtube", "abra o youtube", "abra youtube", "abrir o yt", "abre o yt", "acessar youtube", "ver youtube", "youtube"]):
            res = SystemController.open_url("https://www.youtube.com")
            return {"speech": f"Abrindo o YouTube no seu navegador, {user}.", "action": "open_url", "details": "https://www.youtube.com"}

        if any(p in clean for p in ["abrir spotify", "abrir o spotify", "abre o spotify", "abra o spotify", "abra spotify", "spotify"]):
            res = SystemController.open_app("spotify")
            return {"speech": f"Iniciando Spotify, {user}.", "action": "open_app", "details": res}

        if any(p in clean for p in ["abrir google", "abrir o google", "abre o google", "abra o google", "google"]):
            res = SystemController.open_url("https://www.google.com")
            return {"speech": f"Abrindo o Google, {user}.", "action": "open_url", "details": "https://www.google.com"}

        if any(p in clean for p in ["abrir chatgpt", "abrir o chatgpt", "chatgpt"]):
            res = SystemController.open_url("https://chatgpt.com")
            return {"speech": f"Abrindo ChatGPT, {user}.", "action": "open_url", "details": "https://chatgpt.com"}

        if any(p in clean for p in ["abrir netflix", "abrir o netflix", "netflix"]):
            res = SystemController.open_url("https://www.netflix.com")
            return {"speech": f"Abrindo Netflix, {user}.", "action": "open_url", "details": "https://www.netflix.com"}

        if any(p in clean for p in ["abrir whatsapp", "abrir o whatsapp", "whatsapp"]):
            res = SystemController.open_app("whatsapp")
            return {"speech": f"Iniciando WhatsApp, {user}.", "action": "open_app", "details": res}

        # Pesquisa no Google
        search_match = re.search(r'(?:pesquisar|pesquise|buscar|procure|pesquisa por)\s+(?:no google\s+)?(.+)', clean)
        if search_match:
            query = search_match.group(1).replace("no google", "").strip()
            if query:
                res = SystemController.search_web(query)
                return {"speech": f"Pesquisando {query} no Google, {user}.", "action": "search", "details": f"https://www.google.com/search?q={query}"}

        # ==========================================
        # 2. CONTROLE DE JANELAS E NAVEGADOR
        # ==========================================
        if any(p in clean for p in ["fechar janela", "fecha a janela", "fechar programa", "fechar aplicativo", "fecha isso"]):
            res = SystemController.close_window()
            return {"speech": f"Janela fechada, {user}.", "action": "close_window"}

        if any(p in clean for p in ["alternar janela", "trocar janela", "mudar de janela", "troca de janela", "alt tab"]):
            res = SystemController.switch_window()
            return {"speech": f"Alternando janela.", "action": "switch_window"}

        if any(p in clean for p in ["maximizar", "tela cheia", "maximiza", "aumentar janela"]):
            res = SystemController.maximize_window()
            return {"speech": f"Janela maximizada.", "action": "maximize_window"}

        if any(p in clean for p in ["minimizar", "abaixar janela", "descer janela"]):
            res = SystemController.minimize_window()
            return {"speech": f"Janela minimizada.", "action": "minimize_window"}

        if any(p in clean for p in ["mostrar área de trabalho", "mostrar area de trabalho", "minimizar tudo", "área de trabalho"]):
            res = SystemController.minimize_all_windows()
            return {"speech": f"Exibindo área de trabalho, {user}.", "action": "minimize_all"}

        if any(p in clean for p in ["nova guia", "nova aba", "abrir guia", "abrir aba"]):
            res = SystemController.new_tab()
            return {"speech": f"Nova guia aberta.", "action": "new_tab"}

        if any(p in clean for p in ["fechar guia", "fechar aba", "fecha a aba"]):
            res = SystemController.close_tab()
            return {"speech": f"Guia fechada.", "action": "close_tab"}

        if any(p in clean for p in ["atualizar página", "atualizar pagina", "recarregar", "f5"]):
            res = SystemController.refresh_page()
            return {"speech": f"Página atualizada.", "action": "refresh_page"}

        if any(p in clean for p in ["rolar para baixo", "rola para baixo", "descer página", "desce"]):
            res = SystemController.scroll_down()
            return {"speech": f"Rolando para baixo.", "action": "scroll_down"}

        if any(p in clean for p in ["rolar para cima", "rola para cima", "subir página", "sobe"]):
            res = SystemController.scroll_up()
            return {"speech": f"Rolando para cima.", "action": "scroll_up"}

        # ==========================================
        # 3. CONTROLE DE VOLUME & MÍDIA
        # ==========================================
        if any(p in clean for p in ["aumentar volume", "aumenta o volume", "aumenta o som", "mais alto", "sobe o som", "aumenta"]):
            res = SystemController.volume_up(6)
            return {"speech": f"Volume aumentado, {user}.", "action": "volume_up"}

        if any(p in clean for p in ["diminuir volume", "diminui o volume", "abaixa o som", "abaixar volume", "mais baixo", "abaixa"]):
            res = SystemController.volume_down(6)
            return {"speech": f"Volume reduzido, {user}.", "action": "volume_down"}

        if any(p in clean for p in ["mutar", "mudo", "silenciar", "desmutar", "tirar do mudo"]):
            res = SystemController.toggle_mute()
            return {"speech": f"Áudio alternado.", "action": "toggle_mute"}

        if any(p in clean for p in ["pausar música", "pausar musica", "pausar", "pause", "play", "despausar", "continuar"]):
            res = SystemController.media_play_pause()
            return {"speech": f"Mídia alternada.", "action": "media_play_pause"}

        if any(p in clean for p in ["próxima música", "proxima musica", "pular música", "avançar"]):
            res = SystemController.media_next()
            return {"speech": f"Próxima faixa.", "action": "media_next"}

        if any(p in clean for p in ["música anterior", "musica anterior", "voltar"]):
            res = SystemController.media_prev()
            return {"speech": f"Faixa anterior.", "action": "media_prev"}

        # ==========================================
        # 4. SEGURANÇA E PRINT
        # ==========================================
        if any(p in clean for p in ["bloquear pc", "bloquear o pc", "bloquear tela", "bloquear computador", "travar pc"]):
            res = SystemController.lock_pc()
            return {"speech": f"Bloqueando computador imediatamente, {user}.", "action": "lock_pc"}

        if any(p in clean for p in ["tirar print", "print da tela", "screenshot", "captura de tela", "tire um print", "print"]):
            res = SystemController.take_screenshot()
            if res.get("success"):
                return {"speech": f"Print capturado com sucesso, {user}.", "action": "screenshot", "details": res}
            return {"speech": f"Captura realizada, {user}.", "action": "screenshot"}

        if any(p in clean for p in ["limpar lixeira", "esvaziar lixeira", "esvazie a lixeira"]):
            res = SystemController.empty_recycle_bin()
            return {"speech": f"Lixeira esvaziada, {user}.", "action": "empty_recycle"}

        # Status do PC
        if any(p in clean for p in ["status do sistema", "status do pc", "como está a máquina", "como esta a maquina", "diagnóstico"]):
            telem = SystemController.get_system_telemetry()
            cpu = telem["cpu"]["percent"]
            ram = telem["ram"]["percent"]
            return {"speech": f"Processador em {cpu}% e memória em {ram}%, tudo operacional, {user}.", "action": "telemetry", "details": telem}

        # Abrir Aplicativos Genéricos e Pastas
        open_match = re.search(r'(?:abrir|abra|iniciar|inicie|executar|execute|acessar|acesse)\s+(?:o\s+|a\s+|pasta\s+|pasta de\s+)?(.+)', clean)
        if open_match:
            app_target = re.sub(r'[?!.,;]+$', '', open_match.group(1).strip()).strip()
            res = SystemController.open_app(app_target)
            return {"speech": f"Iniciando {app_target}, {user}.", "action": "open_app", "details": res}

        return None

    def _fallback_chat_response(self, clean: str) -> dict:
        user = self.config.get('user_name', 'senhor')
        return {
            "speech": f"Às suas ordens, {user}. Diga o aplicativo ou comando que deseja executar.",
            "action": "ready"
        }

    async def _process_with_gemini(self, text: str) -> dict:
        """Gemini com foco exclusivo em EXECUÇÃO DE COMANDOS DO SISTEMA."""
        user = self.config.get('user_name', 'senhor')
        system_instruction = (
            f"Você é J.A.R.V.I.S., o operador e piloto do computador do usuário ({user}). "
            "O usuário NÃO quer explicações longas e NÃO quer conversas teóricas. "
            "Ele quer controlar o computador 100% por voz, sem usar teclado e sem mouse. "
            "Sua tarefa é interpretar a ordem e responder em 1 frase curta com a tag de ação no início: "
            "[ACTION:open_url:https://www.youtube.com] quando ele quiser YouTube; "
            "[ACTION:open_app:NOME] para abrir qualquer programa ou pasta (como chrome, spotify, downloads, calculadora, bloco de notas); "
            "[ACTION:play_youtube:TERMO] para pesquisar ou tocar algo no YouTube; "
            "[ACTION:search:TERMO] para pesquisar no Google; "
            "[ACTION:volume_up] ou [ACTION:volume_down] para áudio; "
            "[ACTION:close_window] para fechar janela; "
            "[ACTION:switch_window] para alternar janela; "
            "[ACTION:screenshot] para print; "
            "[ACTION:lock_pc] para bloquear. "
            "Exemplo de resposta: '[ACTION:open_url:https://www.youtube.com] Abrindo o YouTube imediatamente, senhor.'"
        )

        models_to_try = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]
        for model_name in models_to_try:
            try:
                response = self.gemini_client.models.generate_content(
                    model=model_name,
                    contents=text,
                    config={
                        "system_instruction": system_instruction,
                        "temperature": 0.3,
                    }
                )
                raw_answer = response.text.strip()
                action_name = "gemini_response"
                details = None

                action_match = re.match(r'\[ACTION:([^\]]+)\]\s*(.*)', raw_answer, re.DOTALL)
                if action_match:
                    action_cmd = action_match.group(1).strip()
                    spoken_text = action_match.group(2).strip()

                    if action_cmd.startswith("open_url:"):
                        target = action_cmd.split(":", 1)[1]
                        details = SystemController.open_url(target)
                        action_name = "open_url"
                    elif action_cmd.startswith("open_app:"):
                        target = action_cmd.split(":", 1)[1]
                        details = SystemController.open_app(target)
                        action_name = "open_app"
                    elif action_cmd.startswith("play_youtube:"):
                        query = action_cmd.split(":", 1)[1]
                        details = SystemController.play_youtube(query)
                        action_name = "youtube"
                    elif action_cmd.startswith("play_spotify:"):
                        query = action_cmd.split(":", 1)[1]
                        details = SystemController.play_spotify(query)
                        action_name = "spotify"
                    elif action_cmd.startswith("search:"):
                        query = action_cmd.split(":", 1)[1]
                        details = SystemController.search_web(query)
                        action_name = "search"
                    elif action_cmd == "volume_up":
                        details = SystemController.volume_up()
                        action_name = "volume_up"
                    elif action_cmd == "volume_down":
                        details = SystemController.volume_down()
                        action_name = "volume_down"
                    elif action_cmd == "close_window":
                        details = SystemController.close_window()
                        action_name = "close_window"
                    elif action_cmd == "switch_window":
                        details = SystemController.switch_window()
                        action_name = "switch_window"
                    elif action_cmd == "screenshot":
                        details = SystemController.take_screenshot()
                        action_name = "screenshot"
                    elif action_cmd == "lock_pc":
                        details = SystemController.lock_pc()
                        action_name = "lock_pc"

                    return {"speech": spoken_text or f"Executado, {user}.", "action": action_name, "details": details}

                return {"speech": raw_answer, "action": "gemini_response"}
            except Exception as e:
                continue

        return self._fallback_chat_response(text.lower())
