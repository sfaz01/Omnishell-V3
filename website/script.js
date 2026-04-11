/* ═══════════════════════════════════════════
   OmniShell Landing Page — Interactions v2
   Advanced animations, particles, tilt, spotlight
   ═══════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initNavbar();
    initTerminalAnimation();
    initScrollReveal();
    initCopyButtons();
    initMobileMenu();
    initSmoothScroll();
    animateStats();
    initCardSpotlight();
    initTerminalTilt();
    initParallaxGlow();
});

/* ── Floating Particles ── */
function initParticles() {
    const container = document.querySelector('.particles-container');
    if (!container) return;

    const particleCount = 25;
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';

        const size = Math.random() * 4 + 1;
        const left = Math.random() * 100;
        const duration = Math.random() * 15 + 10;
        const delay = Math.random() * 15;
        const hue = Math.random() > 0.5 ? '246, 92, 139' : '130, 92, 246';
        const opacity = Math.random() * 0.4 + 0.1;

        particle.style.cssText = `
            width: ${size}px; height: ${size}px;
            left: ${left}%; bottom: -10px;
            background: rgba(${hue}, ${opacity});
            animation-duration: ${duration}s;
            animation-delay: ${delay}s;
            box-shadow: 0 0 ${size * 3}px rgba(${hue}, ${opacity * 0.5});
        `;
        container.appendChild(particle);
    }
}

/* ── Navbar scroll effect ── */
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });
}

/* ── Terminal Tilt Effect ── */
function initTerminalTilt() {
    const terminal = document.querySelector('.terminal');
    if (!terminal) return;

    terminal.addEventListener('mousemove', (e) => {
        const rect = terminal.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = (y - centerY) / centerY * -4;
        const rotateY = (x - centerX) / centerX * 4;
        terminal.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });

    terminal.addEventListener('mouseleave', () => {
        terminal.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
    });
}

/* ── Card Spotlight (mouse follow) ── */
function initCardSpotlight() {
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            card.style.setProperty('--mouse-x', x + '%');
            card.style.setProperty('--mouse-y', y + '%');
        });
    });
}

/* ── Parallax Glow ── */
function initParallaxGlow() {
    const glows = document.querySelectorAll('.bg-glow');
    window.addEventListener('mousemove', (e) => {
        const x = (e.clientX / window.innerWidth - 0.5) * 30;
        const y = (e.clientY / window.innerHeight - 0.5) * 30;
        glows.forEach((glow, i) => {
            const factor = (i + 1) * 0.5;
            glow.style.transform = `translate(${x * factor}px, ${y * factor}px)`;
        });
    });
}

/* ── Terminal typing animation ── */
function initTerminalAnimation() {
    const terminal = document.getElementById('terminal-body');
    if (!terminal) return;

    const sequences = [
        [
            { type: 'prompt', text: 'USER >' },
            { type: 'typing', text: ' update my system', speed: 50 },
            { type: 'pause', duration: 600 },
            { type: 'line', html: '<span class="terminal__output">  👁️  Scanning: cat /etc/os-release</span>' },
            { type: 'pause', duration: 400 },
            { type: 'line', html: '<span class="terminal__info">🤖 SUGGESTION:</span>' },
            { type: 'line', html: '<span class="terminal__highlight">   sudo pacman -Syu</span>' },
            { type: 'pause', duration: 300 },
            { type: 'line', html: '<span class="terminal__output">  [E]xecute, [X]plain, [S]kip? </span><span class="terminal__command">e</span>' },
            { type: 'pause', duration: 500 },
            { type: 'line', html: '<span class="terminal__output">  :: Synchronizing package databases...</span>' },
            { type: 'line', html: '<span class="terminal__success">  ✅ Command executed successfully.</span>' },
        ],
        [
            { type: 'prompt', text: 'USER >' },
            { type: 'typing', text: ' install docker and start it', speed: 45 },
            { type: 'pause', duration: 600 },
            { type: 'line', html: '<span class="terminal__info">🤖 SUGGESTION:</span>' },
            { type: 'line', html: '<span class="terminal__highlight">   sudo pacman -S docker && sudo systemctl enable --now docker</span>' },
            { type: 'pause', duration: 300 },
            { type: 'line', html: '<span class="terminal__warning">  ⚠️  This command requires elevated privileges</span>' },
            { type: 'line', html: '<span class="terminal__output">  [E]xecute, [X]plain, [S]kip? </span><span class="terminal__command">e</span>' },
            { type: 'pause', duration: 700 },
            { type: 'line', html: '<span class="terminal__success">  ✅ Command executed successfully.</span>' },
        ],
        [
            { type: 'prompt', text: 'USER >' },
            { type: 'typing', text: ' delete everything on my disk', speed: 45 },
            { type: 'pause', duration: 800 },
            { type: 'line', html: '<span class="terminal__warning">🛡️  </span><span style="color: #f43f5e; font-weight: 600;">Blocked dangerous request.</span>' },
            { type: 'line', html: '<span class="terminal__output">  OmniShell refused to generate a destructive command.</span>' },
        ],
        [
            { type: 'prompt', text: 'USER >' },
            { type: 'typing', text: ' install nginx', speed: 50 },
            { type: 'pause', duration: 400 },
            { type: 'line', html: '<span class="terminal__info">🤖 SUGGESTION:</span>' },
            { type: 'line', html: '<span class="terminal__highlight">   sudo pacman -S nginx</span>' },
            { type: 'line', html: '<span class="terminal__output">  [E]xecute, [X]plain, [S]kip? </span><span class="terminal__command">e</span>' },
            { type: 'pause', duration: 400 },
            { type: 'line', html: '<span class="terminal__success">  ✅ Command executed successfully.</span>' },
            { type: 'pause', duration: 500 },
            { type: 'prompt', text: 'USER >' },
            { type: 'typing', text: ' now start it', speed: 50 },
            { type: 'pause', duration: 400 },
            { type: 'line', html: '<span class="terminal__output">  💬 Context: "it" → nginx</span>' },
            { type: 'line', html: '<span class="terminal__info">🤖 SUGGESTION:</span>' },
            { type: 'line', html: '<span class="terminal__highlight">   sudo systemctl enable --now nginx</span>' },
            { type: 'line', html: '<span class="terminal__output">  [E]xecute, [X]plain, [S]kip? </span><span class="terminal__command">e</span>' },
            { type: 'pause', duration: 400 },
            { type: 'line', html: '<span class="terminal__success">  ✅ Command executed successfully.</span>' },
        ],
    ];

    let currentSequence = 0;

    async function playSequence(sequence) {
        terminal.innerHTML = '';
        for (const step of sequence) {
            switch (step.type) {
                case 'prompt': {
                    const line = document.createElement('div');
                    line.className = 'terminal__line';
                    line.innerHTML = `<span class="terminal__prompt">${step.text}</span>`;
                    terminal.appendChild(line);
                    line.style.animation = 'none'; line.offsetHeight; line.style.animation = '';
                    await sleep(100);
                    break;
                }
                case 'typing': {
                    const lastLine = terminal.lastElementChild;
                    const span = document.createElement('span');
                    span.className = 'terminal__command';
                    lastLine.appendChild(span);
                    for (const char of step.text) {
                        span.textContent += char;
                        await sleep(step.speed || 50);
                    }
                    break;
                }
                case 'pause':
                    await sleep(step.duration || 500);
                    break;
                case 'line': {
                    const line = document.createElement('div');
                    line.className = 'terminal__line';
                    line.innerHTML = step.html;
                    terminal.appendChild(line);
                    line.style.animation = 'none'; line.offsetHeight; line.style.animation = '';
                    await sleep(200);
                    break;
                }
            }
        }
        // Cursor
        const cursor = document.createElement('div');
        cursor.className = 'terminal__line';
        cursor.innerHTML = '<span class="terminal__prompt">USER ></span> <span class="terminal__cursor"></span>';
        cursor.style.animation = 'none'; cursor.offsetHeight; cursor.style.animation = '';
        terminal.appendChild(cursor);
    }

    async function loop() {
        while (true) {
            await playSequence(sequences[currentSequence]);
            await sleep(3500);
            currentSequence = (currentSequence + 1) % sequences.length;
        }
    }

    setTimeout(() => loop(), 800);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/* ── Scroll Reveal ── */
function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('visible');
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.reveal, .reveal-stagger').forEach(el => observer.observe(el));
}

/* ── Copy to Clipboard ── */
function initCopyButtons() {
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const code = btn.closest('.install__step-code').querySelector('code').textContent;
            navigator.clipboard.writeText(code).then(() => {
                const orig = btn.textContent;
                btn.textContent = '✓ Copied!';
                btn.style.color = '#10b981';
                setTimeout(() => { btn.textContent = orig; btn.style.color = ''; }, 2000);
            });
        });
    });
}

/* ── Mobile Menu ── */
function initMobileMenu() {
    const toggle = document.querySelector('.navbar__toggle');
    const links = document.querySelector('.navbar__links');
    if (!toggle || !links) return;

    toggle.addEventListener('click', () => {
        links.classList.toggle('open');
        toggle.textContent = links.classList.contains('open') ? '✕' : '☰';
    });
    links.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
            links.classList.remove('open');
            toggle.textContent = '☰';
        });
    });
}

/* ── Smooth Scroll ── */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth' });
        });
    });
}

/* ── Animate Stats Counter ── */
function animateStats() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-count'));
                const suffix = el.getAttribute('data-suffix') || '';
                if (target) { animateCount(el, 0, target, 1500, suffix); observer.unobserve(el); }
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.stat__value').forEach(s => observer.observe(s));
}

function animateCount(el, start, end, duration, suffix) {
    const range = end - start;
    const startTime = performance.now();
    function update(t) {
        const progress = Math.min((t - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + range * eased) + suffix;
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}
