from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import PlainTextResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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
async def verify_webhook(mode: str, verify_token: str, challenge: str):
    # Verify the webhook
    if mode and verify_token:
        if mode == "subscribe" and verify_token == VERIFY_TOKEN:
            # Respond with the challenge token from the request
            return PlainTextResponse(content=challenge)
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            return PlainTextResponse(content="Verification failed", status_code=403)
    else:
        # Responds with '400 Bad Request' if required parameters are missing
        return PlainTextResponse(content="Missing mode or verify_token", status_code=400)
