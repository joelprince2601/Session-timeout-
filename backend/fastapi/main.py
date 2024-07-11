from fastapi import FastAPI, HTTPException, Query, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

SECRET_KEY = "super_secret_key_123456789"  # Shared secret key

class PayloadModel(BaseModel):
    payload: str
    token: str

# Allow CORS for all origins (for testing purposes, this can be restricted)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <body>
            <h1>Welcome to the Payload Receiver</h1>
            <form id="payloadForm">
                <label for="payload">Payload:</label>
                <input type="text" id="payload" name="payload" required><br><br>
                <label for="token">Token:</label>
                <input type="text" id="token" name="token" required><br><br>
                <input type="submit" value="Send Payload">
            </form>
            <p>Or use this test link:</p>
            <a href="/receive-payload?payload=test&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.UAm6VFLE0BqiVeL1qR9srzABKYbdXOeRomcljkOeDMA">Test Receive Payload</a>
            
            <div id="responseMessage"></div>
            <button onclick="checkConnection()">Check Connection</button>

            <script>
            let token = "";
            let timerInterval;

            function checkConnection() {
                if (!token) {
                    token = document.getElementById('token').value;
                }

                fetch(`/check-expiration?token=${token}`)
                    .then(response => {
                        if (response.ok) {
                            return response.json();
                        } else {
                            throw new Error('Network response was not ok.');
                        }
                    })
                    .then(data => {
                        if (data.expired) {
                            document.getElementById('responseMessage').innerText = "Token has expired.";
                            setTimeout(() => {
                                window.location.href = "/";
                            }, 3000);  // Redirect to the form page after 3 seconds
                        } else {
                            document.getElementById('responseMessage').innerText = "Token is still valid.";
                            setTimeout(() => {
                                window.location.href = "/";
                            }, 3000);
                        }
                    })
                    .catch(error => {
                        console.error('Error checking token expiration:', error);
                    });
            }

            function startTimer(expirationTime) {
                const expirationDate = new Date(expirationTime);
                const endTime = new Date(Date.now() + 10000); // 10 seconds from now
                timerInterval = setInterval(() => {
                    const now = new Date();
                    if (now >= endTime) {
                        clearInterval(timerInterval);
                        document.getElementById('responseMessage').innerText = "Token has expired. Reloading the page...";
                        setTimeout(() => {
                            window.location.href = "/";
                        }, 3000);  // Redirect to the form page after 3 seconds
                    }
                }, 2000);  // Check every 2 seconds
            }

            document.getElementById('payloadForm').addEventListener('submit', function(event) {
                event.preventDefault();
                let payload = document.getElementById('payload').value;
                token = document.getElementById('token').value;

                fetch('/receive-payload', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `payload=${payload}&token=${token}`
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error('Network response was not ok.');
                    }
                })
                .then(data => {
                    document.getElementById('responseMessage').innerText = `Payload received: ${data.payload}`;
                    startTimer(data.expiration);  // Start the timer with the expiration time
                })
                .catch(error => {
                    console.error('Error sending payload:', error);
                });
            });
            </script>

        </body>
    </html>
    """

@app.post("/receive-payload")
def receive_payload_post(payload: str = Form(...), token: str = Form(...)):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        expiration_time = decoded_token['exp']
        expiration_datetime = datetime.utcfromtimestamp(expiration_time)
        return {
            "payload": payload,
            "expiration": expiration_datetime.isoformat()  # Return expiration time to the client
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

@app.get("/check-expiration")
async def check_expiration(token: str):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"expired": False}
    except jwt.ExpiredSignatureError:
        return {"expired": True}
    except jwt.InvalidTokenError:
        return {"expired": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
