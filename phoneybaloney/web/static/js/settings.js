document.addEventListener('DOMContentLoaded', () => {
    loadCurrentConfig();
    loadMicrophones();

    document.getElementById('llm-provider').addEventListener('change', (e) => toggleProviderConfig('llm', e.target.value));
    document.getElementById('tts-provider').addEventListener('change', (e) => toggleProviderConfig('tts', e.target.value));
    document.getElementById('stt-provider').addEventListener('change', (e) => toggleProviderConfig('stt', e.target.value));
});

function toggleProviderConfig(type, provider) {
    const container = document.getElementById(`${type}-config`);
    container.querySelectorAll('.config-group').forEach(g => g.style.display = 'none');
    const target = container.querySelector(`.config-${provider}`);
    if (target) target.style.display = 'block';
}

async function loadCurrentConfig() {
    try {
        const resp = await fetch('/api/config');
        const config = await resp.json();

        document.getElementById('llm-provider').value = config.llm_provider || 'ollama';
        document.getElementById('tts-provider').value = config.tts_provider || 'pyttsx3';
        document.getElementById('stt-provider').value = config.stt_provider || 'whisper_local';

        toggleProviderConfig('llm', config.llm_provider || 'ollama');
        toggleProviderConfig('tts', config.tts_provider || 'pyttsx3');
        toggleProviderConfig('stt', config.stt_provider || 'whisper_local');

        if (config.ollama) {
            document.getElementById('ollama-model').value = config.ollama.model || 'llama3';
            document.getElementById('ollama-url').value = config.ollama.url || 'http://localhost:11434';
        }
        if (config.openai) {
            document.getElementById('openai-api-key').value = config.openai.api_key || '';
            document.getElementById('openai-model').value = config.openai.model || 'gpt-4o';
        }
        if (config.claude) {
            document.getElementById('claude-api-key').value = config.claude.api_key || '';
            document.getElementById('claude-model').value = config.claude.model || 'claude-sonnet-4-5-20250929';
        }
        if (config.pyttsx3) {
            document.getElementById('pyttsx3-rate').value = config.pyttsx3.rate || 175;
        }
        if (config.whisper_local) {
            document.getElementById('whisper-model').value = config.whisper_local.model || 'base';
        }
    } catch (e) {
        console.error('Failed to load config:', e);
    }
}

async function loadMicrophones() {
    try {
        const resp = await fetch('/api/microphones');
        const mics = await resp.json();
        const select = document.getElementById('microphone-select');
        select.innerHTML = mics.length
            ? mics.map(m => `<option value="${m.index}">${m.name}</option>`).join('')
            : '<option>No microphones detected</option>';
    } catch (e) {
        document.getElementById('microphone-select').innerHTML = '<option>Error loading microphones</option>';
    }
}

async function testProvider(type) {
    const resultEl = document.getElementById(`${type}-test-result`);
    resultEl.textContent = 'Testing...';
    resultEl.className = 'test-result';
    try {
        const resp = await fetch(`/api/validate/${type}`, { method: 'POST' });
        const data = await resp.json();
        resultEl.textContent = data.message;
        resultEl.className = `test-result ${data.ok ? 'ok' : 'error'}`;
    } catch (e) {
        resultEl.textContent = 'Test failed';
        resultEl.className = 'test-result error';
    }
}

async function loadVoices() {
    const btn = document.getElementById('load-voices-btn');
    const select = document.getElementById('voice-list');
    btn.textContent = 'Loading...';
    try {
        const resp = await fetch('/api/voices');
        const voices = await resp.json();
        if (voices.length) {
            select.innerHTML = voices.map(v => `<option value="${v.id}">${v.name} (${v.gender || 'unknown'})</option>`).join('');
            select.style.display = 'block';
        } else {
            select.innerHTML = '<option>No voices available</option>';
            select.style.display = 'block';
        }
    } catch (e) {
        select.innerHTML = '<option>Error loading voices</option>';
        select.style.display = 'block';
    }
    btn.textContent = 'Load Voices';
}

async function saveSettings() {
    const resultEl = document.getElementById('save-result');
    resultEl.textContent = 'Saving...';
    const config = {
        llm_provider: document.getElementById('llm-provider').value,
        tts_provider: document.getElementById('tts-provider').value,
        stt_provider: document.getElementById('stt-provider').value,
        ollama: {
            model: document.getElementById('ollama-model').value,
            url: document.getElementById('ollama-url').value,
        },
        openai: {
            api_key: document.getElementById('openai-api-key').value,
            model: document.getElementById('openai-model').value,
        },
        claude: {
            api_key: document.getElementById('claude-api-key').value,
            model: document.getElementById('claude-model').value,
        },
        pyttsx3: { rate: parseInt(document.getElementById('pyttsx3-rate').value) },
        whisper_local: { model: document.getElementById('whisper-model').value },
    };
    try {
        const resp = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
        const data = await resp.json();
        resultEl.textContent = data.message || 'Saved!';
        resultEl.style.color = 'var(--success)';
    } catch (e) {
        resultEl.textContent = 'Save failed';
        resultEl.style.color = 'var(--error)';
    }
}
