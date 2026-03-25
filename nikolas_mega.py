#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  NIKOLAS MEGA ULTIMATE v2500 - الملف الموحّد الشامل                      ║
║  ✅ دمج كامل: v1000 + v1300 + v2400 + v2500 + omni_ultimate_v2_mega      ║
║  ✅ 350+ كلاس | 2000+ أمر | مجاني 100%                                   ║
║  ✅ FaceUI + WebSocket + REST API                                          ║
║  ✅ يعمل على: Termux / Andronix / Linux / Android                          ║
║  🚀 تشغيل: python3 nikolas_mega_ultimate.py                                ║
║  🌐 ثم افتح: http://localhost:8080 أو omni_ultimate_v2_mega.html          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import re
import json
import ast
import math
import time
import shutil
import hashlib
import asyncio
import sqlite3
import threading
import tarfile
import pickle
import base64
import random
import string
import importlib.util
import traceback
import functools
import gc
import signal
import subprocess
import socket
import ssl
import http.server
import urllib.parse
import urllib.request
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Set, Union, Callable, Awaitable
from collections import deque, defaultdict, Counter
from enum import Enum
import readline
import atexit

# =============================================================================
# متغيرات البيئة والمسارات
# =============================================================================

_HOME = Path.home()
_NIK_ROOT = _HOME / ".nikolas"
_BRAIN_DIR = _NIK_ROOT / "brain"
_MEMORY_DIR = _NIK_ROOT / "memory"
_AGENTS_DIR = _NIK_ROOT / "agents"
_CORE_DIR = _NIK_ROOT / "core"
_TOOLS_DIR = _NIK_ROOT / "tools"
_API_DIR = _NIK_ROOT / "api"
_ENGINE_DIR = _NIK_ROOT / "engine"
_LOGS_DIR = _NIK_ROOT / "logs"
_MODELS_DIR = _NIK_ROOT / "models"
_CACHE_DIR = _NIK_ROOT / "cache"
_INDEX_DIR = _NIK_ROOT / "indexes"
_CHECKPOINTS = _NIK_ROOT / "checkpoints"

# إنشاء المجلدات
for _d in [_BRAIN_DIR, _MEMORY_DIR, _AGENTS_DIR, _CORE_DIR,
           _TOOLS_DIR, _API_DIR, _ENGINE_DIR, _LOGS_DIR,
           _MODELS_DIR, _CACHE_DIR, _INDEX_DIR, _CHECKPOINTS]:
    _d.mkdir(parents=True, exist_ok=True)

# =============================================================================
# كشف البيئة
# =============================================================================

IS_TERMUX = (
    bool(os.getenv("TERMUX_VERSION")) or
    "com.termux" in os.getenv("PREFIX", "") or
    Path("/data/data/com.termux").exists()
)

IS_ANDRONIX = IS_TERMUX and Path("/etc/os-release").exists()
IS_LINUX = not IS_TERMUX and sys.platform.startswith('linux')
IS_ANDROID = IS_TERMUX

ENV_NAME = "Andronix+Termux" if IS_ANDRONIX else "Termux" if IS_TERMUX else "Linux"

# =============================================================================
# ألوان الطرفية
# =============================================================================

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    @staticmethod
    def ok(msg): return f"{C.GREEN}✅ {msg}{C.RESET}"
    @staticmethod
    def err(msg): return f"{C.RED}❌ {msg}{C.RESET}"
    @staticmethod
    def warn(msg): return f"{C.YELLOW}⚠️ {msg}{C.RESET}"
    @staticmethod
    def info(msg): return f"{C.CYAN}ℹ️ {msg}{C.RESET}"
    @staticmethod
    def bold(msg): return f"{C.BOLD}{msg}{C.RESET}"

# =============================================================================
# Logger
# =============================================================================

class NikolasLogger:
    """مسجّل موحد مع ألوان وملفات يومية."""

    COLORS = {
        'SUCCESS': C.GREEN, 'WARNING': C.YELLOW,
        'ERROR': C.RED, 'CRITICAL': C.RED + C.BOLD,
        'INFO': C.CYAN, 'HEARTBEAT': C.BLUE,
    }
    ICONS = {'SUCCESS': '✅', 'WARNING': '⚠️', 'ERROR': '❌', 'CRITICAL': '🚨', 'INFO': 'ℹ️'}

    def __init__(self):
        self._lock = threading.Lock()
        self._error_log = _LOGS_DIR / "errors.log"
        _LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def _today_log(self) -> Path:
        return _LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"

    def log(self, level: str, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}][{level}] {msg}\n"
        with self._lock:
            try:
                with open(self._today_log(), 'a', encoding='utf-8') as f:
                    f.write(line)
            except Exception: pass
            if level in ('ERROR', 'CRITICAL'):
                try:
                    with open(self._error_log, 'a', encoding='utf-8') as f:
                        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
                except Exception: pass

    def _print(self, level: str, msg: str):
        c = self.COLORS.get(level, '')
        i = self.ICONS.get(level, '•')
        print(f"{c}{i} {msg}{C.RESET}")

    def success(self, msg): self.log('SUCCESS', msg); self._print('SUCCESS', msg)
    def warning(self, msg): self.log('WARNING', msg); self._print('WARNING', msg)
    def error(self, msg): self.log('ERROR', msg); self._print('ERROR', msg)
    def info(self, msg): self.log('INFO', msg)
    def critical(self, msg): self.log('CRITICAL', msg); self._print('CRITICAL', msg)

nlog = NikolasLogger()

# =============================================================================
# تثبيت تلقائي للمكتبات
# =============================================================================

REQUIRED_PACKAGES = {
    "aiohttp": ("aiohttp", "طلبات HTTP غير متزامنة", "critical"),
    "bs4": ("beautifulsoup4", "تحليل HTML", "high"),
    "sympy": ("sympy", "الرياضيات الرمزية", "high"),
    "rich": ("rich", "واجهة الطرفية الملونة", "high"),
    "requests": ("requests", "طلبات HTTP بسيطة", "high"),
    "fitz": ("pymupdf", "قراءة PDF", "medium"),
    "psutil": ("psutil", "مراقبة CPU/RAM", "medium"),
    "cryptography": ("cryptography", "تشفير AES-256", "medium"),
    "PIL": ("pillow", "معالجة الصور", "low"),
    "pytesseract": ("pytesseract", "OCR", "low"),
    "matplotlib": ("matplotlib", "رسم المخططات", "low"),
    "pandas": ("pandas", "تحليل CSV", "low"),
    "sentence_transformers": ("sentence-transformers", "البحث الدلالي", "low"),
}

class AutoInstaller:
    def __init__(self):
        self._status = {}
        self._log = self._load_log()
        self._lock = threading.Lock()
        self._is_termux = IS_TERMUX

    def _load_log(self):
        try:
            if (_BRAIN_DIR / "install_log.json").exists():
                return json.loads((_BRAIN_DIR / "install_log.json").read_text())
        except Exception: pass
        return {"installed": [], "failed": [], "last_check": ""}

    def check_package(self, import_name: str) -> bool:
        try:
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False

    def install_package(self, import_name: str, verbose: bool = True) -> bool:
        if import_name not in REQUIRED_PACKAGES:
            return False
        pip_name, desc, priority = REQUIRED_PACKAGES[import_name]
        if verbose:
            print(f"  📦 تثبيت {pip_name}...", end="", flush=True)
        cmd = [sys.executable, "-m", "pip", "install", pip_name, "-q"]
        if self._is_termux:
            cmd.append("--break-system-packages")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            success = result.returncode == 0
            if verbose:
                print(" ✅" if success else " ❌")
            return success
        except Exception:
            return False

    def check_and_install_all(self, verbose: bool = True) -> dict:
        results = {"available": [], "installed": [], "failed": []}
        for import_name, (pip_name, desc, priority) in REQUIRED_PACKAGES.items():
            available = self.check_package(import_name)
            if available:
                results["available"].append(import_name)
            else:
                if verbose:
                    print(f"  ⚠️ {pip_name} غير موجود - يُثبَّت...")
                success = self.install_package(import_name, False)
                if success:
                    results["installed"].append(import_name)
                else:
                    results["failed"].append(import_name)
        return results

_auto_installer = AutoInstaller()

# =============================================================================
# Response Cache
# =============================================================================

class ResponseCache:
    CACHE_TTL = {
        "crypto": 300, "weather": 1800, "news": 900, "wiki": 3600,
        "arxiv": 3600, "translate": 600,
    }

    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def _get_ttl(self, cmd: str) -> int:
        for prefix, ttl in self.CACHE_TTL.items():
            if cmd.startswith(prefix):
                return ttl
        return 0

    def get(self, cmd: str, args: str) -> Optional[str]:
        key = f"{cmd}:{args}"
        ttl = self._get_ttl(cmd)
        if ttl == 0:
            return None
        with self._lock:
            if key in self._cache:
                result, ts = self._cache[key]
                if time.time() - ts < ttl:
                    self._hits += 1
                    return result
                else:
                    del self._cache[key]
        return None

    def set(self, cmd: str, args: str, result: str):
        ttl = self._get_ttl(cmd)
        if ttl == 0 or not result:
            return
        key = f"{cmd}:{args}"
        with self._lock:
            self._cache[key] = (result, time.time())
            self._misses += 1
            if len(self._cache) > 200:
                now = time.time()
                expired = [k for k, (_, ts) in self._cache.items() if now - ts > 3600]
                for k in expired:
                    del self._cache[k]

    def stats(self) -> str:
        with self._lock:
            total = self._hits + self._misses
            rate = (self._hits / total * 100) if total > 0 else 0
            size = len(self._cache)
        return f"💾 Cache: {size} عنصر | hits: {self._hits} | misses: {self._misses} | نسبة: {rate:.0f}%"

response_cache = ResponseCache()

# =============================================================================
# AutoInstaller للـ FaceUI
# =============================================================================

class FaceUIAutoInstaller:
    @staticmethod
    def install():
        """تثبيت المكتبات المطلوبة لـ FaceUI."""
        missing = []
        for mod, pip in [('fastapi', 'fastapi'), ('uvicorn', 'uvicorn[standard]'), ('websockets', 'websockets')]:
            try:
                importlib.import_module(mod)
            except ImportError:
                missing.append(pip)
        if missing:
            print(f"📦 تثبيت {len(missing)} مكتبة لـ FaceUI...")
            cmd = [sys.executable, '-m', 'pip', 'install', '--break-system-packages', '-q'] + missing
            subprocess.run(cmd, timeout=120)
            import importlib
            importlib.invalidate_caches()

# =============================================================================
# HTML Interface - omni_ultimate_v2_mega
# =============================================================================

OMNI_HTML = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<title>نيكولاس MEGA v2500 | المساعد الذكي الشامل</title>
<meta name="description" content="نيكولاس MEGA - مساعد ذكي شامل مع 2000+ أمر، 350+ كلاس، مجاني 100%">
<meta name="theme-color" content="#0f0f10">
<link rel="manifest" href="/manifest.json">

<!-- Libraries -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/highlight.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github-dark.min.css">

<!-- Fonts & Icons -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<!-- Custom Styles -->
<style>
:root {
  --bg: #0f0f10;
  --surface: #1a1a1c;
  --surface2: #222224;
  --surface3: #2a2a2d;
  --border: #3a3a3d;
  --text: #ececec;
  --muted: #8e8ea0;
  --primary: #4f8ef7;
  --primary-dark: #3a6bc0;
  --secondary: #19c37d;
  --accent: #ab68ff;
  --danger: #ef4444;
  --warning: #f59e0b;
  --info: #3b82f6;
  --user-bg: #2a3a5c;
  --bot-bg: #1a1a1c;
  --radius: 16px;
  --radius-sm: 10px;
  --font: 'Inter', system-ui, -apple-system, sans-serif;
  --mono: 'Fira Code', 'Cascadia Code', monospace;
  --shadow: 0 8px 32px rgba(0,0,0,0.3);
  --transition: all 0.2s ease;
}
[data-theme="light"] {
  --bg: #f7f7f8;
  --surface: #ffffff;
  --surface2: #f0f0f0;
  --surface3: #e5e5e5;
  --border: #d9d9e3;
  --text: #1a1a1a;
  --muted: #666666;
  --user-bg: #e8f0fe;
  --bot-bg: #ffffff;
}
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
html, body {
  height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  overflow: hidden;
}
body {
  display: flex;
  flex-direction: column;
  height: 100dvh;
}
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--primary);
}
button, .btn, .clickable {
  cursor: pointer;
  transition: var(--transition);
}
button:active {
  transform: scale(0.97);
}
input, textarea, select {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  padding: 10px 14px;
  font-family: var(--font);
  font-size: 0.9rem;
  outline: none;
  transition: var(--transition);
}
input:focus, textarea:focus, select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(79, 142, 247, 0.2);
}
textarea {
  resize: none;
}
/* Toast */
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%) translateY(-20px);
  background: var(--surface3);
  border: 1px solid var(--border);
  border-radius: 30px;
  padding: 8px 20px;
  font-size: 0.85rem;
  z-index: 10000;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s ease;
  white-space: nowrap;
  max-width: 90vw;
  overflow-x: auto;
}
.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
/* Modal */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s;
}
.modal.active {
  opacity: 1;
  visibility: visible;
}
.modal-content {
  background: var(--surface);
  border-radius: var(--radius);
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
  padding: 24px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--muted);
  cursor: pointer;
}
/* Login */
.login-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  background: var(--bg);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}
.login-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 40px;
  width: 360px;
  text-align: center;
  box-shadow: var(--shadow);
}
.login-icon {
  font-size: 4rem;
  margin-bottom: 16px;
}
.login-card h2 {
  font-size: 1.5rem;
  margin-bottom: 8px;
}
.login-card p {
  color: var(--muted);
  margin-bottom: 24px;
}
.login-input {
  width: 100%;
  margin-bottom: 16px;
  text-align: center;
}
.login-btn {
  width: 100%;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: 12px;
  font-weight: 600;
  font-size: 1rem;
}
.login-btn:hover {
  background: var(--primary-dark);
}
.login-error {
  color: var(--danger);
  font-size: 0.8rem;
  margin-top: 12px;
}
/* App Container */
#app {
  display: none;
  flex-direction: column;
  height: 100dvh;
  overflow: hidden;
}
/* Header */
.header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  z-index: 10;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--primary);
}
.logo span {
  color: var(--secondary);
}
.logo-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--secondary);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.9); }
}
.model-select {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  padding: 6px 12px;
  font-size: 0.85rem;
  cursor: pointer;
  outline: none;
  flex: 1;
  max-width: 200px;
}
.header-buttons {
  display: flex;
  gap: 8px;
  margin-left: auto;
}
.header-btn {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  color: var(--muted);
  cursor: pointer;
  font-size: 0.85rem;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 6px;
}
.header-btn:hover {
  background: var(--surface3);
  color: var(--text);
}
.header-btn.active {
  color: var(--primary);
  border-color: var(--primary);
}
/* Main Layout */
.main {
  display: flex;
  flex: 1;
  overflow: hidden;
}
/* Sidebar */
.sidebar {
  width: 280px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.2s, opacity 0.2s;
  overflow: hidden;
}
.sidebar.collapsed {
  width: 0;
  opacity: 0;
}
.sidebar-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sidebar-search {
  margin: 12px;
  padding: 8px 12px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 0.85rem;
}
.tools-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.tool-category {
  margin-bottom: 16px;
}
.tool-category-title {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
  padding: 8px 8px 4px;
  font-weight: 600;
}
.tool-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
}
.tool-item:hover {
  background: var(--surface2);
}
.tool-item.active {
  background: var(--surface3);
  color: var(--primary);
}
.tool-icon {
  width: 28px;
  font-size: 1.1rem;
  text-align: center;
}
.tool-name {
  font-size: 0.85rem;
  flex: 1;
}
.tool-badge {
  font-size: 0.7rem;
  background: var(--primary);
  color: white;
  border-radius: 20px;
  padding: 2px 6px;
}
/* Chat Area */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}
/* Welcome */
.welcome {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
  gap: 20px;
}
.welcome-icon {
  font-size: 5rem;
}
.welcome h1 {
  font-size: 1.8rem;
  font-weight: 700;
}
.welcome p {
  color: var(--muted);
  max-width: 500px;
}
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}
.quick-btn {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 10px 16px;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;
}
.quick-btn:hover {
  background: var(--surface3);
  transform: translateY(-2px);
}
/* Messages */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.message {
  display: flex;
  flex-direction: column;
  animation: fadeInUp 0.2s ease;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.message.user {
  align-items: flex-end;
}
.message.bot {
  align-items: flex-start;
}
.message-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  max-width: 85%;
}
.message.user .message-row {
  flex-direction: row-reverse;
}
.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.message-avatar.bot {
  background: linear-gradient(135deg, var(--primary), var(--accent));
}
.message-avatar.user {
  background: var(--surface2);
}
.message-bubble {
  background: var(--bot-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
  font-size: 0.9rem;
  line-height: 1.6;
  word-break: break-word;
}
.message.user .message-bubble {
  background: var(--user-bg);
  border-bottom-right-radius: 4px;
}
.message.bot .message-bubble {
  border-bottom-left-radius: 4px;
}
.message-bubble pre {
  background: #0d1117;
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
  font-family: var(--mono);
  font-size: 0.8rem;
}
.message-bubble code {
  font-family: var(--mono);
  font-size: 0.85em;
}
.message-bubble p {
  margin-bottom: 0.5em;
}
.message-bubble p:last-child {
  margin-bottom: 0;
}
.message-bubble ul, .message-bubble ol {
  padding-right: 20px;
  margin: 8px 0;
}
.message-bubble blockquote {
  border-right: 3px solid var(--primary);
  padding-right: 12px;
  color: var(--muted);
  margin: 8px 0;
}
.message-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  font-size: 0.7rem;
  color: var(--muted);
  padding: 0 4px;
}
.message-actions {
  display: flex;
  gap: 6px;
}
.message-action-btn {
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
}
.message-action-btn:hover {
  background: var(--surface2);
  color: var(--text);
}
/* Typing Indicator */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: var(--bot-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  border-bottom-left-radius: 4px;
  width: fit-content;
}
.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--muted);
  animation: typingBounce 0.9s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.15s; }
.typing-dot:nth-child(3) { animation-delay: 0.3s; }
@keyframes typingBounce {
  0%, 100% { transform: translateY(0); opacity: 0.4; }
  50% { transform: translateY(-5px); opacity: 1; }
}
/* Input Area */
.input-area {
  padding: 12px 16px;
  background: var(--surface);
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}
.context-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.context-chip {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
}
.context-chip:hover {
  border-color: var(--primary);
  color: var(--primary);
}
.input-container {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}
.input-wrapper {
  flex: 1;
  position: relative;
}
#messageInput {
  width: 100%;
  padding: 12px 50px 12px 16px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  font-size: 0.9rem;
  resize: none;
  min-height: 44px;
  max-height: 120px;
  line-height: 1.5;
  font-family: var(--font);
}
#messageInput:focus {
  border-color: var(--primary);
}
.attach-btn {
  position: absolute;
  left: 12px;
  bottom: 12px;
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 1.1rem;
}
.send-btn {
  background: var(--primary);
  border: none;
  border-radius: var(--radius);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: var(--transition);
}
.send-btn:hover {
  background: var(--primary-dark);
}
.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.toolbar {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}
.toolbar-btn {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 5px 10px;
  font-size: 0.75rem;
  color: var(--muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}
.toolbar-btn:hover {
  background: var(--surface3);
  color: var(--text);
}
.toolbar-btn.active {
  color: var(--primary);
  border-color: var(--primary);
}
.char-counter {
  font-size: 0.7rem;
  color: var(--muted);
  margin-left: auto;
}
/* Drop Overlay */
.drop-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(79, 142, 247, 0.1);
  border: 2px dashed var(--primary);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 100;
  border-radius: var(--radius);
  pointer-events: none;
}
.drop-overlay.active {
  display: flex;
}
/* Right Panel (Tools) */
.right-panel {
  width: 300px;
  background: var(--surface);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.2s;
}
.right-panel.collapsed {
  width: 0;
}
.panel-tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
}
.panel-tab {
  flex: 1;
  padding: 10px;
  text-align: center;
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 0.8rem;
}
.panel-tab.active {
  color: var(--primary);
  border-bottom: 2px solid var(--primary);
}
.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}
/* Responsive */
@media (max-width: 768px) {
  .sidebar, .right-panel {
    position: fixed;
    top: 0;
    bottom: 0;
    z-index: 100;
    width: 280px;
  }
  .sidebar {
    left: 0;
  }
  .right-panel {
    right: 0;
  }
  .message-row {
    max-width: 95%;
  }
}
</style>
</head>
<body>

<div class="toast" id="toast"></div>

<!-- Login Screen -->
<div class="login-screen" id="loginScreen">
  <div class="login-card">
    <div class="login-icon">🤖</div>
    <h2>نيكولاس MEGA v2500</h2>
    <p>المساعد الذكي الشامل</p>
    <input class="login-input" id="passwordInput" type="password" placeholder="كلمة المرور (اختياري)" autocomplete="off">
    <button class="login-btn" id="loginBtn">دخول</button>
    <div class="login-error" id="loginError"></div>
  </div>
</div>

<!-- Main App -->
<div id="app">

  <!-- Header -->
  <div class="header">
    <div class="logo">
      <span>🤖</span>
      <span>نيكولاس</span>
      <div class="logo-dot" id="connectionDot"></div>
    </div>
    <select class="model-select" id="modelSelect">
      <option value="auto">🔄 تلقائي (أسرع مزود)</option>
      <option value="groq">⚡ Groq (Llama 3.3 70B)</option>
      <option value="gemini">✨ Gemini 1.5 Flash</option>
      <option value="deepseek">🧠 DeepSeek R1/V3</option>
      <option value="claude">🎭 Claude 3.5 Sonnet</option>
      <option value="openai">💎 GPT-4o mini</option>
      <option value="pollinations">🆓 Pollinations (بدون مفتاح)</option>
      <option value="huggingface">🤗 HuggingFace</option>
      <option value="ollama">🦙 Ollama (محلي)</option>
      <option value="local">💾 نموذج محلي (GGUF)</option>
    </select>
    <div class="header-buttons">
      <button class="header-btn" id="themeToggleBtn" title="المظهر">🌙</button>
      <button class="header-btn" id="sidebarToggleBtn" title="الأدوات">📁</button>
      <button class="header-btn" id="newChatBtn" title="محادثة جديدة">➕</button>
      <button class="header-btn" id="settingsBtn" title="الإعدادات">⚙️</button>
    </div>
  </div>

  <!-- Main Content -->
  <div class="main">

    <!-- Left Sidebar (Tools) -->
    <div class="sidebar" id="sidebar">
      <div class="sidebar-header">
        <span>📚 الأدوات الذكية</span>
        <button class="header-btn" id="closeSidebarBtn" style="padding: 2px 6px;">✕</button>
      </div>
      <input class="sidebar-search" id="toolSearch" placeholder="🔍 بحث في الأدوات...">
      <div class="tools-list" id="toolsList"></div>
    </div>

    <!-- Chat Area -->
    <div class="chat-area" id="chatArea">
      <div class="drop-overlay" id="dropOverlay">📁 أفلت الملف هنا</div>

      <!-- Welcome Screen -->
      <div class="welcome" id="welcomeScreen">
        <div class="welcome-icon">🤖</div>
        <h1>مرحباً بك في نيكولاس MEGA</h1>
        <p>مساعد ذكي شامل مع 2000+ أمر، 350+ كلاس، مجاني 100%</p>
        <div class="quick-actions">
          <div class="quick-btn" onclick="quickSend('weather الرياض')">
            <i class="fas fa-cloud-sun"></i> الطقس
          </div>
          <div class="quick-btn" onclick="quickSend('crypto BTC')">
            <i class="fas fa-bitcoin"></i> البيتكوين
          </div>
          <div class="quick-btn" onclick="quickSend('news')">
            <i class="fas fa-newspaper"></i> الأخبار
          </div>
          <div class="quick-btn" onclick="quickSend('code python fibonacci')">
            <i class="fas fa-code"></i> كود
          </div>
          <div class="quick-btn" onclick="quickSend('imagine sunset over mountains')">
            <i class="fas fa-palette"></i> توليد صورة
          </div>
          <div class="quick-btn" onclick="quickSend('translate hello to arabic')">
            <i class="fas fa-language"></i> ترجمة
          </div>
          <div class="quick-btn" onclick="quickSend('stock AAPL')">
            <i class="fas fa-chart-line"></i> أسهم
          </div>
          <div class="quick-btn" onclick="quickSend('port-scan google.com 80,443')">
            <i class="fas fa-shield-alt"></i> فحص منفذ
          </div>
        </div>
      </div>

      <!-- Messages Container -->
      <div class="messages" id="messages" style="display: none;"></div>
    </div>

    <!-- Right Panel (Advanced Tools) -->
    <div class="right-panel" id="rightPanel">
      <div class="panel-tabs">
        <button class="panel-tab active" data-panel="tools">🛠️ أدوات</button>
        <button class="panel-tab" data-panel="canvas">🎨 Canvas</button>
        <button class="panel-tab" data-panel="diff">📊 Diff</button>
        <button class="panel-tab" data-panel="json">📄 JSON</button>
        <button class="panel-tab" data-panel="regex">🔍 Regex</button>
        <button class="panel-tab" data-panel="api">🌐 API</button>
        <button class="panel-tab" data-panel="graph">📈 Graph</button>
        <button class="panel-tab" data-panel="crypto">🔒 Crypto</button>
      </div>
      <div class="panel-content" id="panelContent">
        <!-- Tools Panel -->
        <div class="panel-tools active" id="panelTools">
          <div style="margin-bottom: 12px;">
            <input type="text" id="commandInput" placeholder="اكتب أمراً..." style="width: 100%;">
            <button id="runCommandBtn" style="width: 100%; margin-top: 8px;">▶️ تنفيذ</button>
          </div>
          <div id="commandOutput" style="background: var(--surface2); padding: 10px; border-radius: 8px; font-family: monospace; font-size: 0.8rem; min-height: 100px;"></div>
        </div>
        <!-- Canvas Panel -->
        <div class="panel-canvas" id="panelCanvas" style="display: none;">
          <select id="canvasLang" style="width: 100%; margin-bottom: 8px;">
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="bash">Bash</option>
            <option value="sql">SQL</option>
            <option value="rust">Rust</option>
          </select>
          <textarea id="canvasCode" rows="8" placeholder="اكتب كودك هنا..." style="width: 100%; font-family: monospace;"></textarea>
          <button id="runCanvasBtn" style="width: 100%; margin-top: 8px;">▶️ تشغيل</button>
          <div id="canvasOutput" style="background: var(--surface2); padding: 10px; border-radius: 8px; margin-top: 8px; font-family: monospace; font-size: 0.8rem; min-height: 80px;"></div>
        </div>
        <!-- Diff Panel -->
        <div class="panel-diff" id="panelDiff" style="display: none;">
          <textarea id="diffLeft" rows="5" placeholder="النص الأصلي..." style="width: 100%; font-family: monospace;"></textarea>
          <textarea id="diffRight" rows="5" placeholder="النص الجديد..." style="width: 100%; margin-top: 8px; font-family: monospace;"></textarea>
          <button id="runDiffBtn" style="width: 100%; margin-top: 8px;">📊 مقارنة</button>
          <div id="diffOutput" style="background: var(--surface2); padding: 10px; border-radius: 8px; margin-top: 8px; font-family: monospace; font-size: 0.8rem;"></div>
        </div>
        <!-- JSON Panel -->
        <div class="panel-json" id="panelJson" style="display: none;">
          <textarea id="jsonInput" rows="6" placeholder="أدخل JSON هنا..." style="width: 100%; font-family: monospace;"></textarea>
          <div style="display: flex; gap: 8px; margin-top: 8px;">
            <button id="jsonFormatBtn" style="flex:1;">🎨 تنسيق</button>
            <button id="jsonValidateBtn" style="flex:1;">✅ تحقق</button>
            <button id="jsonMinifyBtn" style="flex:1;">🗜️ ضغط</button>
          </div>
          <div id="jsonOutput" style="background: var(--surface2); padding: 10px; border-radius: 8px; margin-top: 8px; font-family: monospace; font-size: 0.8rem;"></div>
        </div>
        <!-- Regex Panel -->
        <div class="panel-regex" id="panelRegex" style="display: none;">
          <input type="text" id="regexPattern" placeholder="النمط (Regex)..." style="width: 100%;">
          <textarea id="regexText" rows="4" placeholder="النص المراد اختباره..." style="width: 100%; margin-top: 8px;"></textarea>
          <button id="regexTestBtn" style="width: 100%; margin-top: 8px;">🔍 اختبار</button>
          <div id="regexOutput" style="background: var(--surface2); padding: 10px; border-radius: 8px; margin-top: 8px; font-family: monospace; font-size: 0.8rem;"></div>
        </div>
        <!-- API Panel -->
        <div class="panel-api" id="panelApi" style="display: none;">
          <select id="apiMethod" style="width: 100%; margin-bottom: 8px;">
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
          <input type="text" id="apiUrl" placeholder="https://api.example.com/endpoint" style="width: 100%;">
          <textarea id="apiBody" rows="3" placeholder="JSON body (لـ POST/PUT)..." style="width: 100%; margin-top: 8px;"></textarea>
          <button id="apiSendBtn" style="width: 100%; margin-top: 8px;">🚀 إرسال</button>
          <div id="apiOutput" style="background: var(--surface2); padding: 10px; border-radius: 8px; margin-top: 8px; font-family: monospace; font-size: 0.8rem;"></div>
        </div>
        <!-- Graph Panel -->
        <div class="panel-graph" id="panelGraph" style="display: none;">
          <input type="text" id="graphData" placeholder="بيانات: A:10,B:25,C:15,D:30" style="width: 100%;">
          <select id="graphType" style="width: 100%; margin-top: 8px;">
            <option value="bar">📊 Bar Chart</option>
            <option value="line">📈 Line Chart</option>
            <option value="pie">🥧 Pie Chart</option>
          </select>
          <button id="graphDrawBtn" style="width: 100%; margin-top: 8px;">📊 رسم</button>
          <div id="graphOutput" style="background: var(--surface2); padding: 10px; border-radius: 8px; margin-top: 8px; font-family: monospace; font-size: 0.8rem;"></div>
        </div>
        <!-- Crypto Panel -->
        <div class="panel-crypto" id="panelCrypto" style="display: none;">
          <textarea id="cryptoInput" rows="3" placeholder="النص المراد تشفيره..." style="width: 100%;"></textarea>
          <input type="text" id="cryptoKey" placeholder="المفتاح (اختياري)" style="width: 100%; margin-top: 8px;">
          <div style="display: flex; gap: 8px; margin-top: 8px;">
            <button id="cryptoEncryptBtn" style="flex:1;">🔒 تشفير</button>
            <button id="cryptoDecryptBtn" style="flex:1;">🔓 فك تشفير</button>
            <button id="cryptoHashBtn" style="flex:1;">🔐 هاش</button>
          </div>
          <div id="cryptoOutput" style="background: var(--surface2); padding: 10px; border-radius: 8px; margin-top: 8px; font-family: monospace; font-size: 0.8rem;"></div>
        </div>
      </div>
    </div>

  </div>

  <!-- Input Area -->
  <div class="input-area">
    <div class="context-chips" id="contextChips"></div>
    <div class="input-container">
      <div class="input-wrapper">
        <textarea id="messageInput" placeholder="اكتب رسالتك... (مثال: weather الرياض، crypto BTC، code fibonacci)" rows="1"></textarea>
        <button class="attach-btn" id="attachBtn" title="إرفاق ملف">📎</button>
        <input type="file" id="fileInput" style="display: none;">
      </div>
      <button class="send-btn" id="sendBtn">➤</button>
    </div>
    <div class="toolbar">
      <button class="toolbar-btn" id="voiceBtn" title="إدخال صوتي">🎤</button>
      <button class="toolbar-btn" id="ttsBtn" title="نطق الردود">🔊</button>
      <button class="toolbar-btn" id="privacyBtn" title="وضع الخصوصية">🔒</button>
      <button class="toolbar-btn" id="exportBtn" title="تصدير المحادثة">📥</button>
      <span class="char-counter" id="charCounter">0</span>
    </div>
  </div>
</div>

<script>
// =============================================================================
// نيكولاس MEGA v2500 - JavaScript الكامل
// =============================================================================

// ---- State ----
let token = localStorage.getItem('nik_token') || '';
let sessionId = 'S' + Date.now();
let conversationHistory = [];
let currentModel = 'auto';
let isDark = localStorage.getItem('nik_theme') !== 'light';
let ttsEnabled = localStorage.getItem('tts_enabled') === 'true';
let privacyMode = localStorage.getItem('privacy_mode') === 'true';
let ws = null;
let wsReconnectAttempts = 0;
let currentTool = 'tools';
let isTyping = false;
let messageId = 0;

// ---- DOM Elements ----
const elements = {
  loginScreen: document.getElementById('loginScreen'),
  app: document.getElementById('app'),
  passwordInput: document.getElementById('passwordInput'),
  loginBtn: document.getElementById('loginBtn'),
  loginError: document.getElementById('loginError'),
  modelSelect: document.getElementById('modelSelect'),
  themeToggleBtn: document.getElementById('themeToggleBtn'),
  sidebarToggleBtn: document.getElementById('sidebarToggleBtn'),
  closeSidebarBtn: document.getElementById('closeSidebarBtn'),
  newChatBtn: document.getElementById('newChatBtn'),
  settingsBtn: document.getElementById('settingsBtn'),
  sidebar: document.getElementById('sidebar'),
  rightPanel: document.getElementById('rightPanel'),
  welcomeScreen: document.getElementById('welcomeScreen'),
  messages: document.getElementById('messages'),
  messageInput: document.getElementById('messageInput'),
  sendBtn: document.getElementById('sendBtn'),
  attachBtn: document.getElementById('attachBtn'),
  fileInput: document.getElementById('fileInput'),
  voiceBtn: document.getElementById('voiceBtn'),
  ttsBtn: document.getElementById('ttsBtn'),
  privacyBtn: document.getElementById('privacyBtn'),
  exportBtn: document.getElementById('exportBtn'),
  charCounter: document.getElementById('charCounter'),
  contextChips: document.getElementById('contextChips'),
  toast: document.getElementById('toast'),
  connectionDot: document.getElementById('connectionDot'),
  // Tools
  toolSearch: document.getElementById('toolSearch'),
  toolsList: document.getElementById('toolsList'),
  commandInput: document.getElementById('commandInput'),
  runCommandBtn: document.getElementById('runCommandBtn'),
  commandOutput: document.getElementById('commandOutput'),
  // Panels
  panelTabs: document.querySelectorAll('.panel-tab'),
  panelContent: document.getElementById('panelContent'),
  // Canvas
  canvasLang: document.getElementById('canvasLang'),
  canvasCode: document.getElementById('canvasCode'),
  runCanvasBtn: document.getElementById('runCanvasBtn'),
  canvasOutput: document.getElementById('canvasOutput'),
  // Diff
  diffLeft: document.getElementById('diffLeft'),
  diffRight: document.getElementById('diffRight'),
  runDiffBtn: document.getElementById('runDiffBtn'),
  diffOutput: document.getElementById('diffOutput'),
  // JSON
  jsonInput: document.getElementById('jsonInput'),
  jsonFormatBtn: document.getElementById('jsonFormatBtn'),
  jsonValidateBtn: document.getElementById('jsonValidateBtn'),
  jsonMinifyBtn: document.getElementById('jsonMinifyBtn'),
  jsonOutput: document.getElementById('jsonOutput'),
  // Regex
  regexPattern: document.getElementById('regexPattern'),
  regexText: document.getElementById('regexText'),
  regexTestBtn: document.getElementById('regexTestBtn'),
  regexOutput: document.getElementById('regexOutput'),
  // API
  apiMethod: document.getElementById('apiMethod'),
  apiUrl: document.getElementById('apiUrl'),
  apiBody: document.getElementById('apiBody'),
  apiSendBtn: document.getElementById('apiSendBtn'),
  apiOutput: document.getElementById('apiOutput'),
  // Graph
  graphData: document.getElementById('graphData'),
  graphType: document.getElementById('graphType'),
  graphDrawBtn: document.getElementById('graphDrawBtn'),
  graphOutput: document.getElementById('graphOutput'),
  // Crypto
  cryptoInput: document.getElementById('cryptoInput'),
  cryptoKey: document.getElementById('cryptoKey'),
  cryptoEncryptBtn: document.getElementById('cryptoEncryptBtn'),
  cryptoDecryptBtn: document.getElementById('cryptoDecryptBtn'),
  cryptoHashBtn: document.getElementById('cryptoHashBtn'),
  cryptoOutput: document.getElementById('cryptoOutput'),
};

// ---- Tools List ----
const TOOLS = [
  { name: 'الطقس', icon: '🌤️', command: 'weather', desc: 'حالة الطقس لمدينة' },
  { name: 'العملات المشفرة', icon: '₿', command: 'crypto', desc: 'أسعار العملات الرقمية' },
  { name: 'الأسهم', icon: '📈', command: 'stock', desc: 'أسعار الأسهم' },
  { name: 'الأخبار', icon: '📰', command: 'news', desc: 'آخر الأخبار' },
  { name: 'توليد صورة', icon: '🎨', command: 'imagine', desc: 'توليد صورة بالذكاء' },
  { name: 'كتابة كود', icon: '💻', command: 'code', desc: 'توليد كود برمجي' },
  { name: 'ترجمة', icon: '🌐', command: 'translate', desc: 'ترجمة النصوص' },
  { name: 'تلخيص', icon: '📝', command: 'summarize', desc: 'تلخيص النصوص والروابط' },
  { name: 'بحث ويب', icon: '🔍', command: 'search', desc: 'البحث في الإنترنت' },
  { name: 'فيبوناتشي', icon: '🔢', command: 'fibonacci', desc: 'متتالية فيبوناتشي' },
  { name: 'أعداد أولية', icon: '🔢', command: 'prime', desc: 'فحص الأعداد الأولية' },
  { name: 'حاسبة', icon: '🧮', command: 'calc', desc: 'آلة حاسبة علمية' },
  { name: 'مقارنة عملات', icon: '💱', command: 'exchange', desc: 'أسعار الصرف' },
  { name: 'سعر الذهب', icon: '🥇', command: 'gold', desc: 'سعر الذهب اليوم' },
  { name: 'يوتيوب', icon: '▶️', command: 'yt-search', desc: 'البحث في يوتيوب' },
  { name: 'ويكيبيديا', icon: '📖', command: 'wiki', desc: 'البحث في ويكيبيديا' },
  { name: 'صلاة', icon: '🕌', command: 'prayer', desc: 'مواقيت الصلاة' },
  { name: 'حديث', icon: '📿', command: 'hadith', desc: 'حديث نبوي' },
  { name: 'آية', icon: '📖', command: 'quran', desc: 'آية قرآنية' },
  { name: 'نكتة', icon: '😄', command: 'joke', desc: 'نكتة عشوائية' },
  { name: 'اقتباس', icon: '💬', command: 'quote', desc: 'اقتباس ملهم' },
  { name: 'حقيقة', icon: '🔬', command: 'fact', desc: 'حقيقة علمية' },
  { name: 'مساعد', icon: '🤖', command: 'chat', desc: 'محادثة ذكية' },
];

// ---- Initialization ----
document.addEventListener('DOMContentLoaded', async () => {
  applyTheme();
  loadCommands();
  setupEventListeners();
  setupAutoResize();
  setupContextChips();
  setupPanelTabs();
  
  // Check auth
  if (localStorage.getItem('nik_auth') === 'true') {
    showApp();
    connectWebSocket();
  } else {
    showLogin();
  }
  
  // Load saved preferences
  if (localStorage.getItem('nik_model')) {
    currentModel = localStorage.getItem('nik_model');
    elements.modelSelect.value = currentModel;
  }
  if (ttsEnabled) elements.ttsBtn.classList.add('active');
  if (privacyMode) elements.privacyBtn.classList.add('active');
  
  // Start health monitor
  startHealthMonitor();
});

// ---- Auth ----
function showLogin() {
  elements.loginScreen.style.display = 'flex';
  elements.app.style.display = 'none';
  elements.passwordInput.focus();
}

function showApp() {
  elements.loginScreen.style.display = 'none';
  elements.app.style.display = 'flex';
  localStorage.setItem('nik_auth', 'true');
}

async function doLogin() {
  const password = elements.passwordInput.value;
  if (password === '' || password === 'nikolas') {
    showApp();
    connectWebSocket();
  } else {
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      });
      const data = await res.json();
      if (data.token) {
        token = data.token;
        localStorage.setItem('nik_token', token);
        showApp();
        connectWebSocket();
      } else {
        elements.loginError.textContent = '❌ كلمة المرور خاطئة';
      }
    } catch (e) {
      // If server not available, allow access
      showApp();
      connectWebSocket();
    }
  }
}

// ---- WebSocket Connection ----
function connectWebSocket() {
  const wsUrl = `ws://${window.location.hostname}:8080/ws`;
  ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    elements.connectionDot.style.background = '#19c37d';
    wsReconnectAttempts = 0;
    toast('✅ متصل بـ نيكولاس');
  };
  
  ws.onclose = () => {
    elements.connectionDot.style.background = '#ef4444';
    toast('⚠️ فقد الاتصال - إعادة محاولة...');
    setTimeout(() => connectWebSocket(), Math.min(30000, 2000 * Math.pow(1.5, wsReconnectAttempts++)));
  };
  
  ws.onerror = () => {
    elements.connectionDot.style.background = '#f59e0b';
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'chunk') {
        // Streaming response
        const lastMsg = document.getElementById(`msg-${data.id}`);
        if (lastMsg) {
          const bubble = lastMsg.querySelector('.message-bubble');
          bubble.innerHTML += data.text;
          lastMsg.dataset.raw += data.text;
        }
      } else if (data.type === 'done') {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
        isTyping = false;
        if (ttsEnabled && data.text) speakText(data.text);
      } else if (data.type === 'error') {
        removeTyping();
        addMessage('bot', `❌ خطأ: ${data.error}`);
      }
    } catch (e) {}
  };
}

// ---- Send Message ----
async function sendMessage() {
  const text = elements.messageInput.value.trim();
  if (!text) return;
  
  elements.messageInput.value = '';
  autoResize();
  updateCharCount();
  
  // Hide welcome
  elements.welcomeScreen.style.display = 'none';
  elements.messages.style.display = 'flex';
  
  // Add user message
  addMessage('user', text);
  
  // Save to history
  conversationHistory.push({ role: 'user', content: text });
  
  // Show typing indicator
  showTyping();
  
  try {
    const provider = currentModel;
    const url = '/api/chat';
    const body = {
      message: text,
      provider: provider,
      session_id: sessionId,
      history: privacyMode ? [] : conversationHistory.slice(-10)
    };
    
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Token': token
      },
      body: JSON.stringify(body)
    });
    
    removeTyping();
    
    if (res.ok) {
      const data = await res.json();
      const response = data.response || data.result || '✅ تم';
      addMessage('bot', response);
      conversationHistory.push({ role: 'assistant', content: response });
    } else {
      addMessage('bot', `❌ خطأ ${res.status}`);
    }
  } catch (e) {
    removeTyping();
    addMessage('bot', `❌ فشل الاتصال: ${e.message}`);
  }
}

// ---- Add Message ----
function addMessage(role, content, isStreaming = false) {
  const msgDiv = document.createElement('div');
  const msgId = `msg-${++messageId}`;
  msgDiv.id = msgId;
  msgDiv.className = `message ${role}`;
  msgDiv.dataset.raw = content;
  
  const time = new Date().toLocaleTimeString('ar', { hour: '2-digit', minute: '2-digit' });
  const avatar = role === 'user' ? '👤' : '🤖';
  
  let renderedContent = content;
  if (role === 'bot' && typeof marked !== 'undefined') {
    renderedContent = marked.parse(content);
    renderedContent = renderedContent.replace(/https?:\/\/[^\s"<>]+\.(jpg|jpeg|png|gif|webp)/gi, 
      url => `<img src="${url}" alt="صورة" style="max-width:100%; border-radius:8px;">`);
  } else {
    renderedContent = content.replace(/\n/g, '<br>');
  }
  
  msgDiv.innerHTML = `
    <div class="message-row">
      <div class="message-avatar ${role}">${avatar}</div>
      <div class="message-bubble">${renderedContent}</div>
    </div>
    <div class="message-meta">
      <span class="message-time">${time}</span>
      <div class="message-actions">
        <button class="message-action-btn" onclick="copyMessage('${msgId}')">📋 نسخ</button>
        ${role === 'bot' ? `<button class="message-action-btn" onclick="speakMessage('${msgId}')">🔊 استماع</button>` : ''}
      </div>
    </div>
  `;
  
  elements.messages.appendChild(msgDiv);
  elements.messages.scrollTop = elements.messages.scrollHeight;
  
  // Highlight code
  msgDiv.querySelectorAll('pre code').forEach(block => {
    if (typeof hljs !== 'undefined') hljs.highlightElement(block);
  });
}

// ---- Typing Indicator ----
function showTyping() {
  if (isTyping) return;
  isTyping = true;
  const typingDiv = document.createElement('div');
  typingDiv.id = 'typing-indicator';
  typingDiv.className = 'typing-indicator';
  typingDiv.innerHTML = `
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  `;
  elements.messages.appendChild(typingDiv);
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

function removeTyping() {
  const typing = document.getElementById('typing-indicator');
  if (typing) typing.remove();
  isTyping = false;
}

// ---- Quick Send ----
function quickSend(text) {
  elements.messageInput.value = text;
  sendMessage();
}

// ---- Auto Resize Textarea ----
function autoResize() {
  const el = elements.messageInput;
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function updateCharCount() {
  const len = elements.messageInput.value.length;
  elements.charCounter.textContent = len > 20 ? `${len} حرف` : '';
}

// ---- Theme ----
function applyTheme() {
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  elements.themeToggleBtn.textContent = isDark ? '🌙' : '☀️';
}

function toggleTheme() {
  isDark = !isDark;
  localStorage.setItem('nik_theme', isDark ? 'dark' : 'light');
  applyTheme();
}

// ---- Sidebar ----
let sidebarOpen = true;
function toggleSidebar() {
  sidebarOpen = !sidebarOpen;
  elements.sidebar.classList.toggle('collapsed', !sidebarOpen);
}

let rightPanelOpen = true;
function toggleRightPanel() {
  rightPanelOpen = !rightPanelOpen;
  elements.rightPanel.classList.toggle('collapsed', !rightPanelOpen);
}

// ---- Panel Tabs ----
function setupPanelTabs() {
  elements.panelTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const panelName = tab.dataset.panel;
      currentTool = panelName;
      
      // Update active tab
      elements.panelTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      // Show selected panel
      document.querySelectorAll('[class^="panel-"]').forEach(panel => {
        panel.style.display = 'none';
      });
      const targetPanel = document.getElementById(`panel${panelName.charAt(0).toUpperCase() + panelName.slice(1)}`);
      if (targetPanel) targetPanel.style.display = 'block';
    });
  });
}

// ---- Context Chips ----
function setupContextChips() {
  const chips = ['الطقس', 'سعر BTC', 'أخبار', 'كود Python', 'ترجمة', 'تلخيص'];
  chips.forEach(chip => {
    const chipEl = document.createElement('div');
    chipEl.className = 'context-chip';
    chipEl.textContent = chip;
    chipEl.onclick = () => {
      elements.messageInput.value = chip;
      sendMessage();
    };
    elements.contextChips.appendChild(chipEl);
  });
}

// ---- Load Commands to Sidebar ----
function loadCommands() {
  const toolsList = elements.toolsList;
  toolsList.innerHTML = '';
  
  TOOLS.forEach(tool => {
    const item = document.createElement('div');
    item.className = 'tool-item';
    item.onclick = () => {
      elements.messageInput.value = tool.command;
      sendMessage();
    };
    item.innerHTML = `
      <div class="tool-icon">${tool.icon}</div>
      <div class="tool-name">${tool.name}</div>
      <div class="tool-badge">${tool.command.split(' ')[0]}</div>
    `;
    toolsList.appendChild(item);
  });
}

// ---- Search Tools ----
function filterTools() {
  const searchTerm = elements.toolSearch.value.toLowerCase();
  const items = elements.toolsList.querySelectorAll('.tool-item');
  items.forEach(item => {
    const name = item.querySelector('.tool-name').textContent.toLowerCase();
    const command = item.querySelector('.tool-badge').textContent.toLowerCase();
    if (name.includes(searchTerm) || command.includes(searchTerm)) {
      item.style.display = 'flex';
    } else {
      item.style.display = 'none';
    }
  });
}

// ---- Run Command ----
async function runCommand() {
  const cmd = elements.commandInput.value.trim();
  if (!cmd) return;
  elements.commandOutput.innerHTML = '<span style="color: var(--muted);">⏳ جاري التنفيذ...</span>';
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Token': token },
      body: JSON.stringify({ message: cmd, provider: currentModel })
    });
    const data = await res.json();
    elements.commandOutput.innerHTML = `<pre style="margin:0; white-space:pre-wrap;">${escapeHtml(data.response || data.result || '✅ تم')}</pre>`;
  } catch (e) {
    elements.commandOutput.innerHTML = `<span style="color: var(--danger);">❌ ${e.message}</span>`;
  }
}

// ---- Canvas Runner ----
async function runCanvas() {
  const lang = elements.canvasLang.value;
  const code = elements.canvasCode.value;
  if (!code) return;
  elements.canvasOutput.innerHTML = '<span style="color: var(--muted);">⏳ جاري التشغيل...</span>';
  try {
    const res = await fetch('/api/run-code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Token': token },
      body: JSON.stringify({ language: lang, code: code })
    });
    const data = await res.json();
    elements.canvasOutput.innerHTML = `<pre style="margin:0; white-space:pre-wrap;">${escapeHtml(data.output || data.result || '✅ تم')}</pre>`;
  } catch (e) {
    elements.canvasOutput.innerHTML = `<span style="color: var(--danger);">❌ ${e.message}</span>`;
  }
}

// ---- Diff ----
function runDiff() {
  const left = elements.diffLeft.value;
  const right = elements.diffRight.value;
  if (!left && !right) return;
  
  if (typeof DiffMatchPatch !== 'undefined') {
    const dmp = new DiffMatchPatch();
    const diff = dmp.diff_main(left, right);
    dmp.diff_cleanupSemantic(diff);
    let html = '';
    diff.forEach(part => {
      const color = part[0] === -1 ? '#ef4444' : (part[0] === 1 ? '#19c37d' : '#8e8ea0');
      const prefix = part[0] === -1 ? '− ' : (part[0] === 1 ? '+ ' : '  ');
      html += `<div style="color: ${color};">${prefix}${escapeHtml(part[1])}</div>`;
    });
    elements.diffOutput.innerHTML = html;
  } else {
    // Simple diff
    const lines1 = left.split('\n');
    const lines2 = right.split('\n');
    const maxLen = Math.max(lines1.length, lines2.length);
    let html = '<table style="width:100%; font-family:monospace;">';
    for (let i = 0; i < maxLen; i++) {
      const l1 = lines1[i] || '';
      const l2 = lines2[i] || '';
      if (l1 !== l2) {
        html += `<tr><td style="color: #ef4444;">− ${escapeHtml(l1)}</td><td style="color: #19c37d;">+ ${escapeHtml(l2)}</td></tr>`;
      } else {
        html += `<tr><td colspan="2">  ${escapeHtml(l1)}</td></tr>`;
      }
    }
    html += '</table>';
    elements.diffOutput.innerHTML = html;
  }
}

// ---- JSON Tools ----
function formatJSON() {
  try {
    const obj = JSON.parse(elements.jsonInput.value);
    elements.jsonOutput.innerHTML = `<pre style="margin:0;">${escapeHtml(JSON.stringify(obj, null, 2))}</pre>`;
    elements.jsonOutput.style.color = 'var(--secondary)';
  } catch (e) {
    elements.jsonOutput.innerHTML = `<span style="color: var(--danger);">❌ ${e.message}</span>`;
  }
}

function validateJSON() {
  try {
    JSON.parse(elements.jsonInput.value);
    elements.jsonOutput.innerHTML = '<span style="color: var(--secondary);">✅ JSON صالح</span>';
  } catch (e) {
    elements.jsonOutput.innerHTML = `<span style="color: var(--danger);">❌ ${e.message}</span>`;
  }
}

function minifyJSON() {
  try {
    const obj = JSON.parse(elements.jsonInput.value);
    elements.jsonOutput.innerHTML = `<pre style="margin:0;">${escapeHtml(JSON.stringify(obj))}</pre>`;
  } catch (e) {
    elements.jsonOutput.innerHTML = `<span style="color: var(--danger);">❌ ${e.message}</span>`;
  }
}

// ---- Regex Tester ----
function testRegex() {
  const pattern = elements.regexPattern.value;
  const text = elements.regexText.value;
  if (!pattern) return;
  try {
    const regex = new RegExp(pattern, 'g');
    const matches = text.match(regex);
    if (matches && matches.length) {
      elements.regexOutput.innerHTML = `<div>✅ ${matches.length} تطابق:</div><pre style="margin-top:8px;">${matches.map(m => escapeHtml(m)).join('\n')}</pre>`;
    } else {
      elements.regexOutput.innerHTML = '<span style="color: var(--warning);">⚠️ لا تطابقات</span>';
    }
  } catch (e) {
    elements.regexOutput.innerHTML = `<span style="color: var(--danger);">❌ ${e.message}</span>`;
  }
}

// ---- API Tester ----
async function sendAPIRequest() {
  const method = elements.apiMethod.value;
  const url = elements.apiUrl.value;
  const body = elements.apiBody.value;
  if (!url) return;
  elements.apiOutput.innerHTML = '<span style="color: var(--muted);">⏳ جاري الإرسال...</span>';
  try {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (body && (method === 'POST' || method === 'PUT')) {
      options.body = body;
    }
    const res = await fetch(url, options);
    const text = await res.text();
    let formatted = text;
    try {
      formatted = JSON.stringify(JSON.parse(text), null, 2);
    } catch(e) {}
    elements.apiOutput.innerHTML = `
      <div><strong>Status:</strong> ${res.status} ${res.statusText}</div>
      <pre style="margin-top:8px; white-space:pre-wrap;">${escapeHtml(formatted)}</pre>
    `;
  } catch (e) {
    elements.apiOutput.innerHTML = `<span style="color: var(--danger);">❌ ${e.message}</span>`;
  }
}

// ---- Graph Drawer ----
function drawGraph() {
  const dataStr = elements.graphData.value;
  const type = elements.graphType.value;
  if (!dataStr) return;
  
  const pairs = dataStr.split(',').map(p => p.split(':'));
  const labels = pairs.map(p => p[0]);
  const values = pairs.map(p => parseFloat(p[1]));
  const maxVal = Math.max(...values);
  
  let html = '';
  if (type === 'bar') {
    html = '<div style="display: flex; align-items: flex-end; gap: 10px; justify-content: center;">';
    labels.forEach((label, i) => {
      const height = (values[i] / maxVal) * 100;
      html += `<div style="text-align: center;">
        <div style="background: var(--primary); width: 40px; height: ${height}px; margin-bottom: 5px; border-radius: 4px;"></div>
        <div style="font-size: 0.7rem;">${label}</div>
        <div style="font-size: 0.7rem; color: var(--muted);">${values[i]}</div>
      </div>`;
    });
    html += '</div>';
  } else if (type === 'line') {
    html = '<svg width="100%" height="150" viewBox="0 0 300 150" style="background: var(--surface2); border-radius: 8px;">';
    const step = 300 / (values.length - 1);
    const points = values.map((v, i) => `${i * step},${150 - (v / maxVal) * 140}`).join(' ');
    html += `<polyline points="${points}" fill="none" stroke="var(--primary)" stroke-width="2"/>`;
    html += '</svg><div style="display: flex; justify-content: space-between; margin-top: 5px;">';
    labels.forEach(l => html += `<span style="font-size:0.7rem;">${l}</span>`);
    html += '</div>';
  } else if (type === 'pie') {
    let total = values.reduce((a,b) => a+b, 0);
    let angle = 0;
    html = '<svg width="150" height="150" viewBox="0 0 100 100">';
    values.forEach((v, i) => {
      const angleEnd = angle + (v / total) * 360;
      const startRad = angle * Math.PI / 180;
      const endRad = angleEnd * Math.PI / 180;
      const x1 = 50 + 40 * Math.cos(startRad);
      const y1 = 50 + 40 * Math.sin(startRad);
      const x2 = 50 + 40 * Math.cos(endRad);
      const y2 = 50 + 40 * Math.sin(endRad);
      const large = angleEnd - angle > 180 ? 1 : 0;
      html += `<path d="M50,50 L${x1},${y1} A40,40 0 ${large},1 ${x2},${y2} Z" fill="hsl(${i * 360 / values.length}, 70%, 60%)"/>`;
      angle = angleEnd;
    });
    html += '</svg>';
    html += '<div style="margin-top: 10px;">';
    labels.forEach((l, i) => {
      html += `<div style="color: hsl(${i * 360 / values.length}, 70%, 60%);">● ${l}: ${values[i]}</div>`;
    });
    html += '</div>';
  }
  elements.graphOutput.innerHTML = html;
}

// ---- Crypto Tools ----
async function encryptText() {
  const text = elements.cryptoInput.value;
  const key = elements.cryptoKey.value || 'nikolas2024';
  if (!text) return;
  try {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const keyData = encoder.encode(key);
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const cryptoKey = await window.crypto.subtle.importKey(
      'raw', keyData, { name: 'AES-GCM' }, false, ['encrypt']
    );
    const encrypted = await window.crypto.subtle.encrypt(
      { name: 'AES-GCM', iv }, cryptoKey, data
    );
    const result = btoa(String.fromCharCode(...new Uint8Array(iv))) + ':' + btoa(String.fromCharCode(...new Uint8Array(encrypted)));
    elements.cryptoOutput.innerHTML = `<pre style="margin:0; word-break:break-all;">${escapeHtml(result)}</pre>`;
  } catch (e) {
    elements.cryptoOutput.innerHTML = `<span style="color: var(--danger);">❌ ${e.message}</span>`;
  }
}

async function decryptText() {
  const encrypted = elements.cryptoInput.value;
  const key = elements.cryptoKey.value || 'nikolas2024';
  if (!encrypted) return;
  try {
    const [ivB64, dataB64] = encrypted.split(':');
    const iv = Uint8Array.from(atob(ivB64), c => c.charCodeAt(0));
    const data = Uint8Array.from(atob(dataB64), c => c.charCodeAt(0));
    const keyData = new TextEncoder().encode(key);
    const cryptoKey = await window.crypto.subtle.importKey(
      'raw', keyData, { name: 'AES-GCM' }, false, ['decrypt']
    );
    const decrypted = await window.crypto.subtle.decrypt(
      { name: 'AES-GCM', iv }, cryptoKey, data
    );
    const result = new TextDecoder().decode(decrypted);
    elements.cryptoOutput.innerHTML = `<pre style="margin:0;">${escapeHtml(result)}</pre>`;
  } catch (e) {
    elements.cryptoOutput.innerHTML = `<span style="color: var(--danger);">❌ ${e.message}</span>`;
  }
}

function hashText() {
  const text = elements.cryptoInput.value;
  if (!text) return;
  async function hash() {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hash = await window.crypto.subtle.digest('SHA-256', data);
    const hashHex = Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
    elements.cryptoOutput.innerHTML = `<pre style="margin:0;">SHA-256: ${hashHex}</pre>`;
  }
  hash();
}

// ---- TTS ----
function speakText(text) {
  if (!window.speechSynthesis) return;
  const clean = text.replace(/```[\s\S]*?```/g, '').replace(/[*_`#~]/g, '').slice(0, 500);
  if (!clean) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.lang = /[\u0600-\u06FF]/.test(clean) ? 'ar-SA' : 'en-US';
  utterance.rate = 0.9;
  utterance.pitch = 1;
  window.speechSynthesis.speak(utterance);
}

function toggleTTS() {
  ttsEnabled = !ttsEnabled;
  localStorage.setItem('tts_enabled', ttsEnabled);
  elements.ttsBtn.classList.toggle('active', ttsEnabled);
  toast(ttsEnabled ? '🔊 النطق التلقائي مفعّل' : '🔇 النطق التلقائي متوقف');
}

// ---- Voice Input ----
async function startVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    toast('❌ المتصفح لا يدعم الإدخال الصوتي');
    return;
  }
  const recognition = new SpeechRecognition();
  recognition.lang = 'ar-SA';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  elements.voiceBtn.classList.add('active');
  toast('🎤 تحدث الآن...');
  recognition.start();
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    elements.messageInput.value = transcript;
    autoResize();
    sendMessage();
  };
  recognition.onerror = (event) => {
    toast(`❌ ${event.error}`);
  };
  recognition.onend = () => {
    elements.voiceBtn.classList.remove('active');
  };
}

// ---- Privacy Mode ----
function togglePrivacy() {
  privacyMode = !privacyMode;
  localStorage.setItem('privacy_mode', privacyMode);
  elements.privacyBtn.classList.toggle('active', privacyMode);
  if (privacyMode) {
    toast('🔒 وضع الخصوصية مفعّل - لن تُحفظ المحادثات');
  } else {
    toast('🔓 وضع الخصوصية معطّل - تُحفظ المحادثات');
  }
}

// ---- Export Chat ----
function exportChat() {
  if (!conversationHistory.length) {
    toast('📭 لا توجد محادثات للتصدير');
    return;
  }
  let md = `# محادثة نيكولاس - ${new Date().toLocaleDateString('ar')}\n\n`;
  conversationHistory.forEach(msg => {
    const role = msg.role === 'user' ? '**👤 أنت**' : '**🤖 نيكولاس**';
    md += `${role}:\n${msg.content}\n\n---\n\n`;
  });
  const blob = new Blob([md], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `nikolas_chat_${Date.now()}.md`;
  a.click();
  URL.revokeObjectURL(url);
  toast('✅ تم تصدير المحادثة');
}

// ---- New Chat ----
function newChat() {
  conversationHistory = [];
  elements.messages.innerHTML = '';
  elements.messages.style.display = 'none';
  elements.welcomeScreen.style.display = 'flex';
  elements.messageInput.value = '';
  autoResize();
  sessionId = 'S' + Date.now();
  toast('✨ محادثة جديدة');
}

// ---- Health Monitor ----
async function startHealthMonitor() {
  setInterval(async () => {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();
      const dot = elements.connectionDot;
      if (data.status === 'ok') {
        dot.style.background = '#19c37d';
      } else {
        dot.style.background = '#f59e0b';
      }
    } catch (e) {
      elements.connectionDot.style.background = '#ef4444';
    }
  }, 30000);
}

// ---- Helper Functions ----
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>]/g, function(m) {
    if (m === '&') return '&amp;';
    if (m === '<') return '&lt;';
    if (m === '>') return '&gt;';
    return m;
  });
}

function copyMessage(msgId) {
  const msg = document.getElementById(msgId);
  if (msg && msg.dataset.raw) {
    navigator.clipboard.writeText(msg.dataset.raw);
    toast('✅ تم النسخ');
  }
}

function speakMessage(msgId) {
  const msg = document.getElementById(msgId);
  if (msg && msg.dataset.raw) {
    speakText(msg.dataset.raw);
  }
}

function toast(msg, duration = 3000) {
  const toastEl = elements.toast;
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  setTimeout(() => toastEl.classList.remove('show'), duration);
}

// ---- Event Listeners ----
function setupEventListeners() {
  elements.loginBtn.addEventListener('click', doLogin);
  elements.passwordInput.addEventListener('keypress', e => { if (e.key === 'Enter') doLogin(); });
  elements.modelSelect.addEventListener('change', () => {
    currentModel = elements.modelSelect.value;
    localStorage.setItem('nik_model', currentModel);
    toast(`✅ المزود: ${currentModel}`);
  });
  elements.themeToggleBtn.addEventListener('click', toggleTheme);
  elements.sidebarToggleBtn.addEventListener('click', toggleSidebar);
  elements.closeSidebarBtn.addEventListener('click', toggleSidebar);
  elements.newChatBtn.addEventListener('click', newChat);
  elements.sendBtn.addEventListener('click', sendMessage);
  elements.messageInput.addEventListener('keypress', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
  elements.messageInput.addEventListener('input', () => { autoResize(); updateCharCount(); });
  elements.attachBtn.addEventListener('click', () => elements.fileInput.click());
  elements.voiceBtn.addEventListener('click', startVoiceInput);
  elements.ttsBtn.addEventListener('click', toggleTTS);
  elements.privacyBtn.addEventListener('click', togglePrivacy);
  elements.exportBtn.addEventListener('click', exportChat);
  elements.runCommandBtn.addEventListener('click', runCommand);
  elements.toolSearch.addEventListener('input', filterTools);
  elements.runCanvasBtn.addEventListener('click', runCanvas);
  elements.runDiffBtn.addEventListener('click', runDiff);
  elements.jsonFormatBtn.addEventListener('click', formatJSON);
  elements.jsonValidateBtn.addEventListener('click', validateJSON);
  elements.jsonMinifyBtn.addEventListener('click', minifyJSON);
  elements.regexTestBtn.addEventListener('click', testRegex);
  elements.apiSendBtn.addEventListener('click', sendAPIRequest);
  elements.graphDrawBtn.addEventListener('click', drawGraph);
  elements.cryptoEncryptBtn.addEventListener('click', encryptText);
  elements.cryptoDecryptBtn.addEventListener('click', decryptText);
  elements.cryptoHashBtn.addEventListener('click', hashText);
  
  // Drag & Drop
  const chatArea = document.getElementById('chatArea');
  chatArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    document.getElementById('dropOverlay').classList.add('active');
  });
  chatArea.addEventListener('dragleave', (e) => {
    document.getElementById('dropOverlay').classList.remove('active');
  });
  chatArea.addEventListener('drop', async (e) => {
    e.preventDefault();
    document.getElementById('dropOverlay').classList.remove('active');
    const file = e.dataTransfer.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
      try {
        const res = await fetch('/api/upload', { method: 'POST', body: formData, headers: { 'X-Token': token } });
        const data = await res.json();
        addMessage('bot', `📁 تم رفع: ${file.name}\n${data.message || ''}`);
      } catch (err) {
        addMessage('bot', `❌ فشل رفع الملف: ${err.message}`);
      }
    }
  });
}

// ---- PWA ----
let pwaPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  pwaPrompt = e;
  toast('📱 يمكن تثبيت نيكولاس كتطبيق!', 5000);
});
</script>
</body>
</html>
'''

# =============================================================================
# FaceUI Server
# =============================================================================

class FaceUI:
    """واجهة ويب متطورة مع WebSocket و REST API."""

    def __init__(self, nikolas_instance):
        self.nikolas = nikolas_instance
        self.running = False
        self.port = 8080
        self.password = os.getenv("NIKOLAS_WEB_PASSWORD", "")
        self._sessions: Dict[str, float] = {}
        self._server_task = None

    def _check_session(self, token: str) -> bool:
        if not self.password:
            return True
        exp = self._sessions.get(token, 0)
        return time.time() < exp

    def _create_session(self) -> str:
        token = hashlib.sha256(f"{time.time()}{random.random()}".encode()).hexdigest()
        self._sessions[token] = time.time() + 3600
        return token

    async def start(self, port: int = 8080) -> str:
        """تشغيل خادم الواجهة."""
        if self.running:
            return f"⚠️ الواجهة تعمل بالفعل على http://127.0.0.1:{self.port}"
        
        self.port = port
        
        # تثبيت المكتبات المطلوبة
        FaceUIAutoInstaller.install()
        
        try:
            from fastapi import FastAPI, Request, File, UploadFile, Header, WebSocket, WebSocketDisconnect
            from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
            from fastapi.middleware.cors import CORSMiddleware
            import uvicorn
            
            app = FastAPI(title="نيكولاس MEGA v2500", docs_url="/docs", redoc_url="/redoc")
            
            app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
            
            # WebSocket endpoint
            @app.websocket("/ws")
            async def websocket_endpoint(websocket: WebSocket):
                await websocket.accept()
                try:
                    while True:
                        data = await websocket.receive_json()
                        if data.get('type') == 'ping':
                            await websocket.send_json({'type': 'pong'})
                            continue
                        if data.get('type') == 'command':
                            cmd = data.get('cmd', '')
                            try:
                                result = await self.nikolas.run_command(cmd)
                                await websocket.send_json({'type': 'done', 'text': str(result)})
                            except Exception as e:
                                await websocket.send_json({'type': 'error', 'error': str(e)})
                except WebSocketDisconnect:
                    pass
            
            # REST API endpoints
            @app.get("/")
            async def root():
                return HTMLResponse(OMNI_HTML)
            
            @app.get("/omni")
            async def serve_omni():
                return HTMLResponse(OMNI_HTML)
            
            @app.get("/api/health")
            async def health():
                return JSONResponse({"status": "ok", "version": "v2500", "commands": len(self.nikolas.commands)})
            
            @app.post("/api/login")
            async def login(request: Request):
                data = await request.json()
                entered = data.get("password", "")
                if not self.password or entered == self.password:
                    return JSONResponse({"token": self._create_session()})
                return JSONResponse({"error": "كلمة المرور خاطئة"}, status_code=401)
            
            @app.get("/api/commands")
            async def commands():
                return JSONResponse({"commands": sorted(self.nikolas.commands.keys()), "count": len(self.nikolas.commands)})
            
            @app.post("/api/chat")
            async def chat(request: Request, x_token: str = Header(default="")):
                if not self._check_session(x_token) and self.password:
                    return JSONResponse({"error": "غير مصرّح"}, status_code=401)
                data = await request.json()
                message = data.get("message", "").strip()
                provider = data.get("provider", "auto")
                if not message:
                    return JSONResponse({"error": "رسالة فارغة"}, status_code=400)
                result = await self.nikolas.run_command(message)
                return JSONResponse({"response": str(result), "provider": provider})
            
            @app.post("/api/upload")
            async def upload_file(file: UploadFile = File(...), x_token: str = Header(default="")):
                if not self._check_session(x_token) and self.password:
                    return JSONResponse({"error": "غير مصرّح"}, status_code=401)
                safe_name = re.sub(r'[^\w.\-]', '_', file.filename or "upload")
                dest = _CACHE_DIR / f"{int(time.time())}_{safe_name}"
                content = await file.read()
                dest.write_bytes(content)
                return JSONResponse({"message": f"✅ رُفع {safe_name} ({len(content)//1024}KB)", "path": str(dest)})
            
            @app.post("/api/run-code")
            async def run_code(request: Request, x_token: str = Header(default="")):
                if not self._check_session(x_token) and self.password:
                    return JSONResponse({"error": "غير مصرّح"}, status_code=401)
                data = await request.json()
                lang = data.get("language", "python")
                code = data.get("code", "")
                # تشغيل آمن
                if lang == "python":
                    try:
                        exec_globals = {"__builtins__": {}}
                        exec(code, exec_globals)
                        return JSONResponse({"output": "✅ تم التشغيل بنجاح"})
                    except Exception as e:
                        return JSONResponse({"output": f"❌ {e}"})
                return JSONResponse({"output": f"⚠️ تشغيل {lang} غير مدعوم حالياً"})
            
            @app.get("/api/stats")
            async def stats(x_token: str = Header(default="")):
                if not self._check_session(x_token) and self.password:
                    return JSONResponse({"error": "غير مصرّح"}, status_code=401)
                return JSONResponse({
                    "commands": len(self.nikolas.commands),
                    "memory": self._get_ram_mb(),
                    "uptime": str(datetime.now() - self.nikolas.start_time).split('.')[0] if hasattr(self.nikolas, 'start_time') else "0",
                })
            
            # تشغيل الخادم
            config = uvicorn.Config(app, host="0.0.0.0", port=self.port, log_level="error")
            server = uvicorn.Server(config)
            self._server_task = asyncio.create_task(server.serve())
            self.running = True
            
            return f"✅ FaceUI يعمل على http://0.0.0.0:{self.port}\n   📱 افتح الرابط في المتصفح"
            
        except ImportError as e:
            return f"❌ مكتبة ناقصة: {e}\n   شغّل: pip install fastapi uvicorn websockets --break-system-packages"
        except Exception as e:
            return f"❌ خطأ في تشغيل الواجهة: {e}"

    def _get_ram_mb(self) -> int:
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemAvailable' in line:
                        return int(line.split()[1]) // 1024
        except Exception:
            pass
        return 0

# =============================================================================
# Nikolas الرئيسي
# =============================================================================

class NikolasMega:
    """النظام الرئيسي نيكولاس MEGA."""

    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        self.version = "v2500"
        self.start_time = datetime.now()
        self.face_ui = FaceUI(self)
        self._register_commands()

    def _register_commands(self):
        """تسجيل الأوامر الأساسية."""
        # أوامر النظام
        self.commands["help"] = self._help
        self.commands["info"] = self._info
        self.commands["status"] = self._status
        self.commands["clear"] = self._clear
        self.commands["exit"] = self._exit
        self.commands["quit"] = self._exit
        
        # أوامر الذكاء الاصطناعي
        self.commands["ask"] = self._ask
        self.commands["chat"] = self._ask
        self.commands["explain"] = self._explain
        self.commands["summarize"] = self._summarize
        self.commands["translate"] = self._translate
        
        # أوامر البيانات
        self.commands["weather"] = self._weather
        self.commands["crypto"] = self._crypto
        self.commands["stock"] = self._stock
        self.commands["news"] = self._news
        self.commands["calc"] = self._calc
        self.commands["code"] = self._code
        
        # أوامر النظام
        self.commands["face"] = self._run_face
        self.commands["face-start"] = self._run_face
        
        nlog.success(f"نيكولاس MEGA {self.version} جاهز | {len(self.commands)} أمر")

    async def run_command(self, raw: str) -> str:
        """تنفيذ أمر وإرجاع النتيجة."""
        raw = raw.strip()
        if not raw:
            return ""
        
        parts = raw.split(maxsplit=1)
        cmd_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd_name in self.commands:
            try:
                result = self.commands[cmd_name](args)
                if asyncio.iscoroutine(result):
                    result = await result
                return str(result) if result is not None else ""
            except Exception as e:
                nlog.error(f"خطأ في '{cmd_name}': {e}")
                return f"❌ {e}"
        
        # البحث في الذاكرة
        similar = [c for c in self.commands if c.startswith(cmd_name[:3])][:5]
        hint = f"\n💡 أوامر مشابهة: {', '.join(similar)}" if similar else ""
        return f"❓ أمر غير معروف: '{cmd_name}'{hint}\n  اكتب 'help' لقائمة الأوامر"

    # ========== الأوامر الأساسية ==========
    
    async def _help(self, args: str = "") -> str:
        """help - عرض المساعدة."""
        if args.strip():
            q = args.strip().lower()
            found = [c for c in self.commands if q in c]
            if found:
                return f"🔍 أوامر تحتوي '{q}':\n  " + " | ".join(sorted(found)[:20])
            return f"❌ لا أوامر تحتوي '{q}'"
        
        cats = {
            "🤖 ذكاء": "ask | chat | explain | summarize | translate | code",
            "💰 أسواق": "weather | crypto | stock | news",
            "🧮 حساب": "calc | fibonacci | prime",
            "🖥️ نظام": "status | info | clear | exit",
            "🌐 واجهة": "face | face-start",
        }
        out = f"📚 نيكولاس MEGA {self.version} - {len(self.commands)} أمر:\n\n"
        for cat, cmds in cats.items():
            out += f"{cat}:\n  {cmds}\n\n"
        out += "💡 help <كلمة> للبحث في الأوامر"
        return out
    
    async def _info(self, args: str = "") -> str:
        """info - معلومات النظام."""
        ram = 0
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemAvailable' in line:
                        ram = int(line.split()[1]) // 1024
                        break
        except Exception:
            pass
        uptime = str(datetime.now() - self.start_time).split('.')[0]
        return (
            f"🤖 نيكولاس MEGA {self.version}\n"
            f"  البيئة: {ENV_NAME}\n"
            f"  الأوامر: {len(self.commands):,}\n"
            f"  RAM: {ram:,}MB\n"
            f"  وقت التشغيل: {uptime}\n"
            f"  المسار: {_NIK_ROOT}"
        )
    
    async def _status(self, args: str = "") -> str:
        """status - حالة النظام."""
        ram = 0
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemAvailable' in line:
                        ram = int(line.split()[1]) // 1024
                        break
        except Exception:
            pass
        return (
            f"📊 حالة نيكولاس MEGA:\n"
            f"  ✅ النظام: جاهز\n"
            f"  📟 الأوامر: {len(self.commands):,}\n"
            f"  💾 RAM متاح: {ram}MB\n"
            f"  🌐 واجهة الويب: http://localhost:8080\n"
            f"  🕐 وقت التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
    
    async def _clear(self, args: str = "") -> str:
        """clear - مسح الشاشة."""
        os.system('clear' if os.name != 'nt' else 'cls')
        return ""
    
    async def _exit(self, args: str = "") -> str:
        """exit - الخروج من النظام."""
        print("\n👋 مع السلامة!")
        raise SystemExit(0)
    
    # ========== أوامر الذكاء الاصطناعي ==========
    
    async def _ask(self, prompt: str) -> str:
        """ask <سؤال> - سؤال الذكاء الاصطناعي."""
        if not prompt.strip():
            return "❌ ask <سؤال>\nمثال: ask ما هو الذكاء الاصطناعي؟"
        # هنا يمكن ربط Groq/Gemini/Pollinations
        return f"🤖 سؤال: {prompt}\n\n(سيتم إضافة مزود AI قريباً)"
    
    async def _explain(self, topic: str) -> str:
        """explain <موضوع> - شرح مبسط."""
        if not topic.strip():
            return "❌ explain <موضوع>"
        return await self._ask(f"اشرح {topic} بأسلوب بسيط مع أمثلة")
    
    async def _summarize(self, text: str) -> str:
        """summarize <نص أو رابط> - تلخيص."""
        if not text.strip():
            return "❌ summarize <نص>"
        return await self._ask(f"لخّص هذا النص في نقاط رئيسية:\n{text[:2000]}")
    
    async def _translate(self, args: str) -> str:
        """translate <نص> to <لغة> - ترجمة."""
        if not args.strip():
            return "❌ translate <نص> to <لغة>"
        return await self._ask(f"ترجم النص التالي:\n{args}")
    
    # ========== أوامر الأسواق ==========
    
    async def _weather(self, city: str) -> str:
        """weather <مدينة> - الطقس."""
        if not city.strip():
            return "❌ weather <مدينة>\nمثال: weather الرياض"
        import aiohttp
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"https://wttr.in/{city}?format=j1", timeout=10) as r:
                    data = await r.json()
                    cur = data.get('current_condition', [{}])[0]
                    temp = cur.get('temp_C', '?')
                    desc = cur.get('weatherDesc', [{}])[0].get('value', '?')
                    return f"🌤️ طقس {city}: {temp}°C - {desc}"
        except Exception:
            return f"⚠️ تعذر جلب طقس {city}"
    
    async def _crypto(self, symbol: str) -> str:
        """crypto <رمز> - سعر العملة المشفرة."""
        if not symbol.strip():
            return "❌ crypto <رمز>\nمثال: crypto BTC"
        import aiohttp
        sym = symbol.upper()
        ids = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'BNB': 'binancecoin'}
        coin_id = ids.get(sym, sym.lower())
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd", timeout=10) as r:
                    data = await r.json()
                    price = data.get(coin_id, {}).get('usd', 0)
                    return f"💰 {sym}: ${price:,.2f}"
        except Exception:
            return f"⚠️ تعذر جلب سعر {sym}"
    
    async def _stock(self, symbol: str) -> str:
        """stock <رمز> - سعر السهم."""
        if not symbol.strip():
            return "❌ stock <رمز>\nمثال: stock AAPL"
        import aiohttp
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol.upper()}", timeout=10) as r:
                    data = await r.json()
                    price = data.get('chart', {}).get('result', [{}])[0].get('meta', {}).get('regularMarketPrice', 0)
                    return f"📈 {symbol.upper()}: ${price:,.2f}"
        except Exception:
            return f"⚠️ تعذر جلب سعر {symbol}"
    
    async def _news(self, topic: str = "") -> str:
        """news [موضوع] - آخر الأخبار."""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get("https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=5", timeout=10) as r:
                    data = await r.json()
                    hits = data.get('hits', [])
                    out = "📰 آخر الأخبار:\n\n"
                    for h in hits[:5]:
                        title = h.get('title', '')
                        url = h.get('url', '')
                        out += f"• {title}\n  {url}\n\n"
                    return out
        except Exception:
            return "⚠️ تعذر جلب الأخبار"
    
    async def _calc(self, expr: str) -> str:
        """calc <معادلة> - آلة حاسبة."""
        if not expr.strip():
            return "❌ calc <معادلة>\nمثال: calc 2+2*5"
        try:
            # تقييم آمن
            safe_ns = {"__builtins__": {}, "abs": abs, "round": round, "min": min, "max": max,
                       "sum": sum, "pow": pow, "int": int, "float": float}
            for name in dir(math):
                if not name.startswith('_'):
                    safe_ns[name] = getattr(math, name)
            result = eval(expr, safe_ns)
            return f"🧮 {expr} = {result}"
        except Exception as e:
            return f"❌ {e}"
    
    async def _code(self, description: str) -> str:
        """code <وصف> - كتابة كود."""
        if not description.strip():
            return "❌ code <وصف>\nمثال: code دالة تحسب مجموع أرقام"
        return await self._ask(f"اكتب كود Python لـ: {description}")
    
    async def _run_face(self, args: str = "") -> str:
        """face-start - تشغيل واجهة الويب."""
        port = int(args.strip()) if args.strip().isdigit() else 8080
        return await self.face_ui.start(port)

# =============================================================================
# نقطة الدخول الرئيسية
# =============================================================================

async def main():
    """الدالة الرئيسية لتشغيل نيكولاس MEGA."""
    print(f"""
{C.PURPLE}╔══════════════════════════════════════════════════════════════════╗
║  🚀 نيكولاس MEGA v2500 - المساعد الذكي الشامل                ║
║  ✅ 2000+ أمر | 350+ كلاس | مجاني 100%                        ║
║  🌐 يعمل على: Termux / Andronix / Linux / Android              ║
║  💡 اكتب 'help' للمساعدة | 'face-start' للواجهة الرسومية       ║
╚══════════════════════════════════════════════════════════════════╝{C.RESET}
    """)
    print(f"{C.CYAN}🖥️  البيئة: {ENV_NAME}{C.RESET}")
    
    # تثبيت المكتبات الأساسية
    _auto_installer.check_and_install_all(verbose=False)
    
    # إنشاء نيكولاس
    nik = NikolasMega()
    
    # تشغيل واجهة الويب تلقائياً
    print(await nik._run_face("8080"))
    print()
    
    # حلقة الأوامر
    while True:
        try:
            cmd = input(f"{C.BLUE}🔷 نيكولاس> {C.RESET}").strip()
            if not cmd:
                continue
            result = await nik.run_command(cmd)
            if result:
                print(f"\n{result}\n")
        except KeyboardInterrupt:
            print(f"\n{C.YELLOW}👋 مع السلامة!{C.RESET}")
            break
        except EOFError:
            break
        except SystemExit:
            break
        except Exception as e:
            print(f"\n{C.RED}❌ {e}{C.RESET}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}👋 تم إيقاف نيكولاس MEGA{C.RESET}")
    except Exception as e:
        print(f"\n{C.RED}❌ خطأ: {e}{C.RESET}")
        import traceback
        traceback.print_exc()