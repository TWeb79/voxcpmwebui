/**
 * Main Application Logic for VoxCPM WebUI
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize API client with configurable base URL
    const apiBaseURL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://' + window.location.hostname + ':8138'
        : window.location.protocol + '//' + window.location.hostname + ':8138';
    const api = new APIClient(apiBaseURL);
    
    // DOM elements
    const tabs = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const forms = {
        tts: document.getElementById('tts-form'),
        voiceDesign: document.getElementById('voice-design-form'),
        voiceClone: document.getElementById('voice-clone-form'),
        ultimateClone: document.getElementById('ultimate-clone-form')
    };
    
    const resultSection = document.querySelector('.result-section');
    const audioPlayer = document.getElementById('result-audio');
    const downloadBtn = document.getElementById('download-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');
    
    // Current audio blob for download
    let currentAudioBlob = null;
    
    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and panes
            tabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Show corresponding tab pane
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
    
    // Form submissions
    forms.tts.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleTTSGenerate(e.target);
    });
    
    forms.voiceDesign.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleVoiceDesignGenerate(e.target);
    });
    
    forms.voiceClone.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleVoiceCloneGenerate(e.target);
    });
    
    forms.ultimateClone.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleUltimateCloneGenerate(e.target);
    });
    
    // Download button
    downloadBtn.addEventListener('click', () => {
        if (currentAudioBlob) {
            const url = window.URL.createObjectURL(currentAudioBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'voxcpm_output.wav';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
    });
    
    // Helper functions
    async function handleTTSGenerate(form) {
        await handleGenerate(
            () => {
                const params = {
                    text: form.tts_text.value.trim(),
                    cfg_value: parseFloat(form.tts_cfg.value),
                    inference_timesteps: parseInt(form.tts_steps.value)
                };
                return api.generateTTS(params);
            },
            'TTS generation'
        );
    }
    
    async function handleVoiceDesignGenerate(form) {
        await handleGenerate(
            () => {
                const params = {
                    voice_description: form.voice_description.value.trim(),
                    text: form.voice_design_text.value.trim(),
                    cfg_value: parseFloat(form.voice_design_cfg.value),
                    inference_timesteps: parseInt(form.voice_design_steps.value)
                };
                return api.generateVoiceDesign(params);
            },
            'Voice design generation'
        );
    }
    
    async function handleVoiceCloneGenerate(form) {
        await handleGenerate(
            () => {
                const params = {
                    text: form.clone_text.value.trim(),
                    reference_audio: form.reference_audio.files[0],
                    cfg_value: parseFloat(form.clone_cfg.value),
                    inference_timesteps: parseInt(form.clone_steps.value)
                };
                return api.generateVoiceClone(params);
            },
            'Voice cloning'
        );
    }
    
    async function handleUltimateCloneGenerate(form) {
        await handleGenerate(
            () => {
                const params = {
                    text: form.ultimate_text.value.trim(),
                    prompt_audio: form.prompt_audio.files[0] || null,
                    prompt_text: form.prompt_text.value.trim() || null,
                    reference_audio: form.reference_audio_ultimate.files[0] || null
                };
                return api.generateUltimateClone(params);
            },
            'Ultimate cloning'
        );
    }
    
    async function handleGenerate(generateFunc, operationName) {
        // Validate inputs
        if (!validateInputs()) {
            return;
        }
        
        // Show loading state
        setLoading(true);
        clearResult();
        
        try {
            // Generate audio
            const audioBlob = await generateFunc();
            
            // Handle result
            currentAudioBlob = audioBlob;
            const url = window.URL.createObjectURL(audioBlob);
            audioPlayer.src = url;
            downloadBtn.disabled = false;
            
            // Show success message
            showMessage(`✅ ${operationName} completed successfully!`, 'success');
            
        } catch (error) {
            // Show error
            showMessage(`❌ ${operationName} failed: ${error.message}`, 'error');
            console.error(error);
        } finally {
            // Hide loading state
            setLoading(false);
        }
    }
    
    function validateInputs() {
        // Clear previous errors
        errorMessage.classList.add('hidden');
        errorMessage.textContent = '';
        
        // Get active tab
        const activeTab = document.querySelector('.tab-button.active');
        const tabId = activeTab.getAttribute('data-tab');
        
        let isValid = true;
        let errorMsg = '';
        
        switch (tabId) {
            case 'tts':
                if (!forms.tts.tts_text.value.trim()) {
                    errorMsg = 'Please enter text to synthesize';
                    isValid = false;
                }
                break;
                
            case 'voice-design':
                if (!forms.voiceDesign.voice_description.value.trim()) {
                    errorMsg = 'Please enter a voice description';
                    isValid = false;
                } else if (!forms.voiceDesign.voice_design_text.value.trim()) {
                    errorMsg = 'Please enter text to synthesize';
                    isValid = false;
                }
                break;
                
            case 'voice-clone':
                if (!forms.voiceClone.clone_text.value.trim()) {
                    errorMsg = 'Please enter text to synthesize';
                    isValid = false;
                } else if (!forms.voiceClone.reference_audio.files[0]) {
                    errorMsg = 'Please select a reference audio file';
                    isValid = false;
                }
                break;
                
            case 'ultimate-clone':
                if (!forms.ultimateClone.ultimate_text.value.trim()) {
                    errorMsg = 'Please enter text to synthesize';
                    isValid = false;
                }
                // Note: prompt audio and reference audio are optional for ultimate cloning
                break;
        }
        
        if (!isValid) {
            showMessage(errorMsg, 'error');
        }
        
        return isValid;
    }
    
    function setLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.classList.remove('hidden');
            resultSection.style.opacity = '0.5';
            // Disable all submit buttons
            document.querySelectorAll('button[type="submit"]').forEach(btn => {
                btn.disabled = true;
            });
        } else {
            loadingIndicator.classList.add('hidden');
            resultSection.style.opacity = '1';
            // Enable all submit buttons
            document.querySelectorAll('button[type="submit"]').forEach(btn => {
                btn.disabled = false;
            });
        }
    }
    
    function clearResult() {
        if (audioPlayer.src) {
            window.URL.revokeObjectURL(audioPlayer.src);
        }
        audioPlayer.src = '';
        audioPlayer.load();
        downloadBtn.disabled = true;
        currentAudioBlob = null;
        errorMessage.classList.add('hidden');
    }
    
    function showMessage(message, type) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');

        if (type === 'success') {
            errorMessage.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
            errorMessage.style.borderColor = 'var(--success-color)';
            errorMessage.style.color = 'var(--success-color)';
            setTimeout(() => {
                errorMessage.classList.add('hidden');
                errorMessage.style.backgroundColor = '';
                errorMessage.style.borderColor = '';
                errorMessage.style.color = '';
            }, 3000);
        } else {
            errorMessage.style.backgroundColor = '';
            errorMessage.style.borderColor = '';
            errorMessage.style.color = '';
        }
    }
    
    // Initial health check
    async function checkInitialHealth() {
        try {
            const health = await api.checkHealth();
            console.log('API Health:', health);
        } catch (error) {
            console.warn('API health check failed:', error.message);
            showMessage('⚠️ Backend API may not be available. Please ensure the server is running.', 'error');
        }
    }
    
    // Run initial health check
    checkInitialHealth();
});