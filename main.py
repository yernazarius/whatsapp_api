from fastapi import FastAPI, Request, HTTPException, status, Response
from pydantic import BaseModel
import uvicorn
import os
import httpx

app = FastAPI()

# Load environment variables
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')


class WhatsAppMessage(BaseModel):
    object: str
    entry: list


@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()

    # Check the Incoming webhook message
    print(body)

    if body.get('object'):
        entry = body.get('entry', [])
        if entry and 'changes' in entry[0]:
            changes = entry[0]['changes']
            if changes and 'value' in changes[0] and 'messages' in changes[0]['value']:
                phone_number_id = changes[0]['value']['metadata']['phone_number_id']
                from_number = changes[0]['value']['messages'][0]['from']
                msg_body = changes[0]['value']['messages'][0]['text']['body']

                # Send response message
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={WHATSAPP_TOKEN}",
                        json={
                            "messaging_product": "whatsapp",
                            "to": from_number,
                            "text": {"body": "Ack: " + msg_body},
                        },
                        headers={"Content-Type": "application/json"},
                    )

        return {"message": "Received"}, 200
    else:
        raise HTTPException(status_code=404, detail="Event is not from a WhatsApp API")

@app.get("/webhook")
async def verify_webhook(response: Response, hub_mode: str = None, hub_verify_token: str = None, hub_challenge: str = None):
    if hub_mode and hub_verify_token:
        if hub_mode == 'subscribe' and hub_verify_token == VERIFY_TOKEN:
            response.media_type = "text/plain"
            return hub_challenge
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    else:
        raise HTTPException(status_code=400, detail="Missing mode or token")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 8000)))