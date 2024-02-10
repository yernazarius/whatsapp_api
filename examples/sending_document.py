from os import getenv
from yernazarius import WhatsApp

from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()

    messenger = WhatsApp(token=getenv("TOKEN"), phone_number_id=getenv("PHONE_NUMBER_ID"))

    response = messenger.send_document(
        document="http://www.africau.edu/images/default/sample.pdf",
        recipient_id="255757294146",
    )

    print(response)
