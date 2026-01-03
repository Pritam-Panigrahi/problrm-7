let recognition;
let isListening = false;
let synthesis = window.speechSynthesis;
let isSpeaking = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    
    const langCode = document.documentElement.lang || 'en-US';
    recognition.lang = getSTTLanguageCode(langCode);
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('userInput').value = transcript;
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isListening = false;
        updateVoiceButton();
    };
    
    recognition.onend = () => {
        isListening = false;
        updateVoiceButton();
    };
}

function getSTTLanguageCode(lang) {
    const languageMap = {
        'hi': 'hi-IN',
        'or': 'or-IN',
        'en': 'en-US'
    };
    return languageMap[lang] || 'en-US';
}

function getTTSLanguageCode(lang) {
    const languageMap = {
        'hi': 'hi-IN',
        'or': 'or-IN',
        'en': 'en-US'
    };
    return languageMap[lang] || 'en-US';
}

function toggleVoiceInput() {
    if (!recognition) {
        alert('Voice input is not supported in your browser. Please use Chrome or Edge.');
        return;
    }
    
    if (isListening) {
        recognition.stop();
        isListening = false;
    } else {
        recognition.start();
        isListening = true;
    }
    
    updateVoiceButton();
}

function updateVoiceButton() {
    const btn = document.getElementById('voiceBtn');
    if (btn) {
        btn.innerHTML = isListening ? '🔴' : '🎤';
        btn.classList.toggle('listening', isListening);
    }
}

function speakText(text, language = 'en') {
    if (!synthesis) {
        console.warn('Text-to-speech is not supported in this browser');
        return;
    }
    
    if (isSpeaking) {
        synthesis.cancel();
    }
    
    const utterance = new SpeechSynthesisUtterance(text);
    const langCode = getTTSLanguageCode(language);
    utterance.lang = langCode;
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    const voices = synthesis.getVoices();
    const preferredVoice = voices.find(voice => voice.lang.startsWith(langCode.split('-')[0]));
    if (preferredVoice) {
        utterance.voice = preferredVoice;
    }
    
    utterance.onstart = () => {
        isSpeaking = true;
        updateSpeakerButton(true);
    };
    
    utterance.onend = () => {
        isSpeaking = false;
        updateSpeakerButton(false);
    };
    
    utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event.error);
        isSpeaking = false;
        updateSpeakerButton(false);
    };
    
    synthesis.speak(utterance);
}

function stopSpeaking() {
    if (synthesis && isSpeaking) {
        synthesis.cancel();
        isSpeaking = false;
        updateSpeakerButton(false);
    }
}

function updateSpeakerButton(speaking) {
    const btn = document.getElementById('speakerBtn');
    if (btn) {
        btn.innerHTML = speaking ? '🔇' : '🔊';
        btn.classList.toggle('speaking', speaking);
        btn.title = speaking ? 'Stop speaking' : 'Read AI response aloud';
    }
}

if (synthesis) {
    synthesis.onvoiceschanged = () => {
        synthesis.getVoices();
    };
}
