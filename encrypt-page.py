#!/usr/bin/env python3
"""
Encrypt an HTML page's body content with AES-256-GCM.
Uses only Python stdlib (no external packages).
Browser decrypts with Web Crypto API (PBKDF2 + AES-GCM).

Python 3.6+ has AES-GCM support via the `cryptography` module isn't needed -
we can use the `ssl` module's underlying OpenSSL via ctypes, but the simplest
stdlib approach is to use hmac-based encryption that the browser can replicate.

Actually, the cleanest zero-dependency approach: generate the encrypted payload
using a Node.js one-liner (Web Crypto API equivalent) since we need browser
compatibility anyway.
"""

import os
import sys
import json
import base64
import hashlib
import subprocess
from pathlib import Path


def extract_parts(html: str):
    """Split HTML into head content and body content."""
    body_start = html.find('<body')
    body_tag_end = html.find('>', body_start) + 1
    body_close = html.rfind('</body>')

    head_start = html.find('<head')
    head_tag_end = html.find('>', head_start) + 1
    head_close = html.rfind('</head>')

    head_content = html[head_tag_end:head_close]
    body_content = html[body_tag_end:body_close]

    return head_content, body_content


def encrypt_with_node(plaintext: str, password: str) -> dict:
    """Use Node.js crypto module (always available) for AES-256-GCM encryption."""
    # Write plaintext to a temp file to avoid shell escaping issues
    tmp_plain = Path("/tmp/_encrypt_plain.txt")
    tmp_plain.write_text(plaintext, encoding='utf-8')

    node_script = '''
const crypto = require("crypto");
const fs = require("fs");

const password = process.argv[1];
const plaintext = fs.readFileSync("/tmp/_encrypt_plain.txt", "utf-8");

const salt = crypto.randomBytes(16);
const iv = crypto.randomBytes(12);
const key = crypto.pbkdf2Sync(password, salt, 100000, 32, "sha256");

const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
const encrypted = Buffer.concat([cipher.update(plaintext, "utf8"), cipher.final()]);
const tag = cipher.getAuthTag();

// Web Crypto API expects ciphertext + tag concatenated
const combined = Buffer.concat([encrypted, tag]);

console.log(JSON.stringify({
    salt: salt.toString("base64"),
    iv: iv.toString("base64"),
    data: combined.toString("base64")
}));
'''

    result = subprocess.run(
        ["node", "-e", node_script, password],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode != 0:
        raise RuntimeError(f"Node encryption failed: {result.stderr}")

    # Clean up temp file
    tmp_plain.unlink(missing_ok=True)

    return json.loads(result.stdout.strip())


def build_protected_page(head_content: str, encrypted: dict) -> str:
    """Build the protected HTML page with login form, decryption, and sessionStorage."""

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Preview - Authentication Required</title>
<meta name="robots" content="noindex, nofollow">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #1a1a2e; min-height: 100vh; display: flex; align-items: center; justify-content: center; }}

.login-panel {{
  background: #16213e;
  border-radius: 8px;
  padding: 40px 36px;
  width: 360px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}}
.login-panel h2 {{
  color: #e2e2e2;
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 24px;
  text-align: center;
}}
.login-panel input {{
  width: 100%;
  padding: 12px 16px;
  background: #0f3460;
  border: 1px solid #1a1a4e;
  border-radius: 6px;
  color: #e2e2e2;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}}
.login-panel input:focus {{
  border-color: #533483;
}}
.login-panel input::placeholder {{
  color: #6b7b9e;
}}
.login-panel button {{
  width: 100%;
  padding: 12px;
  margin-top: 16px;
  background: #533483;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}}
.login-panel button:hover {{
  background: #6a42a0;
}}
.error-msg {{
  color: #e94560;
  font-size: 13px;
  text-align: center;
  margin-top: 12px;
  min-height: 20px;
}}
.shake {{
  animation: shake 0.4s ease-in-out;
}}
@keyframes shake {{
  0%, 100% {{ transform: translateX(0); }}
  25% {{ transform: translateX(-8px); }}
  75% {{ transform: translateX(8px); }}
}}
#page-content {{
  display: none;
}}
</style>
</head>
<body>

<div class="login-panel" id="login-panel">
  <h2>Enter password to continue</h2>
  <form id="login-form" onsubmit="return handleLogin(event)">
    <input type="password" id="pwd" placeholder="Password" autocomplete="off" autofocus>
    <button type="submit" id="btn">Unlock</button>
  </form>
  <div class="error-msg" id="error"></div>
</div>

<div id="encrypted-payload" style="display:none">{json.dumps(encrypted)}</div>

<template id="original-head">{head_content}</template>

<div id="page-content"></div>

<script>
// Auto-unlock if already authenticated in this tab
(async function checkSession() {{
  const savedPwd = sessionStorage.getItem("_pk");
  if (savedPwd) {{
    try {{
      const html = await decryptContent(savedPwd);
      showContent(html);
    }} catch (e) {{
      sessionStorage.removeItem("_pk");
    }}
  }}
}})();

async function deriveKey(password, salt) {{
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    "raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]
  );
  return crypto.subtle.deriveKey(
    {{ name: "PBKDF2", salt: salt, iterations: 100000, hash: "SHA-256" }},
    keyMaterial,
    {{ name: "AES-GCM", length: 256 }},
    false,
    ["decrypt"]
  );
}}

function b64ToBuffer(b64) {{
  const bin = atob(b64);
  const buf = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  return buf;
}}

async function decryptContent(password) {{
  const payload = JSON.parse(document.getElementById("encrypted-payload").textContent);
  const salt = b64ToBuffer(payload.salt);
  const iv = b64ToBuffer(payload.iv);
  const data = b64ToBuffer(payload.data);
  const key = await deriveKey(password, salt);
  const decrypted = await crypto.subtle.decrypt(
    {{ name: "AES-GCM", iv: iv }}, key, data
  );
  return new TextDecoder().decode(decrypted);
}}

function showContent(html) {{
  const headTemplate = document.getElementById("original-head").innerHTML;
  document.head.innerHTML = headTemplate;
  const panel = document.getElementById("login-panel");
  if (panel) panel.style.display = "none";
  const container = document.getElementById("page-content");
  container.innerHTML = html;
  container.style.display = "block";
  document.body.style.background = "";
  document.body.style.display = "";
  document.body.style.alignItems = "";
  document.body.style.justifyContent = "";
  document.body.style.minHeight = "";
}}

async function handleLogin(e) {{
  e.preventDefault();
  const pwd = document.getElementById("pwd").value;
  const btn = document.getElementById("btn");
  const panel = document.getElementById("login-panel");
  const error = document.getElementById("error");

  btn.textContent = "Decrypting...";
  btn.disabled = true;
  error.textContent = "";

  try {{
    const html = await decryptContent(pwd);
    sessionStorage.setItem("_pk", pwd);
    showContent(html);
  }} catch (err) {{
    error.textContent = "Incorrect password";
    panel.classList.add("shake");
    setTimeout(() => panel.classList.remove("shake"), 400);
    btn.textContent = "Unlock";
    btn.disabled = false;
  }}
  return false;
}}
</script>
</body>
</html>'''


def encrypt_file(source: Path, password: str):
    """Encrypt a single HTML file in place (backs up original first)."""
    backup = source.with_suffix('.html.bak')
    if not backup.exists():
        import shutil
        shutil.copy2(source, backup)
        print(f"  Backed up to: {backup.name}")

    html = backup.read_text(encoding='utf-8')
    head_content, body_content = extract_parts(html)

    print(f"  Body: {len(body_content):,} chars")

    encrypted = encrypt_with_node(body_content, password)

    print(f"  Encrypted: {len(encrypted['data']):,} chars (base64)")

    protected = build_protected_page(head_content, encrypted)
    source.write_text(protected, encoding='utf-8')

    print(f"  Written: {source.name} ({source.stat().st_size:,} bytes)")


def main():
    base = Path("/Users/grantharrison/Documents/Claude/preview-x7k9m2")

    sys.path.insert(0, str(Path(__file__).parent.parent / "Cognita" / "creative-iq"))
    from config import get_password
    password = get_password(os.environ.get("SCHOOL", "ais"))

    files = sys.argv[1:] if len(sys.argv) > 1 else ["index.html", "asia-v2.html"]

    for filename in files:
        source = base / filename
        if not source.exists():
            print(f"Skipping {filename} - not found")
            continue
        print(f"\nEncrypting {filename}...")
        encrypt_file(source, password)


if __name__ == "__main__":
    main()
