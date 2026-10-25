/* ==========================================================================
   Specs the Flying Bird AI Companion & Mascot — Static Corner & Hand Motion
   ========================================================================== */

(function () {
    'use strict';

    let chirpEnabled = true;

    // DOM Elements
    let widget, avatarBtn, bubble, bubbleText, bubbleClose, popoverCard, closeBtn, chirpBtn;
    let chatInput, sendBtn, answerArea;

    // Contextual Tips
    const pageTips = {
        '/': "Tweet! Hi, I'm Specs! Ready to explore your AI learning today?",
        '/chat': "Tweet! Ask me anything about Python, NLP, Data Structures, or AI!",
        '/dashboard': "Tweet! Look at your learning performance! Soaring high with great momentum!",
        '/quiz': "Tweet! Take a deep breath and read each question carefully! Bonus XP awaits!",
        '/subjects': "Tweet! Master prerequisites first to unlock advanced concept modules!",
        '/flashcards': "Tweet! Spaced repetition helps your memory stick like feathers on a bird!",
        '/knowledge-graph': "Tweet! Trace the prerequisite graph to see how every concept connects!",
        '/documents': "Tweet! Upload lecture notes so I can quiz you on your exact syllabus!",
        '/admin': "Tweet! Welcome to the Instructor & Curriculum Management Portal!"
    };

    // Synthetic Audio Synthesizer for Bird Chirp (Web Audio API)
    function playBirdChirp() {
        if (!chirpEnabled) return;
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            const ctx = new AudioContext();

            const now = ctx.currentTime;
            
            // First chirp pulse
            const osc1 = ctx.createOscillator();
            const gain1 = ctx.createGain();
            osc1.type = 'sine';
            osc1.frequency.setValueAtTime(2400, now);
            osc1.frequency.exponentialRampToValueAtTime(3600, now + 0.08);
            osc1.frequency.exponentialRampToValueAtTime(2800, now + 0.14);

            gain1.gain.setValueAtTime(0, now);
            gain1.gain.linearRampToValueAtTime(0.12, now + 0.02);
            gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.14);

            osc1.connect(gain1);
            gain1.connect(ctx.destination);
            osc1.start(now);
            osc1.stop(now + 0.15);

            // Second chirp pulse (higher pitch echo)
            const osc2 = ctx.createOscillator();
            const gain2 = ctx.createGain();
            osc2.type = 'sine';
            osc2.frequency.setValueAtTime(3000, now + 0.12);
            osc2.frequency.exponentialRampToValueAtTime(4200, now + 0.20);
            osc2.frequency.exponentialRampToValueAtTime(3200, now + 0.26);

            gain2.gain.setValueAtTime(0, now + 0.12);
            gain2.gain.linearRampToValueAtTime(0.15, now + 0.15);
            gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.28);

            osc2.connect(gain2);
            gain2.connect(ctx.destination);
            osc2.start(now + 0.12);
            osc2.stop(now + 0.29);

            setTimeout(() => { ctx.close(); }, 400);
        } catch (e) {
            // AudioContext not allowed before user interaction
        }
    }

    // Initialize Static Mascot System
    function init() {
        widget = document.getElementById('duo-companion-widget');
        avatarBtn = document.getElementById('duo-avatar-btn');
        bubble = document.getElementById('duo-speech-bubble');
        bubbleText = document.getElementById('duo-speech-text');
        bubbleClose = document.getElementById('duo-bubble-close');
        popoverCard = document.getElementById('duo-popover-card');
        closeBtn = document.getElementById('duo-close-btn');
        chirpBtn = document.getElementById('duo-chirp-btn');
        chatInput = document.getElementById('duo-chat-input');
        sendBtn = document.getElementById('duo-send-btn');
        answerArea = document.getElementById('duo-answer-area');

        if (!widget || !avatarBtn) return;

        // Set initial speech tip based on page route
        const pathname = window.location.pathname;
        const initialTip = pageTips[pathname] || "Tweet! I'm Specs, your study companion!";
        if (bubbleText) bubbleText.textContent = initialTip;

        // Auto-show tip and fade after 6 seconds
        showSpeechBubble(initialTip, 6000);

        // Setup Event Listeners
        setupEventListeners();

        // Load Gamification Data
        fetchGamificationData();

        // Periodic encouraging study tip every 35 seconds
        setInterval(showRandomStudyTip, 35000);
    }

    function showRandomStudyTip() {
        if (popoverCard && popoverCard.classList.contains('active')) return;
        const tips = [
            "Tweet! Don't forget to practice flashcards for long-term retention!",
            "Tweet! Need a concept explanation? Click me anytime to ask!",
            "Tweet! Consistency builds mastery! Great work today!",
            "Tweet! Check your Knowledge Graph to see prerequisites!"
        ];
        const randomTip = tips[Math.floor(Math.random() * tips.length)];
        showSpeechBubble(randomTip, 5000);
    }

    // Show Speech Bubble with Auto-dismiss
    let bubbleTimeout = null;
    function showSpeechBubble(text, duration = 4500) {
        if (!bubble || !bubbleText) return;
        bubbleText.textContent = text;
        bubble.style.display = 'flex';
        bubble.style.opacity = '1';

        if (bubbleTimeout) clearTimeout(bubbleTimeout);
        if (duration > 0) {
            bubbleTimeout = setTimeout(() => {
                bubble.style.opacity = '0';
                setTimeout(() => {
                    if (bubble.style.opacity === '0') bubble.style.display = 'none';
                }, 300);
            }, duration);
        }
    }

    // Setup All Event Listeners
    function setupEventListeners() {
        // Avatar Click -> Toggle Popover Drawer
        avatarBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            togglePopover();
        });

        // Speech Bubble Click -> Open Popover Drawer
        if (bubble) {
            bubble.addEventListener('click', (e) => {
                if (e.target === bubbleClose) return;
                togglePopover();
            });
        }

        if (bubbleClose) {
            bubbleClose.addEventListener('click', (e) => {
                e.stopPropagation();
                if (bubble) bubble.style.display = 'none';
            });
        }

        // Close Popover Button
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                closePopover();
            });
        }

        // Chirp Button
        if (chirpBtn) {
            chirpBtn.addEventListener('click', () => {
                playBirdChirp();
                showSpeechBubble("Tweet-tweet! Specs is energized and ready!", 3000);
            });
        }

        // Eye Tracking on Mouse Movement
        document.addEventListener('mousemove', (e) => {
            handleEyeTracking(e.clientX, e.clientY);
        });

        // Chat Input Handlers
        if (sendBtn) {
            sendBtn.addEventListener('click', sendQuickQuestion);
        }
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendQuickQuestion();
            });
        }
    }

    // Toggle Popover Drawer
    function togglePopover() {
        if (!popoverCard) return;
        const isActive = popoverCard.classList.toggle('active');
        const dot = document.getElementById('duo-badge-dot');
        if (dot) dot.style.display = 'none';

        if (isActive) {
            playBirdChirp();
            fetchGamificationData();
            showSpeechBubble("Tweet! What would you like to explore?", 3000);
        }
    }

    function closePopover() {
        if (!popoverCard) return;
        popoverCard.classList.remove('active');
    }

    // Eye Tracking relative to static bird position
    function handleEyeTracking(mouseX, mouseY) {
        const pupils = document.querySelectorAll('.bird-pupil');
        if (!pupils.length || !widget) return;

        const rect = widget.getBoundingClientRect();
        const birdCenterX = rect.left + rect.width / 2;
        const birdCenterY = rect.top + rect.height / 2;

        const dx = mouseX - birdCenterX;
        const dy = mouseY - birdCenterY;
        const angle = Math.atan2(dy, dx);
        const dist = Math.min(2.5, Math.hypot(dx, dy) * 0.012);

        const offsetX = Math.cos(angle) * dist;
        const offsetY = Math.sin(angle) * dist;

        pupils.forEach(pupil => {
            pupil.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
        });
    }

    // Markdown to HTML Formatter
    function renderMarkdownToHtml(text) {
        if (!text) return '';
        let html = text;

        html = html.replace(/```(?:[a-zA-Z0-9_\-]+)?\n([\s\S]*?)```/g, (match, code) => {
            const escaped = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return `<pre class="specs-code-block"><code>${escaped.trim()}</code></pre>`;
        });

        html = html.replace(/`([^`]+)`/g, (match, code) => {
            const escaped = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return `<code class="specs-inline-code">${escaped}</code>`;
        });

        html = html.replace(/^###\s+(.*?)$/gm, '<h6 class="specs-h">$1</h6>');
        html = html.replace(/^##\s+(.*?)$/gm, '<h6 class="specs-h">$1</h6>');
        html = html.replace(/^---$/gm, '<hr class="specs-divider">');
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/^[•\-\*]\s+(.*?)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*?<\/li>(\n|$) *)+/g, '<ul class="specs-list">$&</ul>');
        html = html.replace(/\n/g, '<br>');

        return html;
    }

    // Quick Question Submission to AI Backend
    function sendQuickQuestion() {
        if (!chatInput) return;
        const q = chatInput.value.trim ? chatInput.value.trim() : chatInput.value;
        if (!q) return;

        if (answerArea) {
            answerArea.classList.add('active');
            answerArea.innerHTML = '<i class="fa-solid fa-feather fa-spin me-2 text-primary"></i>Specs is searching and generating answer...';
        }

        fetch('/api/tutor/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: q })
        })
        .then(res => res.json())
        .then(data => {
            if (answerArea) {
                const answerText = data.answer || "Tweet! I couldn't process that question right now.";
                const formattedHtml = renderMarkdownToHtml(answerText);
                answerArea.innerHTML = `<div class="specs-formatted-answer"><strong class="text-primary"><i class="fa-solid fa-glasses me-1"></i> Specs Answer:</strong><div class="mt-2">${formattedHtml}</div></div>`;
                playBirdChirp();
            }
            chatInput.value = '';
            fetchGamificationData();
        })
        .catch(() => {
            if (answerArea) {
                answerArea.innerHTML = '<span class="text-danger"><i class="fa-solid fa-triangle-exclamation me-1"></i> Error getting answer. Please try again.</span>';
            }
        });
    }

    // Fetch Gamification & Streak for stats pills
    function fetchGamificationData() {
        fetch('/api/gamification/profile')
        .then(res => res.json())
        .then(data => {
            const streakVal = document.getElementById('duo-streak-val');
            const xpVal = document.getElementById('duo-xp-val');
            const levelVal = document.getElementById('duo-level-val');

            const streak = data.streak_days !== undefined ? data.streak_days : 1;
            const xp = data.total_xp !== undefined ? data.total_xp : 0;
            const level = data.level !== undefined ? data.level : 1;

            if (streakVal) streakVal.textContent = `🔥 ${streak}`;
            if (xpVal) xpVal.textContent = `⚡ ${xp}`;
            if (levelVal) levelVal.textContent = `🏆 ${level}`;
        })
        .catch(() => {});
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
