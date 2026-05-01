/**
 * Audio Recorder Utility for VoxCPM WebUI
 * Provides audio recording capabilities using MediaRecorder API
 */
class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
    }

    /**
     * Start recording audio from microphone
     * @returns {Promise<void>}
     */
    async start() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(this.stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                // Clean up stream when stopped
                if (this.stream) {
                    this.stream.getTracks().forEach(track => track.stop());
                }
            };

            this.mediaRecorder.start();
        } catch (error) {
            throw new Error(`Failed to start audio recording: ${error.message}`);
        }
    }

    /**
     * Stop recording and return audio blob
     * @returns {Promise<Blob>} - Recorded audio as WAV blob
     */
    async stop() {
        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder) {
                reject(new Error('No recording in progress'));
                return;
            }

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                resolve(audioBlob);
            };

            this.mediaRecorder.onerror = (event) => {
                reject(new Error(`Recording error: ${event.error}`));
            };

            this.mediaRecorder.stop();
        });
    }

    /**
     * Check if audio recording is available in browser
     * @returns {boolean}
     */
    static isAvailable() {
        return !!(
            navigator.mediaDevices &&
            navigator.mediaDevices.getUserMedia &&
            window.MediaRecorder
        );
    }

    /**
     * Release resources
     */
    async cleanup() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            await this.stop();
        }
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
}

// Export for use in other modules
window.AudioRecorder = AudioRecorder;