#!/usr/bin/env python3
"""
auto_assistant.py
Assistente de automação tipo "ChatGPT" para terminal.

Funcionalidades:
- Chat interativo (usa OpenAI se OPENAI_API_KEY estiver configurada; senão usa fallback)
- Memória simples (salva/recupera notas)
- Histórico de conversas salvo em JSON
- Comandos úteis: /exec (executa comando shell), /find (procura texto em arquivos locais),
  /summarize (resume texto - usa OpenAI se disponível), /copy (copiar senha/texto para clipboard),
  /remember (salvar nota), /recall (listar notas)
- Saída colorida (colorama)
"""

import os
import sys
import json
import shlex
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    import openai
except Exception:
    openai = None

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
except Exception:
    # fallback no colors if colorama não instalado
    class Dummy:
        def __getattr__(self, name): return ""
    Fore = Style = Dummy()

try:
    import pyperclip
except Exception:
    pyperclip = None

# ---------- Configurações ----------
DATA_DIR = Path.home() / ".auto_assistant"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"
MEMORY_FILE = DATA_DIR / "memory.json"
MAX_CHAT_HISTORY = 20  # quantas mensagens manter em contexto

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # use .env or export OPENAI_API_KEY=...

if OPENAI_API_KEY and openai:
    openai.api_key = OPENAI_API_KEY

# ---------- Utilitários I/O ----------
def load_json(path: Path) -> Any:
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_json(path: Path, data: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- Histórico e Memória ----------
def append_history(role: str, text: str):
    history = load_json(HISTORY_FILE)
    history.append({"ts": datetime.utcnow().isoformat(), "role": role, "text": text})
    # truncate to reasonable length on disk
    if len(history) > 1000:
        history = history[-1000:]
    save_json(HISTORY_FILE, history)

def get_recent_messages(n=MAX_CHAT_HISTORY) -> List[Dict[str, str]]:
    history = load_json(HISTORY_FILE)
    # map to chat messages style for OpenAI (user/assistant)
    msgs = []
    for item in history[-n:]:
        role = "user" if item["role"] == "user" else "assistant"
        msgs.append({"role": role, "content": item["text"]})
    return msgs

def remember_note(title: str, content: str):
    mem = load_json(MEMORY_FILE) or []
    mem.append({"ts": datetime.utcnow().isoformat(), "title": title, "content": content})
    save_json(MEMORY_FILE, mem)

def recall_notes(limit: int = 20):
    mem = load_json(MEMORY_FILE) or []
    for i, item in enumerate(mem[-limit:], start=1):
        print(Fore.CYAN + f"[{i}] {item['title']} - {item['ts']}")
        print("    ", item['content'])

# ---------- Shell Exec ----------
def run_shell(cmd: str) -> str:
    try:
        # cuidado com segurança — este utilitário executará comandos do sistema
        completed = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        out = completed.stdout.strip()
        err = completed.stderr.strip()
        if err:
            return f"STDERR:\n{err}\n\nSTDOUT:\n{out}"
        return out or "(sem saída)"
    except Exception as e:
        return f"Erro ao executar: {e}"

# ---------- Busca simples em arquivos locais ----------
def find_in_files(root: str, pattern: str, max_matches=20) -> List[str]:
    root_path = Path(root).expanduser()
    results = []
    for p in root_path.rglob("*"):
        if p.is_file() and p.suffix in ['.txt', '.md', '.py', '.json', '.log']:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                if pattern.lower() in text.lower():
                    snippet_index = text.lower().find(pattern.lower())
                    start = max(0, snippet_index - 40)
                    end = min(len(text), snippet_index + len(pattern) + 40)
                    snippet = text[start:end].replace("\n", " ")
                    results.append(f"{p}: ...{snippet}...")
                    if len(results) >= max_matches:
                        break
            except Exception:
                continue
    return results

# ---------- Summarizer (fallback simples) ----------
def extractive_summary(text: str, max_sentences: int = 3) -> str:
    # implementação simples: ranking por frequência de palavras
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(sentences) <= max_sentences:
        return text.strip()
    # score each sentence by word frequency
    words = re.findall(r'\w+', text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    scores = []
    for s in sentences:
        s_words = re.findall(r'\w+', s.lower())
        score = sum(freq.get(w, 0) for w in s_words)
        scores.append((score, s))
    scores.sort(reverse=True)
    top = [s for _, s in scores[:max_sentences]]
    return " ".join(top)

# ---------- OpenAI wrapper (se opcionalmente disponível) ----------
def openai_chat(prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
    if not (openai and OPENAI_API_KEY):
        return None
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        # include recent messages for context
        messages.extend(get_recent_messages())
        messages.append({"role": "user", "content": prompt})
        # call OpenAI ChatCompletion (GPT-3.5/4 style)
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini" if "gpt-4o-mini" in openai.Model.list().__repr__() else "gpt-3.5-turbo",
            messages=messages,
            max_tokens=800,
            temperature=0.2,
        )
        text = resp['choices'][0]['message']['content'].strip()
        return text
    except Exception as e:
        return f"(Erro OpenAI: {e})"

# ---------- Chat fallback (simples) ----------
def fallback_reply(user_text: str) -> str:
    txt = user_text.lower()
    # intenções simples
    if any(w in txt for w in ["hora", "que horas", "horário"]):
        return f"São {datetime.now().strftime('%H:%M:%S')}."
    if any(w in txt for w in ["data", "que dia", "hoje"]):
        return f"Hoje é {datetime.now().strftime('%Y-%m-%d')}."
    if "ajuda" in txt or "o que você faz" in txt:
        return "Posso: conversar, executar comandos (/exec), procurar arquivos (/find), salvar notas (/remember), listar notas (/recall), resumir textos (/summarize). Use /help para ver comandos."
    if txt.strip().startswith("ping"):
        return "pong"
    # fallback trivial: eco com dica
    return "Interessante — conte mais ou use /help para ver comandos."

# ---------- Interface principal ----------
WELCOME = f"""
{Fore.GREEN}AutoAssistant — terminal bot (foda)
{Style.RESET_ALL}Comandos:
  /help           Mostrar ajuda
  /exit           Sair
  /exec <cmd>     Executar comando shell
  /find <root> <pattern>   Procurar padrão em arquivos (root = . ou ~/docs)
  /remember <title>         Salvar nota rápida; depois digite conteúdo
  /recall                 Listar últimas notas
  /history               Ver histórico de chat breve
  /summarize [file|text]  Resumir arquivo ou texto (usa OpenAI se disponível)
  /copy <text>           Copiar texto para clipboard (pyperclip)
  /chat <mensagem>       Mensagem direta (sem contexto adicional)
  /config                Mostrar config (OPENAI ativo?)
Digite sua pergunta normalmente para conversar.
"""

def print_help():
    print(WELCOME)

def command_loop():
    print(WELCOME)
    while True:
        try:
            raw = input(Fore.YELLOW + "\nVocê> " + Style.RESET_ALL)
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break
        if not raw.strip():
            continue

        if raw.startswith("/"):
            parts = shlex.split(raw)
            cmd = parts[0].lower()
            args = parts[1:]
            if cmd == "/help":
                print_help()
            elif cmd == "/exit":
                print("Até mais — sessão encerrada.")
                break
            elif cmd == "/exec":
                if not args:
                    print("Use: /exec <comando shell>")
                    continue
                cmdline = " ".join(args)
                print(Fore.MAGENTA + run_shell(cmdline))
                append_history("assistant", f"[exec] {cmdline}")
            elif cmd == "/find":
                if len(args) < 2:
                    print("Use: /find <root> <pattern>")
                    continue
                root, pattern = args[0], " ".join(args[1:])
                print(f"Procurando '{pattern}' em {root} ...")
                hits = find_in_files(root, pattern)
                if not hits:
                    print(Fore.RED + "Nenhum resultado encontrado.")
                else:
                    for h in hits:
                        print(Fore.CYAN + h)
                append_history("assistant", f"[find] {root} {pattern}")
            elif cmd == "/remember":
                if not args:
                    print("Use: /remember <title>")
                    continue
                title = " ".join(args)
                print("Digite o conteúdo da nota. Termine com uma linha vazia.")
                lines = []
                while True:
                    line = input()
                    if line == "":
                        break
                    lines.append(line)
                content = "\n".join(lines).strip()
                remember_note(title, content)
                print(Fore.GREEN + "Nota salva.")
                append_history("assistant", f"[remember] {title}")
            elif cmd == "/recall":
                recall_notes()
            elif cmd == "/history":
                h = load_json(HISTORY_FILE)
                for item in h[-50:]:
                    role = item['role']
                    ts = item['ts']
                    text = item['text']
                    print(f"[{ts}] {role}: {text}")
            elif cmd == "/summarize":
                if not args:
                    print("Use: /summarize <path_to_file>  OR  /summarize text:<your text>")
                    continue
                arg0 = args[0]
                if arg0.startswith("text:"):
                    text = raw.partition("text:")[2]
                    if OPENAI_API_KEY and openai:
                        ans = openai_chat(f"Resuma o texto a seguir em 3 frases:\n\n{text}")
                        print(Fore.GREEN + ans)
                        append_history("assistant", "[summarize] text")
                    else:
                        print(Fore.GREEN + extractive_summary(text))
                        append_history("assistant", "[summarize] text (local)")
                else:
                    path = Path(arg0).expanduser()
                    if not path.exists():
                        print(Fore.RED + "Arquivo não encontrado:", path)
                        continue
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    if OPENAI_API_KEY and openai:
                        ans = openai_chat("Resuma o texto a seguir em 5-7 frases:\n\n" + text)
                        print(Fore.GREEN + ans)
                        append_history("assistant", f"[summarize] {path}")
                    else:
                        print(Fore.GREEN + extractive_summary(text, max_sentences=5))
                        append_history("assistant", f"[summarize] {path} (local)")
            elif cmd == "/copy":
                if pyperclip is None:
                    print(Fore.RED + "pyperclip não instalado. Instale com: pip install pyperclip")
                    continue
                to_copy = " ".join(args)
                pyperclip.copy(to_copy)
                print(Fore.GREEN + "Texto copiado para área de transferência.")
                append_history("assistant", "[copy]")
            elif cmd == "/chat":
                if not args:
                    print("Use: /chat <mensagem>")
                    continue
                prompt = " ".join(args)
                # try OpenAI
                if OPENAI_API_KEY and openai:
                    ans = openai_chat(prompt)
                    if ans is None:
                        ans = "(erro ao chamar OpenAI)"
                else:
                    ans = fallback_reply(prompt)
                print(Fore.GREEN + "Assistente> " + ans)
                append_history("user", prompt)
                append_history("assistant", ans)
            elif cmd == "/config":
                print("Config:")
                print("  OPENAI API:", bool(OPENAI_API_KEY and openai))
                print(f"  History file: {HISTORY_FILE}")
                print(f"  Memory file:  {MEMORY_FILE}")
            else:
                print("Comando desconhecido. Use /help")
            continue  # next loop

        # Normal chat message (not starting with /)
        user_text = raw.strip()
        # store
        append_history("user", user_text)

        # Prefer OpenAI if disponível
        reply = None
        if OPENAI_API_KEY and openai:
            reply = openai_chat(user_text)
            if reply is None:
                reply = "(Erro OpenAI; caindo para fallback)"
        if not reply:
            reply = fallback_reply(user_text)

        print(Fore.GREEN + "Assistente> " + reply)
        append_history("assistant", reply)


if __name__ == "__main__":
    try:
        command_loop()
    except KeyboardInterrupt:
        print("\nSaindo... bye")
