const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const APK_PATH = path.resolve('app/build/outputs/apk/debug/app-debug.apk');
const LOG_FILE = path.resolve('phone_logs.txt');

const server = http.createServer((req, res) => {
    // Cabeceras CORS universales para permitir fetch desde el WebView
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        return res.end();
    }

    console.log(`[${new Date().toLocaleTimeString()}] ${req.method} ${req.url}`);

    // Endpoint para recibir logs del juego
    if (req.url === '/log' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk; });
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                const logs = Array.isArray(data.logs) ? data.logs.join('\n') : (data.logs || body);
                const header = `\n================ LOGS RECIBIDOS (${new Date().toLocaleString()}) ================\n`;
                fs.appendFileSync(LOG_FILE, header + logs + '\n');
                console.log(`\n\x1b[32m✔ [LOGS RECIBIDOS DEL TELÉFONO]\x1b[0m Guardados en phone_logs.txt (${data.logs ? data.logs.length : 1} entradas)`);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ status: 'ok', received: true }));
            } catch (err) {
                console.error('Error procesando logs:', err);
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ status: 'error', message: err.message }));
            }
        });
        return;
    }

    // Endpoint para descargar el APK
    if (req.url === '/app-debug.apk' || req.url.startsWith('/app-debug.apk')) {
        if (!fs.existsSync(APK_PATH)) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            return res.end('APK no encontrado. Compilalo primero.');
        }

        const stat = fs.statSync(APK_PATH);
        res.writeHead(200, {
            'Content-Type': 'application/vnd.android.package-archive',
            'Content-Length': stat.size,
            'Content-Disposition': 'attachment; filename="app-debug.apk"'
        });

        const stream = fs.createReadStream(APK_PATH);
        stream.pipe(res);
        return;
    }

    // Página de bienvenida
    const apkExists = fs.existsSync(APK_PATH);
    const sizeMb = apkExists ? (fs.statSync(APK_PATH).size / (1024 * 1024)).toFixed(1) : 0;
    const dateStr = apkExists ? fs.statSync(APK_PATH).mtime.toLocaleTimeString() : '';

    const html = `<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Descargar VR Shooter APK</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            background: rgba(30, 41, 59, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 32px 24px;
            max-width: 420px;
            width: 100%;
            text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .icon {
            font-size: 56px;
            margin-bottom: 12px;
        }
        h1 {
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p {
            color: #94a3b8;
            font-size: 15px;
            margin-bottom: 24px;
        }
        .btn {
            display: block;
            width: 100%;
            padding: 16px;
            background: linear-gradient(90deg, #0284c7, #4f46e5);
            color: white;
            text-decoration: none;
            font-weight: 600;
            font-size: 17px;
            border-radius: 14px;
            box-shadow: 0 10px 25px -5px rgba(14, 165, 233, 0.4);
            transition: transform 0.2s, background 0.2s;
        }
        .btn:active {
            transform: scale(0.98);
        }
        .info {
            margin-top: 20px;
            font-size: 13px;
            color: #64748b;
            line-height: 1.6;
        }
        .badge {
            display: inline-block;
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            margin-bottom: 16px;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">🥽</div>
        <div class="badge">Versión 1.0 Debug</div>
        <h1>VR Shooter</h1>
        <p>Instala la última versión con soporte para gamepad X3 y cámara VR anclada.</p>
        
        <a href="/app-debug.apk" class="btn" download="app-debug.apk">
            Descargar APK (${sizeMb} MB)
        </a>

        <div class="info">
            Última compilación: ${dateStr}<br>
            Una vez descargado, ábrelo para instalarlo directamente.
        </div>
    </div>
</body>
</html>`;

    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(html);
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`Servidor local activo en puerto ${PORT}`);
});
