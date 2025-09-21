import os
import uvicorn
import json
import re
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from argon2 import PasswordHasher
from jose import JWTError, jwt
from pydantic import BaseModel, constr

# ===============================
# 🔹 Configurações ultra seguras
# ===============================
SECRET_KEY = os.getenv("SECRET_KEY", "MUDAR_PARA_CHAVE_SECRETA_REAL")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
RATE_LIMIT = 5
RATE_WINDOW_MINUTES = 5

ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

COMMON_PASSWORDS = {"123456", "senha", "qwerty", "password"}

# ===============================
# 🔹 Banco de dados simulado
# ===============================
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "SenhaUltraSegura123!")
users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrador",
        "hashed_password": ph.hash(ADMIN_PASSWORD),
        "disabled": False,
        "refresh_tokens": {}  # jti: exp
    }
}

login_attempts = {}  # ip: [timestamps]

# ===============================
# 🔹 Models Pydantic
# ===============================
class LoginForm(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_-]+$")
    password: constr(min_length=8)

# ===============================
# 🔹 Logging estruturado
# ===============================
def log_event(event: str, ip: str = None, user: str = None):
    entry = {
        "time": datetime.utcnow().isoformat(),
        "event": event,
        "ip": ip,
        "user": user
    }
    with open("security.json", "a") as f:
        f.write(json.dumps(entry) + "\n")

# ===============================
# 🔹 Funções auxiliares
# ===============================
def sanitize_input(text: str):
    return re.sub(r"[<>'\";]", "", text)

def verify_password(plain_password, hashed_password):
    try:
        return ph.verify(hashed_password, plain_password)
    except:
        return False

def check_common_password(password):
    if password.lower() in COMMON_PASSWORDS:
        raise HTTPException(status_code=400, detail="Senha comum não permitida")

def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user: dict):
    jti = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    user["refresh_tokens"][jti] = expire.isoformat()
    payload = {"sub": user["username"], "jti": jti, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Não autorizado")
        user = users_db.get(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Não autorizado")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Não autorizado")

# ===============================
# 🔹 Rate Limiting
# ===============================
def check_rate_limit(ip: str):
    now = datetime.utcnow()
    attempts = login_attempts.get(ip, [])
    # Remove timestamps antigos
    attempts = [t for t in attempts if now - t < timedelta(minutes=RATE_WINDOW_MINUTES)]
    login_attempts[ip] = attempts
    if len(attempts) >= RATE_LIMIT:
        return False
    attempts.append(now)
    login_attempts[ip] = attempts
    return True

# ===============================
# 🔹 App FastAPI
# ===============================
app = FastAPI()

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if not request.headers.get("user-agent"):
        log_event("Bloqueio - User-Agent ausente", ip=request.client.host)
        raise HTTPException(status_code=400, detail="User-Agent obrigatório")
    return await call_next(request)

@app.post("/token")
async def login(form: LoginForm, request: Request):
    username = sanitize_input(form.username)
    password = sanitize_input(form.password)
    ip = request.client.host

    check_common_password(password)

    if not check_rate_limit(ip):
        log_event("Bloqueio - Rate limit atingido", ip=ip, user=username)
        raise HTTPException(status_code=429, detail="Muitas tentativas, tente depois")

    user = authenticate_user(username, password)
    if not user:
        log_event("Falha de login", ip=ip, user=username)
        raise HTTPException(status_code=400, detail="Usuário ou senha inválidos")

    access_token = create_access_token({"sub": username})
    refresh_token = create_refresh_token(user)
    log_event("Login bem sucedido", ip=ip, user=username)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/revoke-refresh")
async def revoke_refresh(jti: str, current_user: dict = Depends(get_current_user)):
    if jti in current_user["refresh_tokens"]:
        del current_user["refresh_tokens"][jti]
        log_event("Refresh token revogado", user=current_user["username"])
        return {"status": "revogado"}
    raise HTTPException(status_code=404, detail="Token não encontrado")

@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "full_name": current_user["full_name"]}

@app.get("/admin/logs")
async def get_logs(current_user: dict = Depends(get_current_user)):
    if current_user["username"] != "admin":
        raise HTTPException(status_code=403, detail="Não autorizado")
    try:
        with open("security.json", "r") as f:
            logs = [json.loads(line) for line in f.readlines()]
        return logs
    except FileNotFoundError:
        return []

@app.post("/validate-ip")
async def validate_ip(ip: str):
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return {"ip": ip, "valid": True}
    except ValueError:
        return {"ip": ip, "valid": False}

# ===============================
# 🔹 Inicialização
# ===============================
if __name__ == "__main__":
    uvicorn.run("secure_base_ultimate:app", host="127.0.0.1", port=8000, reload=True)
