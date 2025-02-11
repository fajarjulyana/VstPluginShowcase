document.addEventListener('DOMContentLoaded', function() {
    let synth = new Tone.Synth().toDestination();
    let isPlaying = false;
    const playButton = document.getElementById('playButton');
    const effectSlider = document.getElementById('effectSlider');
    
    // Initialize audio context
    const startAudio = async () => {
        await Tone.start();
        console.log('Audio is ready');
    };

    // Create a basic synthesizer pattern
    const pattern = new Tone.Pattern((time, note) => {
        synth.triggerAttackRelease(note, '8n', time);
    }, ['C4', 'E4', 'G4', 'B4']);

    // Effect processing
    const chorus = new Tone.Chorus(4, 2.5, 0.5).toDestination();
    synth.connect(chorus);

    // Play button handler
    playButton.addEventListener('click', async () => {
        await startAudio();
        if (!isPlaying) {
            playButton.innerHTML = '<i class="fas fa-pause"></i>';
            pattern.start(0);
            Tone.Transport.start();
        } else {
            playButton.innerHTML = '<i class="fas fa-play"></i>';
            Tone.Transport.stop();
            pattern.stop();
        }
        isPlaying = !isPlaying;
    });

    // Effect slider handler
    effectSlider.addEventListener('input', (e) => {
        const value = e.target.value;
        chorus.wet.value = value / 100;
    });

    // Create visualization
    const waveform = document.getElementById('waveform');
    const canvas = document.createElement('canvas');
    waveform.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    function drawWaveform() {
        const width = waveform.offsetWidth;
        const height = waveform.offsetHeight;
        canvas.width = width;
        canvas.height = height;

        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, width, height);

        if (isPlaying) {
            ctx.beginPath();
            ctx.strokeStyle = '#00ffbb';
            ctx.lineWidth = 2;

            for (let i = 0; i < width; i++) {
                const x = i;
                const y = height / 2 + Math.sin(i * 0.05 + Date.now() * 0.01) * 50;
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
        }

        requestAnimationFrame(drawWaveform);
    }

    drawWaveform();
});
