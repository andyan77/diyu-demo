#!/usr/bin/env python3
"""够用的 CDP over WebSocket 客户端（无第三方依赖）。

本机没有 playwright / puppeteer / ws，只有 playwright 缓存里的 chromium 二进制。
第 2–7 轮就是因为「本机无浏览器自动化能力」把画布证据一直挂在 NOT_VERIFIED。
浏览器在，缺的只是一个 WebSocket 客户端——那是一百行的事，不是能力缺口。
"""
import base64
import json
import os
import socket
import struct
import subprocess
import tempfile
import time
import urllib.request

CHROME = os.path.expanduser("~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome")


class WS:
    def __init__(self, url):
        assert url.startswith("ws://")
        rest = url[5:]
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.s = socket.create_connection((host, int(port)), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
               f"Sec-WebSocket-Version: 13\r\n\r\n")
        self.s.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        assert b"101" in buf.split(b"\r\n")[0], buf[:200]
        self.buf = buf.split(b"\r\n\r\n", 1)[1]
        self._id = 0

    def _recv(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(65536)
            if not chunk:
                raise ConnectionError("ws closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, obj):
        payload = json.dumps(obj).encode()
        head = bytes([0x81])
        n = len(payload)
        mask = os.urandom(4)
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 65536:
            head += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            head += bytes([0x80 | 127]) + struct.pack(">Q", n)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.s.sendall(head + mask + masked)

    def recv(self):
        """返回一条完整消息（自动拼分片，自动应答 ping）。"""
        data = b""
        while True:
            b0, b1 = self._recv(2)
            fin, opcode = b0 & 0x80, b0 & 0x0F
            n = b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._recv(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._recv(8))[0]
            payload = self._recv(n) if n else b""
            if opcode == 0x9:                       # ping → pong
                self.s.sendall(bytes([0x8A, 0x80]) + os.urandom(4))
                continue
            if opcode == 0x8:
                raise ConnectionError("ws close frame")
            data += payload
            if fin:
                return json.loads(data.decode())

    def call(self, method, params=None, timeout=120):
        self._id += 1
        mid = self._id
        self.send({"id": mid, "method": method, "params": params or {}})
        t0 = time.time()
        while time.time() - t0 < timeout:
            msg = self.recv()
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
        raise TimeoutError(method)

    def evaluate(self, expr, timeout=60):
        r = self.call("Runtime.evaluate",
                      {"expression": expr, "returnByValue": True, "awaitPromise": True},
                      timeout=timeout)
        if r.get("exceptionDetails"):
            raise RuntimeError(r["exceptionDetails"].get("text"))
        return r["result"].get("value")


class Browser:
    def __init__(self, port=9333, width=2400, height=1500):
        assert os.path.exists(CHROME), CHROME
        self.dir = tempfile.mkdtemp(prefix="cdp_profile_")
        self.proc = subprocess.Popen(
            [CHROME, "--headless=new", f"--remote-debugging-port={port}",
             "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
             "--hide-scrollbars", f"--window-size={width},{height}",
             f"--user-data-dir={self.dir}", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.port = port
        target = None
        for _ in range(60):
            time.sleep(0.5)
            try:
                raw = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5).read()
                pages = [t for t in json.loads(raw) if t.get("type") == "page"]
                if pages:
                    target = pages[0]
                    break
            except Exception:                                  # noqa: BLE001
                continue
        assert target, "chromium 没起来或调试端口不通"
        self.ws = WS(target["webSocketDebuggerUrl"])
        self.ws.call("Page.enable")
        self.ws.call("Runtime.enable")
        self.ws.call("Network.enable")

    def goto(self, url, settle=2.0):
        self.ws.call("Page.navigate", {"url": url}, timeout=120)
        time.sleep(settle)

    def wait_for(self, expr, timeout=90, every=1.0):
        t0 = time.time()
        last = None
        while time.time() - t0 < timeout:
            try:
                last = self.ws.evaluate(expr)
            except Exception as e:                             # noqa: BLE001
                last = f"eval error: {e}"
            if last:
                return last
            time.sleep(every)
        return last

    def screenshot(self, path, full=True):
        r = self.ws.call("Page.captureScreenshot",
                         {"format": "png", "captureBeyondViewport": bool(full)}, timeout=180)
        with open(path, "wb") as f:
            f.write(base64.b64decode(r["data"]))
        return os.path.getsize(path)

    def close(self):
        try:
            self.proc.terminate()
            self.proc.wait(timeout=10)
        except Exception:                                       # noqa: BLE001
            self.proc.kill()
