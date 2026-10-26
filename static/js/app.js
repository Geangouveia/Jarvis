/**
 * J.A.R.V.I.S. // MAIN APPLICATION LOGIC & STARK OS CONTROLLER
 */

class JarvisApp {
  constructor() {
    this.ws = null;
    this.config = {};
    this.init();
  }

  init() {
    this.initLucideIcons();
    this.startClock();
    this.connectWebSocket();
    this.bindEvents();
    this.loadConfig();
    this.loadNotesCount();

    // Inicia microfone contínuo imediatamente (se permissão já foi dada)
    if (window.speechEngine) {
      window.speechEngine.startContinuousMicrophone();
    }

    // Se o navegador exigir interação do usuário, ativa no primeiro clique
    const enableAudio = () => {
      if (window.speechEngine) {
        window.speechEngine.startContinuousMicrophone();
      }
      const banner = document.getElementById('mic-activation-overlay');
      if (banner) banner.style.display = 'none';
    };
    document.body.addEventListener('click', enableAudio, { once: true });
  }

  initLucideIcons() {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  startClock() {
    const updateTime = () => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('pt-BR');
      const dateStr = now.toLocaleDateString('pt-BR', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).toUpperCase();

      const clockElem = document.getElementById('hud-clock');
      const dateElem = document.getElementById('hud-date');
      if (clockElem) clockElem.textContent = timeStr;
      if (dateElem) dateElem.textContent = dateStr;
    };
    updateTime();
    setInterval(updateTime, 1000);
  }

  connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;

    const statusElem = document.getElementById('connection-status-text');

    const connect = () => {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        if (statusElem) statusElem.textContent = 'CONECTADO AO SERVIDOR LOCAL';
        const dot = document.querySelector('.status-indicator-dot');
        if (dot) dot.className = 'status-indicator-dot online';
      };

      this.ws.onmessage = (event) => {
        try {
          const telemetry = JSON.parse(event.data);
          this.updateTelemetryUI(telemetry);
        } catch (e) {
          console.error("Erro ao decodificar telemetria:", e);
        }
      };

      this.ws.onclose = () => {
        if (statusElem) statusElem.textContent = 'RECONECTANDO AO SISTEMA...';
        const dot = document.querySelector('.status-indicator-dot');
        if (dot) dot.className = 'status-indicator-dot';
        setTimeout(connect, 3000);
      };

      this.ws.onerror = () => {
        this.ws.close();
      };
    };

    connect();
  }

  updateTelemetryUI(data) {
    if (!data) return;

    // CPU Gauge
    const cpuVal = data.cpu.percent || 0;
    const cpuValElem = document.getElementById('cpu-val');
    const cpuBar = document.getElementById('cpu-gauge-bar');
    const cpuDetail = document.getElementById('cpu-detail');
    if (cpuValElem) cpuValElem.textContent = Math.round(cpuVal);
    if (cpuBar) cpuBar.setAttribute('stroke-dasharray', `${cpuVal}, 100`);
    if (cpuDetail) cpuDetail.textContent = `${data.cpu.cores} Cores @ ${data.cpu.freq_ghz || '--'} GHz`;

    // RAM Gauge
    const ramVal = data.ram.percent || 0;
    const ramValElem = document.getElementById('ram-val');
    const ramBar = document.getElementById('ram-gauge-bar');
    const ramDetail = document.getElementById('ram-detail');
    if (ramValElem) ramValElem.textContent = Math.round(ramVal);
    if (ramBar) ramBar.setAttribute('stroke-dasharray', `${ramVal}, 100`);
    if (ramDetail) ramDetail.textContent = `${data.ram.used_gb} GB / ${data.ram.total_gb} GB`;

    // Disk C:
    const diskElem = document.getElementById('disk-val');
    if (diskElem) diskElem.textContent = `${data.disk.free_gb} GB Livres`;

    // Battery / Power
    const batteryElem = document.getElementById('battery-val');
    if (batteryElem) {
      if (data.battery) {
        const charging = data.battery.power_plugged ? 'Carregando' : 'Bateria';
        batteryElem.textContent = `${data.battery.percent}% (${charging})`;
      } else {
        batteryElem.textContent = 'Conectado (AC)';
      }
    }

    // Uptime
    const uptimeElem = document.getElementById('uptime-val');
    if (uptimeElem) uptimeElem.textContent = data.uptime || '--';
  }

  async executeCommand(rawCommand) {
    const command = rawCommand.trim();
    if (!command) return;

    // Log user command to terminal
    this.logToTerminal('user', command);

    // Update Arc Reactor to processing
    if (window.arcReactor) window.arcReactor.setState('processing');
    const transcriptDisplay = document.getElementById('reactor-transcript');
    if (transcriptDisplay) transcriptDisplay.textContent = `Executando: "${command}"`;

    try {
      const response = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
      });

      const data = await response.json();

      if (data.success) {
        // Log Jarvis answer
        this.logToTerminal('jarvis', data.speech);

        if (window.speechEngine) {
          window.speechEngine.playSound('confirm');
        }

        // Play synthetic voice audio
        if (data.audio_url) {
          this.playJarvisAudio(data.audio_url);
        } else {
          if (window.arcReactor) window.arcReactor.setState('idle');
        }

        // Se a ação for abrir URL / YouTube / busca, abre a aba imediatamente no navegador
        if (data.details && typeof data.details === 'string' && data.details.startsWith('http')) {
          try {
            window.open(data.details, '_blank');
          } catch (e) {
            console.warn("Popup bloqueado:", e);
          }
        }

        // If command was adding a note, update count
        if (data.action === 'add_note' || data.action === 'delete_note') {
          this.loadNotesCount();
        }
      } else {
        this.logToTerminal('system', 'Falha na execução do protocolo.');
        if (window.arcReactor) window.arcReactor.setState('idle');
      }
    } catch (err) {
      console.error("Erro na requisição de comando:", err);
      this.logToTerminal('system', `Erro de conexão: ${err.message}`);
      if (window.arcReactor) window.arcReactor.setState('idle');
    }
  }

  playJarvisAudio(audioUrl) {
    const player = document.getElementById('jarvis-audio-player');
    if (!player) return;

    if (window.arcReactor) window.arcReactor.setState('speaking');
    const stateBadge = document.getElementById('audio-state-tag');
    if (stateBadge) stateBadge.textContent = 'FALANDO';

    player.src = audioUrl;
    player.play().catch(e => {
      console.warn("Autoplay bloqueado pelo navegador até o primeiro clique:", e);
      if (window.arcReactor) window.arcReactor.setState('idle');
    });
  }

  logToTerminal(type, text) {
    const feed = document.getElementById('terminal-feed');
    if (!feed) return;

    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;

    const timeSpan = document.createElement('span');
    timeSpan.className = 'log-time';

    const now = new Date().toLocaleTimeString('pt-BR');
    if (type === 'user') {
      timeSpan.textContent = `[SENHOR ${now}]`;
    } else if (type === 'jarvis') {
      timeSpan.textContent = `[JARVIS ${now}]`;
    } else {
      timeSpan.textContent = `[SISTEMA ${now}]`;
    }

    const msgSpan = document.createElement('span');
    msgSpan.className = 'log-msg';
    msgSpan.textContent = text;

    entry.appendChild(timeSpan);
    entry.appendChild(msgSpan);
    feed.appendChild(entry);

    feed.scrollTop = feed.scrollHeight;
  }

  bindEvents() {
    // Command Text Input & Send Button
    const input = document.getElementById('command-input');
    const sendBtn = document.getElementById('btn-send-command');

    const handleSend = () => {
      const val = input.value.trim();
      if (val) {
        this.executeCommand(val);
        input.value = '';
      }
    };

    if (sendBtn) sendBtn.addEventListener('click', handleSend);
    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleSend();
      });
    }

    // Microphone Orb Toggle
    const micBtn = document.getElementById('btn-mic-toggle');
    if (micBtn) {
      micBtn.addEventListener('click', () => {
        if (window.speechEngine) {
          window.speechEngine.toggleListening();
        }
      });
    }

    // Continuous Listen Checkbox
    const continuousToggle = document.getElementById('continuous-listen-toggle');
    if (continuousToggle) {
      continuousToggle.addEventListener('change', (e) => {
        if (window.speechEngine) {
          window.speechEngine.continuous = e.target.checked;
          if (e.target.checked) window.speechEngine.startListening();
          else window.speechEngine.stopListening();
        }
      });
    }

    // Quick Command Chips
    document.querySelectorAll('.action-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const cmd = chip.getAttribute('data-cmd');
        if (cmd) this.executeCommand(cmd);
      });
    });

    // Clear Terminal Log
    const clearLogBtn = document.getElementById('btn-clear-log');
    if (clearLogBtn) {
      clearLogBtn.addEventListener('click', () => {
        const feed = document.getElementById('terminal-feed');
        if (feed) {
          feed.innerHTML = `
            <div class="log-entry log-system">
              <span class="log-time">[SISTEMA]</span>
              <span class="log-msg">Terminal limpo. Protocolo em espera.</span>
            </div>
          `;
        }
      });
    }

    // Test Voice Button
    const testVoiceBtn = document.getElementById('btn-test-voice');
    if (testVoiceBtn) {
      testVoiceBtn.addEventListener('click', () => {
        this.executeCommand("status do sistema");
      });
    }

    // Settings Modal
    this.bindSettingsModal();

    // Notes Modal
    this.bindNotesModal();

    // Screenshots Modal
    this.bindScreenshotsModal();
  }

  bindSettingsModal() {
    const modal = document.getElementById('settings-modal');
    const openBtn = document.getElementById('btn-open-settings');
    const closeBtn = document.getElementById('btn-close-settings');
    const saveBtn = document.getElementById('btn-save-settings');

    if (openBtn) openBtn.addEventListener('click', () => modal.classList.add('active'));
    if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.remove('active'));

    if (saveBtn) {
      saveBtn.addEventListener('click', async () => {
        const geminiKey = document.getElementById('cfg-gemini-key').value.trim();
        const voice = document.getElementById('cfg-voice-select').value;
        const userName = document.getElementById('cfg-user-name').value.trim();

        const payload = { voice };
        if (geminiKey) payload.gemini_api_key = geminiKey;
        if (userName) payload.user_name = userName;

        try {
          const res = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          if (data.success) {
            modal.classList.remove('active');
            this.logToTerminal('system', 'Configurações atualizadas com sucesso.');
            this.loadConfig();
          }
        } catch (e) {
          alert("Erro ao salvar configurações.");
        }
      });
    }
  }

  async loadConfig() {
    try {
      const res = await fetch('/api/config');
      this.config = await res.json();

      const aiStatus = document.getElementById('ai-status-val');
      if (aiStatus) {
        aiStatus.textContent = this.config.has_api_key ? 'Google Gemini 2.5' : 'Motor Local';
        aiStatus.style.color = this.config.has_api_key ? '#00ff88' : '#00f0ff';
      }

      const voiceSelect = document.getElementById('cfg-voice-select');
      if (voiceSelect && this.config.voice) {
        voiceSelect.value = this.config.voice;
      }

      const nameInput = document.getElementById('cfg-user-name');
      if (nameInput && this.config.user_name) {
        nameInput.value = this.config.user_name;
      }
    } catch (e) {
      console.warn("Falha ao carregar configurações:", e);
    }
  }

  bindNotesModal() {
    const modal = document.getElementById('notes-modal');
    const openBtn = document.getElementById('btn-toggle-notes');
    const closeBtn = document.getElementById('btn-close-notes');
    const addBtn = document.getElementById('btn-add-note');
    const input = document.getElementById('new-note-input');

    if (openBtn) {
      openBtn.addEventListener('click', () => {
        modal.classList.add('active');
        this.renderNotes();
      });
    }
    if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.remove('active'));

    const handleAdd = async () => {
      const text = input.value.trim();
      if (!text) return;
      await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text })
      });
      input.value = '';
      this.renderNotes();
      this.loadNotesCount();
    };

    if (addBtn) addBtn.addEventListener('click', handleAdd);
    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleAdd();
      });
    }
  }

  async loadNotesCount() {
    try {
      const res = await fetch('/api/notes');
      const notes = await res.json();
      const badge = document.getElementById('notes-badge');
      if (badge) badge.textContent = notes.length;
    } catch (e) {}
  }

  async renderNotes() {
    const container = document.getElementById('notes-list-container');
    if (!container) return;
    container.innerHTML = '<span class="form-hint">Carregando anotações...</span>';

    try {
      const res = await fetch('/api/notes');
      const notes = await res.json();

      if (notes.length === 0) {
        container.innerHTML = '<span class="form-hint">Nenhuma anotação registrada ainda, senhor.</span>';
        return;
      }

      container.innerHTML = '';
      notes.forEach(note => {
        const item = document.createElement('div');
        item.className = 'note-item';
        item.innerHTML = `
          <div>
            <div class="note-text">${note.content}</div>
            <div class="note-date">${note.created_at}</div>
          </div>
          <button class="btn-del-note" data-id="${note.id}" title="Excluir"><i data-lucide="trash-2"></i></button>
        `;
        container.appendChild(item);
      });

      this.initLucideIcons();

      container.querySelectorAll('.btn-del-note').forEach(btn => {
        btn.addEventListener('click', async (e) => {
          const id = btn.getAttribute('data-id');
          await fetch(`/api/notes/${id}`, { method: 'DELETE' });
          this.renderNotes();
          this.loadNotesCount();
        });
      });
    } catch (e) {
      container.innerHTML = '<span class="form-hint">Falha ao carregar anotações.</span>';
    }
  }

  bindScreenshotsModal() {
    const modal = document.getElementById('screenshots-modal');
    const openBtn = document.getElementById('btn-view-screenshots');
    const closeBtn = document.getElementById('btn-close-screenshots');

    if (openBtn) {
      openBtn.addEventListener('click', () => {
        modal.classList.add('active');
        this.renderScreenshots();
      });
    }
    if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.remove('active'));
  }

  async renderScreenshots() {
    const container = document.getElementById('screenshots-grid-container');
    if (!container) return;
    container.innerHTML = '<span class="form-hint">Carregando capturas...</span>';

    try {
      const res = await fetch('/api/screenshots');
      const shots = await res.json();

      if (shots.length === 0) {
        container.innerHTML = '<span class="form-hint">Nenhum print salvo ainda. Diga "Jarvis, tirar print" para testar!</span>';
        return;
      }

      container.innerHTML = '';
      shots.forEach(s => {
        const card = document.createElement('div');
        card.className = 'screenshot-card';
        card.innerHTML = `
          <a href="${s.url}" target="_blank">
            <img src="${s.url}" alt="${s.filename}" />
          </a>
          <div class="screenshot-info">
            <span class="screenshot-name">${s.filename}</span>
            <a href="${s.url}" target="_blank" class="text-hud-btn">VER</a>
          </div>
        `;
        container.appendChild(card);
      });
    } catch (e) {
      container.innerHTML = '<span class="form-hint">Falha ao carregar screenshots.</span>';
    }
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.app = new JarvisApp();
});
