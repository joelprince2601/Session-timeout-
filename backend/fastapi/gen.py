import jwt

payload = "Hello, world!"
secret_key = "super_secret_key_123456789"

token = jwt.encode({"sub": payload}, secret_key, algorithm="HS256")

print("Generated Token:", token.encode())
