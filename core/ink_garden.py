import streamlit.components.v1 as components

def inject_ink_garden():
    """
    Injects the Flashlight WebGL shader background behind the RootCause UI.
    Replaces the previous ASCII dither with the exact WebGL shader provided.
    """
    components.html("""
    <script>
    (function() {
        const parent = window.parent.document;
        
        // Prevent multiple injections
        if (parent.getElementById('flashlight-bg-canvas')) {
            return;
        }

        const canvas = parent.createElement('canvas');
        canvas.id = 'flashlight-bg-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.zIndex = '0';
        canvas.style.pointerEvents = 'none';
        
        const stApp = parent.querySelector('.stApp') || parent.body;
        stApp.insertBefore(canvas, stApp.firstChild);

        const gl = canvas.getContext("webgl", { antialias: false, alpha: false });
        if (!gl) return;

        const VERT = `
        attribute vec2 a_position;
        void main() {
          gl_Position = vec4(a_position, 0.0, 1.0);
        }
        `;

        const FRAG = `
        #ifdef GL_FRAGMENT_PRECISION_HIGH
        precision highp float;
        #else
        precision mediump float;
        #endif

        uniform vec3 u_colors[8];
        uniform vec4 u_scene;      // resolution.xy, time, colour count
        uniform vec4 u_shape;      // scale, intensity, paramA, warp
        uniform vec4 u_surface;    // detail, contrast, brightness, saturation
        uniform vec4 u_finish;     // hue, vignette, blur, grain
        uniform vec4 u_transform;  // seed, rotation, drift, OKLab toggle
        uniform vec4 u_space;      // offset.xy, pointer.xy
        uniform vec4 u_cursor;

        #define u_resolution u_scene.xy
        #define u_time u_scene.z
        #define u_colorCount u_scene.w
        #define u_scale u_shape.x
        #define u_intensity u_shape.y
        #define u_paramA u_shape.z
        #define u_warp u_shape.w
        #define u_detail u_surface.x
        #define u_contrast u_surface.y
        #define u_brightness u_surface.z
        #define u_saturation u_surface.w
        #define u_hue u_finish.x
        #define u_vignette u_finish.y
        #define u_blur u_finish.z
        #define u_grain u_finish.w
        #ifdef GL_FRAGMENT_PRECISION_HIGH
        #define u_seed u_transform.x
        #else
        #define u_seed mod(u_transform.x, 31.0)
        #endif
        #define u_rotate u_transform.y
        #define u_drift u_transform.z
        #define u_oklab u_transform.w
        #define u_offset u_space.xy
        #define u_mouse u_space.zw
        #define u_cursorPresence u_cursor.x
        #define u_cursorEffect u_cursor.y
        #define u_cursorStrength u_cursor.z
        #define u_cursorRadius u_cursor.w

        float hash21(vec2 p) {
        #ifndef GL_FRAGMENT_PRECISION_HIGH
          p = mod(p, 31.0);
        #endif
          p = fract(p * vec2(234.34, 435.345));
          p += dot(p, p + 34.23);
          return fract(p.x * p.y);
        }

        float grainHash(vec2 p) {
          vec3 p3 = fract(vec3(p.xyx) * 0.1031);
          p3 += dot(p3, p3.yzx + 33.33);
          return fract((p3.x + p3.y) * p3.z);
        }

        vec2 hash22(vec2 p) {
        #ifndef GL_FRAGMENT_PRECISION_HIGH
          p = mod(p, 31.0);
        #endif
          float n = sin(dot(p, vec2(41.0, 289.0)));
          return fract(vec2(15731.743, 7892.321) * n);
        }

        float noise(vec2 p) {
          vec2 i = floor(p);
          vec2 f = fract(p);
          vec2 u = f * f * (3.0 - 2.0 * f);
          return mix(
            mix(hash21(i), hash21(i + vec2(1.0, 0.0)), u.x),
            mix(hash21(i + vec2(0.0, 1.0)), hash21(i + vec2(1.0, 1.0)), u.x),
            u.y);
        }

        float fbm(vec2 p) {
          float v = 0.0;
          float a = 0.5;
          for (int i = 0; i < 5; i++) {
            v += a * noise(p);
            p = p * 2.03 + vec2(17.0, 9.2);
            a *= 0.5;
          }
          return v;
        }

        vec3 srgbToLinear(vec3 c) {
          return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)),
            step(0.04045, c));
        }
        vec3 linearToSrgb(vec3 c) {
          return mix(c * 12.92, 1.055 * pow(max(c, vec3(0.0)), vec3(1.0 / 2.4)) - 0.055,
            step(0.0031308, c));
        }
        vec3 linToOklab(vec3 c) {
          float l = 0.4122214708 * c.r + 0.5363325363 * c.g + 0.0514459929 * c.b;
          float m = 0.2119034982 * c.r + 0.6806995451 * c.g + 0.1073969566 * c.b;
          float s = 0.0883024619 * c.r + 0.2817188376 * c.g + 0.6299787005 * c.b;
          l = pow(max(l, 0.0), 1.0 / 3.0);
          m = pow(max(m, 0.0), 1.0 / 3.0);
          s = pow(max(s, 0.0), 1.0 / 3.0);
          return vec3(
            0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s);
        }
        vec3 oklabToLin(vec3 c) {
          float l = c.x + 0.3963377774 * c.y + 0.2158037573 * c.z;
          float m = c.x - 0.1055613458 * c.y - 0.0638541728 * c.z;
          float s = c.x - 0.0894841775 * c.y - 1.2914855480 * c.z;
          l = l * l * l; m = m * m * m; s = s * s * s;
          return vec3(
            4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s);
        }
        vec3 mixColour(vec3 a, vec3 b, float t) {
          if (u_oklab > 0.5) {
            vec3 la = linToOklab(srgbToLinear(a));
            vec3 lb = linToOklab(srgbToLinear(b));
            return clamp(linearToSrgb(oklabToLin(mix(la, lb, t))), 0.0, 1.0);
          }
          return mix(a, b, t);
        }

        vec3 palette(float x) {
          float n = max(u_colorCount - 1.0, 1.0);
          float f = clamp(x, 0.0, 1.0) * n;
          vec3 col = u_colors[0];
          for (int i = 0; i < 7; i++) {
            if (float(i) < n)
              col = mixColour(col, u_colors[i + 1],
                smoothstep(0.0, 1.0, clamp(f - float(i), 0.0, 1.0)));
          }
          return col;
        }

        vec3 hueRotate(vec3 col, float a) {
          const mat3 toYIQ = mat3(0.299, 0.596, 0.211,
                                  0.587, -0.274, -0.523,
                                  0.114, -0.322, 0.312);
          const mat3 toRGB = mat3(1.0, 1.0, 1.0,
                                  0.956, -0.272, -1.106,
                                  0.621, -0.647, 1.703);
          vec3 yiq = toYIQ * col;
          float ca = cos(a), sa = sin(a);
          yiq = vec3(yiq.x, yiq.y * ca - yiq.z * sa, yiq.y * sa + yiq.z * ca);
          return toRGB * yiq;
        }

        vec3 shade(vec2 uv, vec2 p, float t) {
          vec3 acc = u_colors[0] * 0.15;
          float total = 0.15;
          for (int i = 0; i < 8; i++) {
            if (float(i) >= u_colorCount) break;
            float fi = float(i);
            vec2 c = vec2(
              sin(t * (0.21 + fi * 0.071) + fi * 2.4 + u_seed),
              cos(t * (0.17 + fi * 0.093) + fi * 1.7)) * (0.45 + u_intensity * 0.35);
            float w = exp(-dot(p - c, p - c) * 6.0);
            acc += u_colors[i] * w;
            total += w;
          }
          return acc / total;
        }

        void main() {
          vec2 uv = gl_FragCoord.xy / u_resolution.xy;
          vec2 screenUv = uv;
          vec2 p = (gl_FragCoord.xy - 0.5 * u_resolution.xy)
            / min(u_resolution.x, u_resolution.y);
          float cursorMask = 0.0;

          if (u_cursorPresence > 0.001) {
            vec2 cursor = (0.5 * u_mouse * u_resolution.xy)
              / min(u_resolution.x, u_resolution.y);
            vec2 cursorDelta = p - cursor;
            if (u_cursorEffect < 0.5) {
              p += cursor * u_cursorPresence * u_cursorStrength * 0.55;
            } else {
              float cursorDistance = length(cursorDelta);
              vec2 cursorDirection = cursorDelta / max(cursorDistance, 0.0001);
              cursorMask = u_cursorPresence
                * (1.0 - smoothstep(0.0, u_cursorRadius, cursorDistance));
              if (u_cursorEffect < 1.5) {
                p -= cursorDirection * cursorMask * u_cursorStrength * 0.24;
              } else if (u_cursorEffect < 2.5) {
                float cursorAngle = cursorMask * u_cursorStrength * 2.2;
                float cc = cos(cursorAngle), cs = sin(cursorAngle);
                p = cursor + mat2(cc, -cs, cs, cc) * cursorDelta;
              } else if (u_cursorEffect < 3.5) {
                float ripple = sin(
                  cursorDistance / max(u_cursorRadius, 0.001) * 18.0 - u_time * 5.0);
                p -= cursorDirection * ripple * cursorMask * u_cursorStrength * 0.07;
              }
            }
          }

          uv = p * min(u_resolution.x, u_resolution.y) / u_resolution.xy + 0.5;
          p *= u_scale;
          if (abs(u_rotate) > 0.0001) {
            float cr = cos(u_rotate), sr = sin(u_rotate);
            p = mat2(cr, -sr, sr, cr) * p;
          }
          p += u_offset;
          if (u_drift > 0.0001)
            p += u_drift * vec2(sin(u_time * 0.31), cos(u_time * 0.23));
          if (u_warp > 0.0) {
            p += u_warp * (vec2(
              fbm(p * u_detail + u_seed),
              fbm(p * u_detail + vec2(5.2, 1.3))) - 0.5);
          }
          
          vec3 col;
          if (u_blur > 0.0) {
            float e = u_blur;
            float pe = e * u_scale;
            vec2 uvE = vec2(e) * min(u_resolution.x, u_resolution.y) / u_resolution.xy;
            col  = shade(uv, p, u_time) * 0.36;
            col += shade(uv + vec2(uvE.x, 0.0), p + vec2(pe, 0.0), u_time) * 0.16;
            col += shade(uv - vec2(uvE.x, 0.0), p - vec2(pe, 0.0), u_time) * 0.16;
            col += shade(uv + vec2(0.0, uvE.y), p + vec2(0.0, pe), u_time) * 0.16;
            col += shade(uv - vec2(0.0, uvE.y), p - vec2(0.0, pe), u_time) * 0.16;
          } else {
            col = shade(uv, p, u_time);
          }
          
          if (abs(u_contrast - 1.0) > 0.0001)
            col = (col - 0.5) * u_contrast + 0.5;
          if (abs(u_saturation - 1.0) > 0.0001) {
            float luma = dot(col, vec3(0.299, 0.587, 0.114));
            col = mix(vec3(luma), col, u_saturation);
          }
          if (abs(u_hue) > 0.0001)
            col = hueRotate(col, u_hue);
          if (abs(u_brightness) > 0.0001)
            col += u_brightness;
          if (u_vignette > 0.0001) {
            float vd = length(screenUv - 0.5) * 1.41421356;
            col *= 1.0 - u_vignette * smoothstep(0.35, 1.0, vd);
          }
          if (u_cursorPresence > 0.001 && u_cursorEffect > 3.5)
            col += (vec3(0.18) + col * 0.12) * cursorMask * u_cursorStrength;
          if (u_grain > 0.0001)
            col += (grainHash(
              gl_FragCoord.xy + vec2(u_seed * 17.0, u_seed * 31.0)) - 0.5) * u_grain;
          gl_FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
        }
        `;

        function hexToRgb(hex) {
          let h = hex.trim().replace(/^#/, "");
          if (h.length === 3) h = h.replace(/./g, "$&$&");
          const n = /^[0-9a-f]{6}$/i.test(h) ? parseInt(h, 16) : 0;
          return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
        }

        function compile(gl, vert, frag) {
          const program = gl.createProgram();
          if (!program) return null;
          const shaders = [
            [gl.VERTEX_SHADER, vert],
            [gl.FRAGMENT_SHADER, frag],
          ];
          for (let i = 0; i < shaders.length; i++) {
            const type = shaders[i][0];
            const source = shaders[i][1];
            const shader = gl.createShader(type);
            if (!shader) return null;
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
              console.warn(gl.getShaderInfoLog(shader));
              return null;
            }
            gl.attachShader(program, shader);
            gl.deleteShader(shader);
          }
          gl.linkProgram(program);
          if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.warn(gl.getProgramInfoLog(program));
            return null;
          }
          return program;
        }

        const program = compile(gl, VERT, FRAG);
        if (!program) return;

        const triangleBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, triangleBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
        const position = gl.getAttribLocation(program, "a_position");
        gl.enableVertexAttribArray(position);
        gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
        gl.useProgram(program);

        const u = (name) => gl.getUniformLocation(program, name);
        const loc = {
          colors: u("u_colors"),
          scene: u("u_scene"),
          shape: u("u_shape"),
          surface: u("u_surface"),
          finish: u("u_finish"),
          transform: u("u_transform"),
          space: u("u_space"),
          cursor: u("u_cursor"),
        };
        const colorData = new Float32Array(24);

        const settings = {
            palette: ["#101010", "#3A3A3A"],
            wander: true,
            radius: 0.35,
            strength: 1,
            speed: 0.86,
            scale: 2.5,
            intensity: 0.59,
            warp: 0,
            detail: 2.4,
            contrast: 0.91,
            brightness: -0.1,
            saturation: 1,
            hue: 6.28,
            vignette: 0,
            blur: 0.016,
            grain: 0.16,
            drift: 0.03,
            seed: 1,
            rotation: 0,
            oklab: false
        };

        const pointer = { x: 0, y: 0, inside: false };
        const light = { x: 0, y: 0 };
        let presence = 0;
        let time = 0;
        let roam = 0;
        let last = 0;
        let raf = 0;

        function wanderAt(t) {
          return [0.62 * Math.sin(t * 0.37), 0.5 * Math.sin(t * 0.53 + 1.3)];
        }

        const resize = () => {
          const dpr = Math.min(window.parent.devicePixelRatio || 1, 2);
          const w = Math.max(1, Math.round(canvas.clientWidth * dpr));
          const h = Math.max(1, Math.round(canvas.clientHeight * dpr));
          if (canvas.width !== w || canvas.height !== h) {
            canvas.width = w;
            canvas.height = h;
          }
        };

        const draw = (now) => {
          raf = 0;
          const dt = last ? Math.min((now - last) / 1000, 0.05) : 0.016;
          last = now;
          resize();

          time += dt * settings.speed;
          roam += dt;

          const tx = pointer.inside ? pointer.x : (settings.wander ? wanderAt(roam)[0] : 0);
          const ty = pointer.inside ? pointer.y : (settings.wander ? wanderAt(roam)[1] : 0);
          const on = pointer.inside || settings.wander ? 1 : 0;
          
          const k = 1 - Math.exp(-dt / (pointer.inside ? 0.08 : 0.6));
          light.x += (tx - light.x) * k;
          light.y += (ty - light.y) * k;
          presence += (on - presence) * (1 - Math.exp(-dt / 0.25));

          colorData.fill(0);
          settings.palette.forEach((hex, i) => colorData.set(hexToRgb(hex), i * 3));

          gl.viewport(0, 0, canvas.width, canvas.height);
          gl.uniform3fv(loc.colors, colorData);
          gl.uniform4f(loc.scene, canvas.width, canvas.height, time, settings.palette.length);
          gl.uniform4f(loc.shape, settings.scale, settings.intensity, 0.5, settings.warp);
          gl.uniform4f(loc.surface, settings.detail, settings.contrast, settings.brightness, settings.saturation);
          gl.uniform4f(loc.finish, settings.hue, settings.vignette, settings.blur, settings.grain);
          gl.uniform4f(loc.transform, settings.seed, settings.rotation, settings.drift, settings.oklab ? 1 : 0);
          gl.uniform4f(loc.space, 0, 0, light.x, light.y);
          gl.uniform4f(loc.cursor, presence, 4, settings.strength, settings.radius);
          gl.drawArrays(gl.TRIANGLES, 0, 3);

          raf = requestAnimationFrame(draw);
        };

        const kick = () => {
          if (!raf) raf = requestAnimationFrame(draw);
        };
        kick();

        const onMove = (e) => {
          const r = canvas.getBoundingClientRect();
          pointer.inside = e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom;
          pointer.x = ((e.clientX - r.left) / r.width) * 2 - 1;
          pointer.y = 1 - ((e.clientY - r.top) / r.height) * 2;
        };
        const onLeave = () => { pointer.inside = false; };

        window.parent.addEventListener("pointermove", onMove, { passive: true });
        window.parent.document.documentElement.addEventListener("pointerleave", onLeave);

    })();
    </script>
    """, height=0)
