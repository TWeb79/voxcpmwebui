/**
 * API Client for VoxCPM WebUI
 * Handles communication with the backend API
 */
class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    /**
     * Generate speech from text
     * @param {Object} params - TTS parameters
     * @returns {Promise<Blob>} - Audio data as Blob
     */
    async generateTTS(params) {
        try {
            const formData = new FormData();
            formData.append('text', params.text);
            formData.append('cfg_value', params.cfg_value);
            formData.append('inference_timesteps', params.inference_timesteps);

            const response = await fetch(`${this.baseURL}/api/v1/tts/generate`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'TTS generation failed');
            }

            return await response.blob();
        } catch (error) {
            throw new Error(`TTS Error: ${error.message}`);
        }
    }

    /**
     * Generate voice using voice design
     * @param {Object} params - Voice design parameters
     * @returns {Promise<Blob>} - Audio data as Blob
     */
    async generateVoiceDesign(params) {
        try {
            const formData = new FormData();
            formData.append('voice_description', params.voice_description);
            formData.append('text', params.text);
            formData.append('cfg_value', params.cfg_value);
            formData.append('inference_timesteps', params.inference_timesteps);

            const response = await fetch(`${this.baseURL}/api/v1/voice-design/generate`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Voice design generation failed');
            }

            return await response.blob();
        } catch (error) {
            throw new Error(`Voice Design Error: ${error.message}`);
        }
    }

    /**
     * Generate speech using voice cloning
     * @param {Object} params - Voice cloning parameters
     * @returns {Promise<Blob>} - Audio data as Blob
     */
    async generateVoiceClone(params) {
        try {
            const formData = new FormData();
            formData.append('text', params.text);
            formData.append('reference_audio', params.reference_audio);
            formData.append('cfg_value', params.cfg_value);
            formData.append('inference_timesteps', params.inference_timesteps);

            const response = await fetch(`${this.baseURL}/api/v1/voice-clone/generate`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Voice cloning failed');
            }

            return await response.blob();
        } catch (error) {
            throw new Error(`Voice Clone Error: ${error.message}`);
        }
    }

    /**
     * Generate speech using ultimate cloning
     * @param {Object} params - Ultimate cloning parameters
     * @returns {Promise<Blob>} - Audio data as Blob
     */
    async generateUltimateClone(params) {
        try {
            const formData = new FormData();
            formData.append('text', params.text);
            
            if (params.prompt_audio) {
                formData.append('prompt_audio', params.prompt_audio);
            }
            
            if (params.prompt_text) {
                formData.append('prompt_text', params.prompt_text);
            }
            
            if (params.reference_audio) {
                formData.append('reference_audio', params.reference_audio);
            }

            const response = await fetch(`${this.baseURL}/api/v1/ultimate-clone/generate`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ultimate cloning failed');
            }

            return await response.blob();
        } catch (error) {
            throw new Error(`Ultimate Clone Error: ${error.message}`);
        }
    }

    /**
     * Check API health
     * @returns {Promise<Object>} - Health status
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/health`);
            if (!response.ok) {
                throw new Error('Health check failed');
            }
            return await response.json();
        } catch (error) {
            throw new Error(`Health Check Error: ${error.message}`);
        }
    }
}

// Export for use in other modules
window.APIClient = APIClient;