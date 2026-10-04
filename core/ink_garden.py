import streamlit.components.v1 as components

def inject_ink_garden():
    """
    Injects the Ink Garden background canvas behind the RootCause UI.
    This component uses a lightweight Canvas2D renderer and injects a <canvas>
    element directly into the parent document to ensure it covers the full viewport
    without interfering with Streamlit's layout or React lifecycle.
    """
    components.html("""
    <script>
    (function() {
        const parent = window.parent.document;
        
        // Prevent multiple injections
        if (parent.getElementById('ink-garden-canvas')) {
            return;
        }

        const config = {
            renderMode: "dither",
            bgMode: "none",
            bgBlur: 12,
            bgOpacity: 90,
            cellSize: 9,
            coverage: 100,
            invert: false,
            styleBlend: "source-over",
            charSet: "standard",
            customChars: "",
            brightness: 0,
            contrast: 158,
            edgeEmphasis: 0,
            density: 20,
            tint: "#3ca6ff",
            tintOpacity: 0,
            overlayBlend: "multiply",
            saturation: 100,
            grayscale: 0,
            blurType: "off",
            blurAmount: 35,
            animated: true,
            animStyle: "pulse",
            animSpeed: { enabled: true, intensity: 100 },
            animIntensity: { enabled: true, intensity: 60 },
            lights: { enabled: false, points: [] },
            mask: { enabled: false }
        };

        const canvas = parent.createElement('canvas');
        canvas.id = 'ink-garden-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.zIndex = '0';
        canvas.style.pointerEvents = 'none';
        
        // We append the canvas to .stApp and make sure it sits at the bottom z-index.
        const stApp = parent.querySelector('.stApp') || parent.body;
        
        // Insert the canvas as the first child of .stApp so it renders above the stApp background
        // but behind all Streamlit UI components. No CSS overrides needed!
        stApp.insertBefore(canvas, stApp.firstChild);

        const ctx = canvas.getContext('2d', { alpha: true });
        
        let width = 0;
        let height = 0;
        let time = 0;
        let animationFrameId = null;

        function resize() {
            width = parent.documentElement.clientWidth;
            height = parent.documentElement.clientHeight;
            const dpr = window.parent.devicePixelRatio || 1;
            canvas.width = width * dpr;
            canvas.height = height * dpr;
            ctx.scale(dpr, dpr);
        }

        window.parent.addEventListener('resize', resize);
        resize();

        function getLuminance(x, y, t) {
            const nx = x * 0.0015;
            const ny = y * 0.0015;
            const nt = t * 0.0008;
            
            const v1 = Math.sin(nx * 4 + nt);
            const v2 = Math.sin(ny * 4 - nt * 0.7);
            const v3 = Math.sin((nx + ny) * 3 + nt * 1.1);
            const v4 = Math.cos(Math.sqrt(nx*nx + ny*ny) * 5 - nt);
            
            let val = (v1 + v2 + v3 + v4) / 4; 
            return (val + 1) / 2;
        }

        const bayer = [
            [ 0, 8, 2,10],
            [12, 4,14, 6],
            [ 3,11, 1, 9],
            [15, 7,13, 5]
        ];

        function loop() {
            if (!parent.getElementById('ink-garden-canvas')) return;

            // Clear frame
            ctx.clearRect(0, 0, width, height);

            const speed = (config.animSpeed.enabled ? config.animSpeed.intensity : 0) / 100;
            time += 16 * speed;

            let globalLumMult = 1.0;
            if (config.animStyle === "pulse") {
                const pulseIntensity = config.animIntensity.enabled ? config.animIntensity.intensity / 100 : 0;
                globalLumMult = 1.0 - pulseIntensity * 0.3 + Math.sin(time * 0.001) * pulseIntensity * 0.3;
            }

            const step = config.cellSize;
            const b = config.brightness / 100;
            const c = config.contrast / 100;

            ctx.fillStyle = config.tint;
            // Opacity is very subtle. bgOpacity 90 might be 0.9, but we scale it down to keep UI readable.
            ctx.globalAlpha = (config.bgOpacity / 100) * 0.15; 
            ctx.beginPath();

            for (let y = 0; y < height; y += step) {
                for (let x = 0; x < width; x += step) {
                    let lum = getLuminance(x, y, time);
                    
                    lum = lum + b;
                    lum = (lum - 0.5) * c + 0.5;
                    lum = Math.max(0, Math.min(1, lum));
                    
                    lum *= globalLumMult;
                    lum *= (config.density / 20);

                    const col = Math.floor(x / step);
                    const row = Math.floor(y / step);
                    const threshold = (bayer[row % 4][col % 4] + 0.5) / 16;

                    if (config.renderMode === "dither" && lum > threshold) {
                        ctx.rect(x + step * 0.25, y + step * 0.25, step * 0.5, step * 0.5);
                    }
                }
            }
            
            ctx.fill();

            animationFrameId = requestAnimationFrame(loop);
        }

        loop();
        
    })();
    </script>
    """, height=0)
