// ============================================================
// State
// ============================================================
const state = {
    personas: [],           // [{id, name, avatar, color}, ...]
    selectedPersonaIds: [], // ids the user picked on the setup screen
    sessionId: null,        // current session id (uuid)
    topic: "",
    isLoading: false,
};

// ============================================================
// Element references
// ============================================================
const $ = (id) => document.getElementById(id);
const elSetupScreen = $("setup-screen");
const elChatScreen = $("chat-screen");
const elPersonaPicker = $("persona-picker");
const elTopicInput = $("topic-input");
const elStartBtn = $("start-btn");
const elBackBtn = $("back-btn");
const elTopicDisplay = $("topic-display");
const elActivePersonas = $("active-personas");
const elMessages = $("messages");
const elPersonaButtons = $("persona-buttons");
const elUserInput = $("user-input");
const elSendBtn = $("send-btn");

// ============================================================
// API helpers
// ============================================================
async function api(path, options = {}) {
    const res = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!res.ok) {
        let detail;
        try {
            const data = await res.json();
            detail = data.detail || JSON.stringify(data);
        } catch {
            detail = await res.text();
        }
        throw new Error(detail || `HTTP ${res.status}`);
    }
    return res.json();
}

// ============================================================
// Setup screen logic
// ============================================================
async function loadPersonas() {
    const data = await api("/api/personas");
    state.personas = data.personas;
    renderPersonaPicker();
}

function renderPersonaPicker() {
    elPersonaPicker.innerHTML = "";
    for (const p of state.personas) {
        const btn = document.createElement("button");
        btn.className = "persona-card";
        btn.dataset.id = p.id;
        btn.innerHTML = `
            <span class="persona-card-check">✓</span>
            <div class="persona-card-avatar">${p.avatar}</div>
            <div class="persona-card-name">${p.name}</div>
        `;
        btn.addEventListener("click", () => togglePersona(p.id, btn));
        elPersonaPicker.appendChild(btn);
    }
    // Pre-select all personas by default for a smoother first run
    state.selectedPersonaIds = state.personas.map((p) => p.id);
    elPersonaPicker.querySelectorAll(".persona-card").forEach((c) => {
        c.classList.add("selected");
    });
}

function togglePersona(id, btn) {
    const idx = state.selectedPersonaIds.indexOf(id);
    if (idx >= 0) {
        state.selectedPersonaIds.splice(idx, 1);
        btn.classList.remove("selected");
    } else {
        state.selectedPersonaIds.push(id);
        btn.classList.add("selected");
    }
}

function generateSessionId() {
    return "s_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
}

async function startSession() {
    const topic = elTopicInput.value.trim();
    if (!topic) {
        alert("Please enter a discussion topic.");
        return;
    }
    if (state.selectedPersonaIds.length === 0) {
        alert("Please pick at least one persona.");
        return;
    }

    state.sessionId = generateSessionId();
    state.topic = topic;
    elStartBtn.disabled = true;
    elStartBtn.textContent = "Starting...";

    try {
        await api("/api/session/new", {
            method: "POST",
            body: JSON.stringify({ topic, session_id: state.sessionId }),
        });
        enterChatScreen();
    } catch (err) {
        alert("Failed to start session: " + err.message);
    } finally {
        elStartBtn.disabled = false;
        elStartBtn.textContent = "Start the discussion →";
    }
}

// ============================================================
// Chat screen logic
// ============================================================
function enterChatScreen() {
    elSetupScreen.classList.remove("active");
    elChatScreen.classList.add("active");
    elTopicDisplay.textContent = state.topic;

    // Show active persona avatars in the header
    elActivePersonas.innerHTML = state.selectedPersonaIds
        .map((id) => {
            const p = state.personas.find((x) => x.id === id);
            return `<span title="${p.name}">${p.avatar}</span>`;
        })
        .join("");

    renderPersonaButtons();
    elMessages.innerHTML = "";
    addSystemMessage(`Discussion on "${state.topic}" has begun. Pick a persona to start.`);
    elUserInput.focus();
}

function backToSetup() {
    elChatScreen.classList.remove("active");
    elSetupScreen.classList.add("active");
    elTopicInput.value = "";
    elTopicInput.focus();
}

function renderPersonaButtons() {
    elPersonaButtons.innerHTML = "";

    // Per-persona buttons
    for (const id of state.selectedPersonaIds) {
        const p = state.personas.find((x) => x.id === id);
        const btn = document.createElement("button");
        btn.className = "persona-btn";
        btn.dataset.id = id;
        btn.innerHTML = `${p.avatar} ${p.name}`;
        btn.addEventListener("click", () => personaSpeak(id));
        elPersonaButtons.appendChild(btn);
    }

    // "All speak" button
    if (state.selectedPersonaIds.length > 1) {
        const allBtn = document.createElement("button");
        allBtn.className = "persona-btn all-btn";
        allBtn.textContent = "All speak →";
        allBtn.addEventListener("click", allPersonasSpeak);
        elPersonaButtons.appendChild(allBtn);
    }
}

function setLoading(loading) {
    state.isLoading = loading;
    elPersonaButtons.querySelectorAll("button").forEach((b) => (b.disabled = loading));
    elSendBtn.disabled = loading;
    elUserInput.disabled = loading;
}

// ----- Message rendering -----
function addMessage({ speaker, content, avatar, color, isUser = false }) {
    const div = document.createElement("div");
    div.className = "message" + (isUser ? " user-message" : "");

    const avatarHtml = `<div class="message-avatar">${avatar || (isUser ? "You" : "?")}</div>`;
    const bubbleStyle = color ? `style="--persona-color: ${color};"` : "";

    div.innerHTML = `
        ${avatarHtml}
        <div class="message-body">
            <div class="message-speaker">${escapeHtml(speaker)}</div>
            <div class="message-bubble" ${bubbleStyle}>${escapeHtml(content)}</div>
        </div>
    `;

    elMessages.appendChild(div);
    scrollToBottom();
    return div;
}

function addSystemMessage(text) {
    const div = document.createElement("div");
    div.className = "message system-message";
    div.innerHTML = `<div class="message-body">— ${escapeHtml(text)} —</div>`;
    elMessages.appendChild(div);
    scrollToBottom();
}

function addThinkingIndicator(persona) {
    const div = document.createElement("div");
    div.className = "message thinking-row";
    div.innerHTML = `
        <div class="message-avatar">${persona.avatar}</div>
        <div class="message-body">
            <div class="message-speaker">${escapeHtml(persona.name)}</div>
            <div class="thinking-indicator">
                thinking
                <span class="thinking-dots"><span></span><span></span><span></span></span>
            </div>
        </div>
    `;
    elMessages.appendChild(div);
    scrollToBottom();
    return div;
}

function addErrorMessage(text) {
    const div = document.createElement("div");
    div.className = "message system-message";
    div.innerHTML = `<div class="error-banner">⚠️ ${escapeHtml(text)}</div>`;
    elMessages.appendChild(div);
    scrollToBottom();
}

function scrollToBottom() {
    elMessages.scrollTop = elMessages.scrollHeight;
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// ----- Actions -----
async function sendUserMessage() {
    const content = elUserInput.value.trim();
    if (!content || state.isLoading) return;

    elUserInput.value = "";
    setLoading(true);

    try {
        await api("/api/session/user_message", {
            method: "POST",
            body: JSON.stringify({
                session_id: state.sessionId,
                content: content,
            }),
        });
        addMessage({
            speaker: "You",
            content: content,
            isUser: true,
        });
    } catch (err) {
        addErrorMessage("Failed to send message: " + err.message);
    } finally {
        setLoading(false);
        elUserInput.focus();
    }
}

async function personaSpeak(personaId) {
    if (state.isLoading) return;
    const persona = state.personas.find((p) => p.id === personaId);
    if (!persona) return;

    setLoading(true);
    const thinkingEl = addThinkingIndicator(persona);

    try {
        const reply = await api("/api/session/persona_speak", {
            method: "POST",
            body: JSON.stringify({
                session_id: state.sessionId,
                persona_id: personaId,
            }),
        });
        thinkingEl.remove();
        addMessage({
            speaker: reply.speaker,
            content: reply.content,
            avatar: reply.avatar,
            color: reply.color,
        });
    } catch (err) {
        thinkingEl.remove();
        addErrorMessage(`${persona.name} couldn't reply: ${err.message}`);
    } finally {
        setLoading(false);
    }
}

async function allPersonasSpeak() {
    if (state.isLoading) return;
    for (const id of state.selectedPersonaIds) {
        // Sequential, not parallel — keeps the conversation coherent
        // and respects the rate limit.
        await personaSpeak(id);
    }
}

// ============================================================
// Event listeners
// ============================================================
elStartBtn.addEventListener("click", startSession);
elBackBtn.addEventListener("click", backToSetup);
elSendBtn.addEventListener("click", sendUserMessage);

elUserInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendUserMessage();
});

elTopicInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") startSession();
});

// ============================================================
// Init
// ============================================================
loadPersonas().catch((err) => {
    document.body.innerHTML = `<div style="padding: 2rem; color: #a32d2d;">
        Failed to load personas: ${err.message}<br>
        Make sure the backend is running.
    </div>`;
});
