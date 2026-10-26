/**
 * J.A.R.V.I.S. // 100% HANDS-FREE CONTINUOUS VOICE ENGINE
 * Handles continuous microphone listening, noise filtering,
 * automatic silence detection, live transcript streaming, and audio feedback.
 */

class SpeechEngine {
  constructor() {
    this.recognition = null;
    this.mediaStream = null;
    this.isListening = false;
    this.isJarvisSpeaking = false;
    this.audioPlayer = document.getElementById('jarvis-audio-player');
    this.wakeWord = 'jarvis';
    this.audioContext = null;
    this.analyser = null;
    
    // Silence timer for fast command dispatch
    this.silenceTimer = null;
    this.lastSpokenText = '';

    this.initAudioContext();
    this.initRecognition();
    this.setupAudioPlayerHooks();
  }

  initAudioContext() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.audioContext = new AudioCtx();
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 64;
      }
    } catch (e) {
      console.warn("Web Audio API indisponível:", e);
    }
  }

  setupAudioPlayerHooks() {
    if (!this.audioPlayer) return;

    let source = null;
    this.audioPlayer.addEventListener('play', () => {
      this.isJarvisSpeaking = true;
      if (this.audioContext && this.audioContext.state === 'suspended') {
        this.audioContext.resume();
      }
      if (!source && this.audioContext && this.analyser) {
        try {
          source = this.audioContext.createMediaElementSource(this.audioPlayer);
          source.connect(this.analyser);
          this.analyser.connect(this.audioContext.destination);
        } catch (e) {}
      }
      this.monitorVoiceAudio();
    });

    this.audioPlayer.addEventListener('ended', () => {
      this.isJarvisSpeaking = false;
      if (window.arcReactor) window.arcReactor.setState('listening');
      if (window.waveformMonitor) window.waveformMonitor.setLevel(0.08);
      const stateBadge = document.getElementById('audio-state-tag');
      if (stateBadge) stateBadge.textContent = 'ESCUTANDO';
      const transcriptDisplay = document.getElementById('reactor-transcript');
      if (transcriptDisplay) transcriptDisplay.textContent = 'Ouvindo sua voz... Diga um comando.';
    });
  }

  monitorVoiceAudio() {
    if (!this.analyser || this.audioPlayer.paused) return;
    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(dataArray);

    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
    const avg = sum / dataArray.length;
    const norm = Math.min(1, avg / 128);

    if (window.arcReactor) window.arcReactor.setAudioAmplitude(norm);
    if (window.waveformMonitor) window.waveformMonitor.setLevel(norm * 1.5);

    if (this.isJarvisSpeaking) {
      requestAnimationFrame(() => this.monitorVoiceAudio());
    }
  }

  playSound(type) {
    if (!this.audioContext) return;
    if (this.audioContext.state === 'suspended') {
      this.audioContext.resume();
    }

    try {
      const now = this.audioContext.currentTime;
      const osc = this.audioContext.createOscillator();
      const gain = this.audioContext.createGain();
      osc.connect(gain);
      gain.connect(this.audioContext.destination);

      if (type === 'activate') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(1760, now + 0.12);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
        osc.start(now);
        osc.stop(now + 0.25);
      } else if (type === 'confirm') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(523.25, now);
        osc.frequency.setValueAtTime(659.25, now + 0.08);
        osc.frequency.setValueAtTime(1046.50, now + 0.16);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
        osc.start(now);
        osc.stop(now + 0.35);
      }
    } catch (e) {}
  }

  async startContinuousMicrophone() {
    // 1. Abre permissão definitiva de microfone para manter stream aberto no Chrome
    try {
      if (!this.mediaStream) {
        this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      }
    } catch (err) {
      console.warn("Microfone negado ou bloqueado nas configurações do navegador:", err);
    }

    // 2. Inicia o reconhecimento de voz contínuo
    this.startRecognitionLoop();
  }

  initRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
      console.warn("Reconhecimento de fala nativo não suportado neste navegador.");
      return;
    }

    this.recognition = new SpeechRec();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'pt-BR';

    this.recognition.onstart = () => {
      this.isListening = true;
      this.updateMicUI(true);
      if (window.arcReactor && !this.isJarvisSpeaking) {
        window.arcReactor.setState('listening');
      }
      const stateBadge = document.getElementById('audio-state-tag');
      if (stateBadge) stateBadge.textContent = 'ESCUTANDO';
      const transcriptDisplay = document.getElementById('reactor-transcript');
      if (transcriptDisplay) transcriptDisplay.textContent = 'Microfone 100% ativo. Pode falar!';
    };

    this.recognition.onresult = (event) => {
      // Ignora áudio se o próprio Jarvis estiver falando pelos alto-falantes
      if (this.isJarvisSpeaking) return;

      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const text = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += text;
        } else {
          interim += text;
        }
      }

      const activeText = (final || interim).trim();
      if (!activeText) return;

      // CALMA & PACIÊNCIA: Não corta o usuário no meio da frase
      // Exibe em tempo real o que está sendo dito
      const transcriptDisplay = document.getElementById('reactor-transcript');
      if (transcriptDisplay) {
        transcriptDisplay.textContent = `"${activeText}"`;
      }

      // Se detectou a palavra 'Jarvis', toca o chime futurista
      if (activeText.toLowerCase().includes(this.wakeWord) && !this.wakeChimePlayed) {
        this.playSound('activate');
        this.wakeChimePlayed = true;
      }

      // Reinicia o timer de silêncio: aguarda 1.8 segundos de pausa real para o usuário terminar a frase
      clearTimeout(this.silenceTimer);
      this.lastSpokenText = activeText;

      this.silenceTimer = setTimeout(() => {
        if (this.lastSpokenText && this.lastSpokenText.length > 2 && !this.isJarvisSpeaking) {
          const phraseToDispatch = this.lastSpokenText;
          this.lastSpokenText = '';
          this.dispatchSpokenCommand(phraseToDispatch);
        }
      }, 1800);
    };

    this.recognition.onerror = (event) => {
      if (event.error !== 'no-speech') {
        console.warn("Speech recognition status:", event.error);
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;
      this.wakeChimePlayed = false;
      // Auto-reconexão imediata e perpétua para garantir mãos 100% livres
      setTimeout(() => {
        if (!this.isJarvisSpeaking) {
          this.startRecognitionLoop();
        }
      }, 200);
    };
  }

  dispatchSpokenCommand(phrase) {
    clearTimeout(this.silenceTimer);
    let command = phrase.trim();
    if (!command || command.length < 2) return;

    // Se começou com 'Jarvis', limpa a palavra-chave para processar o comando
    command = command.replace(new RegExp(`^(ei\\s+|ok\\s+|olá\\s+)?${this.wakeWord}\\s*,?\\s*`, 'i'), '').trim();

    if (command.length > 0) {
      this.lastSpokenText = '';
      this.wakeChimePlayed = false;
      if (window.app) {
        window.app.executeCommand(command);
      }
    }
  }

  startRecognitionLoop() {
    if (!this.recognition) return;
    try {
      this.recognition.start();
    } catch (e) {
      // Já está escutando
    }
  }

  toggleListening() {
    if (this.isListening) {
      try { this.recognition.stop(); } catch (e) {}
      this.updateMicUI(false);
    } else {
      this.startContinuousMicrophone();
    }
  }

  updateMicUI(active) {
    const micBtn = document.getElementById('btn-mic-toggle');
    const wakeInd = document.getElementById('wake-indicator');
    if (micBtn) {
      if (active) micBtn.classList.add('listening');
      else micBtn.classList.remove('listening');
    }
    if (wakeInd) {
      if (active) wakeInd.classList.add('active');
      else wakeInd.classList.remove('active');
    }
  }
}

window.speechEngine = new SpeechEngine();
