let ws = null;
let muted = false;

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const scenario = params.get('scenario');
    if (!scenario) {
        document.getElementById('scenario-name').textContent = 'Error: No scenario specified';
        return;
    }

    if (!localStorage.getItem('phoneybaloney_howto_dismissed')) {
        document.getElementById('howto-overlay').style.display = 'flex';
    }

    connectWebSocket(scenario);
});

function connectWebSocket(scenario) {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${location.host}/ws/session?scenario=${scenario}`);

    ws.onopen = () => {
        updateStatus('Connected', 'listening');
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
            case 'status':
                handleStatus(msg);
                break;
            case 'transcript':
                addTranscriptEntry(msg.speaker, msg.text, msg.timestamp);
                break;
            case 'scenario_info':
                document.getElementById('scenario-name').textContent = msg.company;
                document.getElementById('scenario-objective').textContent = `Objective: ${msg.objective}`;
                if (document.getElementById('overlay-objective')) {
                    document.getElementById('overlay-objective').textContent = msg.objective;
                }
                break;
            case 'audio':
                playBase64Audio(msg.data);
                break;
            case 'error':
                addSystemMessage(msg.message);
                break;
            case 'call_ended':
                updateStatus('Call ended', '');
                addSystemMessage('Call has been disconnected. Transcript saved.');
                disableControls();
                break;
        }
    };

    ws.onclose = () => {
        updateStatus('Disconnected', '');
    };

    ws.onerror = () => {
        updateStatus('Connection error', '');
    };
}

function handleStatus(msg) {
    const statusMap = {
        listening: 'Listening...',
        thinking: `${msg.character || 'Character'} is thinking...`,
        speaking: `${msg.character || 'Character'} is speaking...`,
    };
    updateStatus(statusMap[msg.status] || msg.status, msg.status);
}

function updateStatus(text, className) {
    const el = document.getElementById('call-status');
    el.textContent = text;
    el.className = `status-indicator ${className}`;
}

function addTranscriptEntry(speaker, text, timestamp) {
    const transcript = document.getElementById('transcript');
    const welcome = transcript.querySelector('.transcript-welcome');
    if (welcome) welcome.remove();

    const entry = document.createElement('div');
    entry.className = 'transcript-entry';
    const isUser = speaker === 'You';
    entry.innerHTML = `
        <span class="transcript-speaker ${isUser ? 'user' : ''}">${speaker}</span>
        ${timestamp ? `<span class="transcript-time">${timestamp}</span>` : ''}
        <div class="transcript-text">${text}</div>
    `;
    transcript.appendChild(entry);
    transcript.scrollTop = transcript.scrollHeight;
}

function addSystemMessage(text) {
    addTranscriptEntry('System', text);
}

function playBase64Audio(base64Data) {
    const volume = document.getElementById('volume-slider').value / 100;
    const audio = new Audio('data:audio/wav;base64,' + base64Data);
    audio.volume = volume;
    audio.play().catch(() => {});
}

function toggleMute() {
    muted = !muted;
    const btn = document.getElementById('mute-btn');
    const icon = document.getElementById('mute-icon');
    if (muted) {
        icon.innerHTML = '&#128263;';
        btn.innerHTML = icon.outerHTML + ' Unmute';
        if (ws) ws.send(JSON.stringify({ type: 'mute', muted: true }));
    } else {
        icon.innerHTML = '&#128266;';
        btn.innerHTML = icon.outerHTML + ' Mute';
        if (ws) ws.send(JSON.stringify({ type: 'mute', muted: false }));
    }
}

function dialExtension() {
    const input = document.getElementById('dial-input');
    const ext = input.value.trim();
    if (ext && ws) {
        ws.send(JSON.stringify({ type: 'dial', extension: ext }));
        input.value = '';
    }
}

function endCall() {
    if (ws) {
        ws.send(JSON.stringify({ type: 'end_call' }));
    }
}

function disableControls() {
    document.getElementById('mute-btn').disabled = true;
    document.getElementById('end-call-btn').disabled = true;
    document.querySelector('.dial-group button').disabled = true;
}

function dismissOverlay() {
    document.getElementById('howto-overlay').style.display = 'none';
    if (document.getElementById('dont-show-again').checked) {
        localStorage.setItem('phoneybaloney_howto_dismissed', 'true');
    }
}
