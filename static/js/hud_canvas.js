/**
 * J.A.R.V.I.S. // ARC REACTOR HUD CANVAS & VISUALIZERS
 * Renders the iconic Stark Industries Arc Reactor with multiple rotating rings,
 * audio frequency wave monitors, and ambient holographic particles.
 */

class ArcReactorRenderer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    
    this.width = this.canvas.width;
    this.height = this.canvas.height;
    this.centerX = this.width / 2;
    this.centerY = this.height / 2;

    this.angle1 = 0;
    this.angle2 = 0;
    this.angle3 = 0;
    this.pulse = 0;
    this.pulseSpeed = 0.03;

    // States: 'idle', 'listening', 'processing', 'speaking'
    this.state = 'idle';
    this.audioAmplitude = 0; // 0 to 1

    this.init();
  }

  setState(newState) {
    this.state = newState;
    const textElem = document.getElementById('reactor-state-text');
    if (!textElem) return;

    if (newState === 'listening') {
      textElem.textContent = 'ESCUTANDO...';
      textElem.style.color = '#ffb700';
      textElem.style.textShadow = '0 0 15px rgba(255, 183, 0, 0.8)';
    } else if (newState === 'processing') {
      textElem.textContent = 'PROCESSANDO...';
      textElem.style.color = '#a855f7';
      textElem.style.textShadow = '0 0 15px rgba(168, 85, 247, 0.8)';
    } else if (newState === 'speaking') {
      textElem.textContent = 'J.A.R.V.I.S. FALANDO';
      textElem.style.color = '#00f0ff';
      textElem.style.textShadow = '0 0 15px rgba(0, 240, 255, 0.9)';
    } else {
      textElem.textContent = 'SISTEMA ONLINE';
      textElem.style.color = '#ffffff';
      textElem.style.textShadow = '0 0 12px rgba(0, 240, 255, 0.6)';
    }
  }

  setAudioAmplitude(val) {
    this.audioAmplitude = Math.max(0, Math.min(1, val));
  }

  init() {
    this.animate();
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    this.draw();
  }

  draw() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    // Dynamic rotation speeds based on state
    let speedMult = 1;
    if (this.state === 'listening') speedMult = 2.5;
    if (this.state === 'processing') speedMult = 4;
    if (this.state === 'speaking') speedMult = 1.8;

    this.angle1 += 0.008 * speedMult;
    this.angle2 -= 0.012 * speedMult;
    this.angle3 += 0.005 * speedMult;
    this.pulse += this.pulseSpeed * speedMult;

    // Glow colors based on state
    let primaryGlow = 'rgba(0, 240, 255, ';
    if (this.state === 'listening') primaryGlow = 'rgba(255, 183, 0, ';
    if (this.state === 'processing') primaryGlow = 'rgba(168, 85, 247, ';

    const cx = this.centerX;
    const cy = this.centerY;

    ctx.save();
    ctx.translate(cx, cy);

    // 1. Outer Tech Target Ring (Radius: 230)
    ctx.beginPath();
    ctx.arc(0, 0, 230, 0, Math.PI * 2);
    ctx.strokeStyle = primaryGlow + '0.15)';
    ctx.lineWidth = 1;
    ctx.stroke();

    // 2. Segmented Outer Track with Ticks
    ctx.save();
    ctx.rotate(this.angle1 * 0.4);
    for (let i = 0; i < 36; i++) {
      const rad = (i * 10 * Math.PI) / 180;
      const isMajor = i % 3 === 0;
      const len = isMajor ? 12 : 6;
      ctx.beginPath();
      ctx.moveTo(Math.cos(rad) * 218, Math.sin(rad) * 218);
      ctx.lineTo(Math.cos(rad) * (218 - len), Math.sin(rad) * (218 - len));
      ctx.strokeStyle = isMajor ? primaryGlow + '0.7)' : primaryGlow + '0.25)';
      ctx.lineWidth = isMajor ? 2 : 1;
      ctx.stroke();
    }
    ctx.restore();

    // 3. Middle Dash Ring (Radius: 185)
    ctx.save();
    ctx.rotate(this.angle2);
    ctx.beginPath();
    ctx.arc(0, 0, 185, 0, Math.PI * 2);
    ctx.setLineDash([18, 12, 6, 12]);
    ctx.strokeStyle = primaryGlow + '0.6)';
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.restore();

    // 4. Hexagonal Aperture Grid (Radius: 155)
    ctx.save();
    ctx.rotate(this.angle3);
    for (let i = 0; i < 8; i++) {
      const a = (i * Math.PI) / 4;
      ctx.beginPath();
      ctx.arc(0, 0, 155, a, a + 0.28);
      ctx.strokeStyle = primaryGlow + '0.85)';
      ctx.lineWidth = 5;
      ctx.shadowColor = primaryGlow + '0.8)';
      ctx.shadowBlur = 10;
      ctx.stroke();
    }
    ctx.restore();

    // 5. Ten Arc Coils (Stark Power Generator)
    const coilRadius = 125;
    ctx.save();
    ctx.rotate(this.angle1);
    for (let i = 0; i < 10; i++) {
      const angle = (i * Math.PI * 2) / 10;
      ctx.save();
      ctx.rotate(angle);
      ctx.translate(0, -coilRadius);

      // Copper/Energy Coil Block
      ctx.beginPath();
      ctx.rect(-12, -7, 24, 14);
      ctx.fillStyle = primaryGlow + '0.2)';
      ctx.fill();
      ctx.strokeStyle = primaryGlow + '0.9)';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Inner coil wires
      ctx.beginPath();
      ctx.moveTo(-6, -7);
      ctx.lineTo(-6, 7);
      ctx.moveTo(0, -7);
      ctx.lineTo(0, 7);
      ctx.moveTo(6, -7);
      ctx.lineTo(6, 7);
      ctx.strokeStyle = primaryGlow + '0.5)';
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.restore();
    }
    ctx.restore();

    // 6. Inner Energy Containment Ring
    const pulseFactor = Math.sin(this.pulse) * 4;
    const audioExpansion = this.audioAmplitude * 20;
    const coreRadius = 80 + pulseFactor + audioExpansion;

    ctx.beginPath();
    ctx.arc(0, 0, 95, 0, Math.PI * 2);
    ctx.strokeStyle = primaryGlow + '0.4)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // 7. Glowing Core Gradient
    const coreGrad = ctx.createRadialGradient(0, 0, 5, 0, 0, coreRadius);
    coreGrad.addColorStop(0, '#ffffff');
    coreGrad.addColorStop(0.3, primaryGlow + '0.95)');
    coreGrad.addColorStop(0.7, primaryGlow + '0.4)');
    coreGrad.addColorStop(1, 'transparent');

    ctx.beginPath();
    ctx.arc(0, 0, coreRadius, 0, Math.PI * 2);
    ctx.fillStyle = coreGrad;
    ctx.shadowColor = primaryGlow + '1)';
    ctx.shadowBlur = 25 + (this.audioAmplitude * 30);
    ctx.fill();

    // Triangular Inner Core Target
    ctx.save();
    ctx.rotate(-this.angle2 * 0.8);
    ctx.beginPath();
    const triR = 40 + (audioExpansion * 0.5);
    for (let i = 0; i < 3; i++) {
      const a = (i * 2 * Math.PI) / 3 - Math.PI / 2;
      const x = Math.cos(a) * triR;
      const y = Math.sin(a) * triR;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.strokeStyle = primaryGlow + '0.9)';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();

    ctx.restore();
  }
}

// Realtime Waveform Oscilloscope Monitor
class WaveformMonitor {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.width = this.canvas.width;
    this.height = this.canvas.height;
    this.phase = 0;
    this.active = false;
    this.level = 0.2; // base ambient level
    this.init();
  }

  setLevel(level) {
    this.level = level;
    this.active = level > 0.05;
  }

  init() {
    this.animate();
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    this.draw();
  }

  draw() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    const mid = h / 2;

    ctx.clearRect(0, 0, w, h);
    this.phase += 0.06;

    // Draw grid background line
    ctx.beginPath();
    ctx.moveTo(0, mid);
    ctx.lineTo(w, mid);
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.15)';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Draw primary sine/voice wave
    ctx.beginPath();
    for (let x = 0; x < w; x++) {
      const normX = x / w;
      // Combined harmonic frequencies
      const amp = this.active ? (this.level * (h / 2.5)) : 3;
      const y = mid + Math.sin(normX * 18 + this.phase) * amp * Math.sin(normX * Math.PI)
                    + Math.cos(normX * 8 - this.phase * 1.5) * (amp * 0.4);
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }

    ctx.strokeStyle = this.active ? '#00f0ff' : 'rgba(0, 240, 255, 0.35)';
    ctx.lineWidth = 2;
    ctx.shadowColor = '#00f0ff';
    ctx.shadowBlur = this.active ? 12 : 4;
    ctx.stroke();

    // Second faint harmonic wave
    ctx.beginPath();
    for (let x = 0; x < w; x++) {
      const normX = x / w;
      const amp = this.active ? (this.level * (h / 3.5)) : 2;
      const y = mid + Math.sin(normX * 28 - this.phase * 0.8) * amp * Math.sin(normX * Math.PI);
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.2)';
    ctx.lineWidth = 1;
    ctx.stroke();
  }
}

// Background Floating Holographic Particles
class ParticleField {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.particles = [];
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.createParticles();
    this.animate();
  }

  resize() {
    this.width = this.canvas.width = window.innerWidth;
    this.height = this.canvas.height = window.innerHeight;
  }

  createParticles() {
    const count = Math.min(60, Math.floor(this.width / 25));
    this.particles = [];
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        size: Math.random() * 2 + 0.8,
        alpha: Math.random() * 0.5 + 0.2
      });
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = this.width;
      if (p.x > this.width) p.x = 0;
      if (p.y < 0) p.y = this.height;
      if (p.y > this.height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, 240, 255, ${p.alpha})`;
      ctx.fill();

      // Connect nearby particles with subtle lines
      for (let j = i + 1; j < this.particles.length; j++) {
        const p2 = this.particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 100) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(0, 240, 255, ${(1 - dist / 100) * 0.08})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }
  }
}

// Global Instances
window.arcReactor = new ArcReactorRenderer('arc-reactor-canvas');
window.waveformMonitor = new WaveformMonitor('waveform-canvas');
window.particleField = new ParticleField('bg-particles');
