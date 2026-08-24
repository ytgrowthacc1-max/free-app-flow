import os
import json
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whop Notification Redirect Tester</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #0f0f12;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            background: #18181f;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            border: 1px solid #2d2d3d;
            max-width: 450px;
        }
        h2 {
            color: #a855f7;
            margin-bottom: 15px;
        }
        p {
            color: #9ca3af;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .param-box {
            background: #0f0f12;
            padding: 10px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.85rem;
            color: #34d399;
            margin: 15px 0;
            border: 1px solid #222;
            text-align: left;
            word-break: break-all;
        }
        .btn {
            display: inline-block;
            background: #a855f7;
            color: #fff;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            transition: background 0.2s;
            margin-top: 10px;
        }
        .btn:hover {
            background: #9333ea;
        }
        .loader {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #a855f7;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 8px;
            vertical-align: middle;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Whop Redirect App</h2>
        
        <div id="redirecting-section" style="display: none;">
            <p><span class="loader"></span>Redirecting you to your billing settings...</p>
            <div class="param-box" id="target-url"></div>
            <p>If you are not redirected automatically, click the button below:</p>
            <a href="#" id="manual-link" target="_parent" class="btn">Go to Billing</a>
        </div>

        <div id="no-redirect-section">
            <p>App loaded successfully at path: <code id="loaded-path"></code></p>
            <p>No <code>restPath</code> redirect parameter was detected.</p>
            <div class="param-box">
                URL Parameters:<br>
                {{ params_json }}
            </div>
        </div>
    </div>

    <script>
        // Set path
        document.getElementById('loaded-path').innerText = window.location.pathname;

        // Parse incoming query parameters and path
        const urlParams = new URLSearchParams(window.location.search);
        const restPath = urlParams.get('restPath');
        const path = window.location.pathname;
        const decodedPath = decodeURIComponent(path);
        
        let destination = null;
        
        // Helper to decode Base64
        function tryDecodeBase64(str) {
            try {
                // Remove base64 padding errors or other URL-safe modifications if any
                const decoded = atob(str);
                if (decoded.startsWith('http://') || decoded.startsWith('https://')) {
                    return decoded;
                }
            } catch (e) {}
            return null;
        }
        
        // 1. Check if restPath is a direct URL
        if (restPath && restPath.startsWith('http')) {
            destination = restPath;
        } 
        // 2. Check if restPath is base64 encoded URL
        else if (restPath && tryDecodeBase64(restPath)) {
            destination = tryDecodeBase64(restPath);
        }
        // 3. Check if path has base64 encoded URL in the last segment
        else {
            const segments = path.split('/').filter(Boolean);
            if (segments.length > 0) {
                const lastSegment = segments[segments.length - 1];
                const decodedBase64 = tryDecodeBase64(lastSegment);
                if (decodedBase64) {
                    destination = decodedBase64;
                }
            }
        }
        
        // 4. Fallback checks for hardcoded routing paths
        if (!destination) {
            if (decodedPath.includes('http://') || decodedPath.includes('https://')) {
                const index = decodedPath.indexOf('http');
                destination = decodedPath.substring(index);
            } else if (restPath === '/settings/billing' || path.includes('/settings/billing') || path.includes('/billing')) {
                destination = 'https://whop.com/checkout/settings';
            } else if (path.includes('/login')) {
                // Fallback: If Whop stripped it down to just /login, redirect to usefastlane login
                destination = 'https://app.usefastlane.ai/login';
            }
        }
        
        if (destination) {
            document.getElementById('no-redirect-section').style.display = 'none';
            document.getElementById('redirecting-section').style.display = 'block';
            
            document.getElementById('target-url').innerText = destination;
            document.getElementById('manual-link').href = destination;
            
            // Attempt auto-redirect of the parent browser window
            setTimeout(() => {
                try {
                    window.parent.location.href = destination;
                } catch (e) {
                    console.log("Parent redirect blocked, trying top:", e);
                    try {
                        window.top.location.href = destination;
                    } catch (err) {
                        console.log("Top redirect blocked, user must click button manually.", err);
                    }
                }
            }, 1000);
        }
    </script>
</body>
</html>
"""

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    params = dict(request.args)
    params_json = json.dumps(params, indent=2) if params else "None"
    return render_template_string(HTML_TEMPLATE, params_json=params_json)

if __name__ == "__main__":
    print("[SERVER] Starting Whop Redirection App on http://localhost:8090")
    app.run(host="0.0.0.0", port=8090)
