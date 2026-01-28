# Auth API

FastAPI ile JWT kimlik dogrulama API'si.

## Kurulum

```bash
pip install -r requirements.txt
cd app
uvicorn main:app --reload --port 8000
```

Docker ile:
```bash
docker-compose up --build
```

## API Dokumantasyonu

- Swagger UI: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json

## Endpoint Ornekleri

### Health Check
```bash
curl http://localhost:8000/health
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@gmail.com", "password": "abcd"}'
```

### Token Yenileme
```bash
curl -X POST "http://localhost:8000/auth/refresh?refresh_token=TOKEN"
```

### Kullanici Bilgisi
```bash
curl "http://localhost:8000/auth/me?access_token=TOKEN"
```

### Logout
```bash
curl -X POST "http://localhost:8000/auth/logout?email=admin@gmail.com"
```

## Testler

```bash
cd app
pytest test_api.py -v
```

## Varsayilan Kullanicilar

| Email | Sifre |
|-------|-------|
| admin@gmail.com | abcd |
| kaan@gmail.com | abcd |
