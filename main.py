from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
import os
import httpx

app = FastAPI()

# Your WhatsApp token and verify token from environment variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

class WhatsAppMessage(BaseModel):
    object: str
    entry: list

@app.post("/webhook")
async def receive_message(request: Request):
    # Parse the request body
    body = await request.json()

    print(body)  # Log the request body to console

    # Process the WhatsApp message
    if body.get("object"):
        entry = body.get("entry", [])
        if entry:
            changes = entry[0].get("changes", [])
            if changes:
                message_data = changes[0].get("value")
                messages = message_data.get("messages", [])
                if messages:
                    phone_number_id = message_data.get("metadata", {}).get("phone_number_id")
                    from_number = messages[0].get("from")
                    msg_body = messages[0].get("text", {}).get("body")
                    
                    # Echo the received message back to the sender
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={WHATSAPP_TOKEN}",
                            json={
                                "messaging_product": "whatsapp",
                                "to": from_number,
                                "text": {"body": f"Ack: {msg_body}"}
                            },
                            headers={"Content-Type": "application/json"}
                        )
        return {"message": "Received"}, status.HTTP_200_OK
    else:
        raise HTTPException(status_code=404, detail="Event is not from WhatsApp API")

@app.get("/webhook")
async def verify_webhook(request: Request):
    # Verify the webhook
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return JSONResponse(content=int(challenge))  # Return challenge as a plain text response
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    else:
        raise HTTPException(status_code=400, detail="Missing mode or token")
