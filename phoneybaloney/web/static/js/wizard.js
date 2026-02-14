let currentStep = 1;
const totalSteps = 5;

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.wizard-option input').forEach(input => {
        input.addEventListener('change', (e) => {
            const options = e.target.closest('.wizard-options');
            options.querySelectorAll('.wizard-option').forEach(opt => opt.classList.remove('selected'));
            e.target.closest('.wizard-option').classList.add('selected');
        });
    });

    loadWizardMicrophones();
});

function wizardNext() {
    if (currentStep < totalSteps) {
        document.getElementById(`step-${currentStep}`).classList.remove('active');
        document.querySelector(`.wizard-step[data-step="${currentStep}"]`).classList.remove('active');
        document.querySelector(`.wizard-step[data-step="${currentStep}"]`).classList.add('done');
        currentStep++;
        document.getElementById(`step-${currentStep}`).classList.add('active');
        document.querySelector(`.wizard-step[data-step="${currentStep}"]`).classList.add('active');

        if (currentStep === totalSteps) {
            showWizardSummary();
        }
    }
}

function wizardPrev() {
    if (currentStep > 1) {
        document.getElementById(`step-${currentStep}`).classList.remove('active');
        document.querySelector(`.wizard-step[data-step="${currentStep}"]`).classList.remove('active');
        currentStep--;
        document.getElementById(`step-${currentStep}`).classList.add('active');
        document.querySelector(`.wizard-step[data-step="${currentStep}"]`).classList.add('active');
        document.querySelector(`.wizard-step[data-step="${currentStep}"]`).classList.remove('done');
    }
}

function showWizardSummary() {
    const llm = document.querySelector('input[name="llm"]:checked').value;
    const tts = document.querySelector('input[name="tts"]:checked').value;
    const stt = document.querySelector('input[name="stt"]:checked').value;
    const summary = document.getElementById('wizard-summary');
    summary.innerHTML = `
        <p><strong>LLM:</strong> ${llm}</p>
        <p><strong>TTS:</strong> ${tts}</p>
        <p><strong>STT:</strong> ${stt}</p>
    `;
}

async function wizardTest(type) {
    const resultEl = document.getElementById(`wizard-${type}-result`);
    resultEl.textContent = 'Testing...';
    try {
        const resp = await fetch(`/api/validate/${type}`, { method: 'POST' });
        const data = await resp.json();
        resultEl.textContent = data.ok ? 'Connected!' : data.message;
        resultEl.style.color = data.ok ? 'var(--success)' : 'var(--error)';
    } catch (e) {
        resultEl.textContent = 'Test failed';
        resultEl.style.color = 'var(--error)';
    }
}

async function wizardFinish() {
    const config = {
        llm_provider: document.querySelector('input[name="llm"]:checked').value,
        tts_provider: document.querySelector('input[name="tts"]:checked').value,
        stt_provider: document.querySelector('input[name="stt"]:checked').value,
    };
    try {
        await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
    } catch (e) {}
    window.location.href = '/';
}

async function loadWizardMicrophones() {
    try {
        const resp = await fetch('/api/microphones');
        const mics = await resp.json();
        const select = document.getElementById('wizard-mic');
        if (mics.length) {
            select.innerHTML = mics.map(m => `<option value="${m.index}">${m.name}</option>`).join('');
        } else {
            select.innerHTML = '<option>No microphones detected</option>';
        }
    } catch (e) {
        document.getElementById('wizard-mic').innerHTML = '<option>Error detecting</option>';
    }
}
