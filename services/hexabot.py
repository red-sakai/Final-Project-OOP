from flask import Blueprint, request, jsonify
import re
from transformers import pipeline
import requests

hexabot_bp = Blueprint("hexabot", __name__)

# Initialize DistilBERT QA pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

CONVERSATION_PATTERNS = {
    "greetings": [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening", "yo", "sup"
    ],
    "thanks": [
        "thank you", "thanks", "thx", "ty"
    ],
    "goodbye": [
        "bye", "goodbye", "see you", "see ya", "farewell"
    ]
}

CONVERSATION_RESPONSES = {
    "greetings": "Hello, I am HexaBot, your logistics assistant. What can I do for you today?",
    "thanks": "You're welcome! If you have more questions about HexaHaul, just ask.",
    "goodbye": "Goodbye! If you need anything else about HexaHaul, feel free to chat again."
}

CONVERSATION_RESPONSES_TL = {
    "greetings": "Kumusta, ako si HexaBot, ang iyong logistics assistant. Ano ang maaari kong gawin para sa iyo ngayon?",
    "thanks": "Walang anuman! Kung may iba ka pang tanong tungkol sa HexaHaul, itanong mo lang.",
    "goodbye": "Paalam! Kung kailangan mo pa ng tulong tungkol sa HexaHaul, huwag mag-atubiling makipag-chat muli."
}

QUICK_REPLY_ANSWERS = {
    "about hexahaul": "HexaHaul is a logistics company founded and operated by a passionate team of six people: Jhered, Carl, Patricia, Kris, Sandrine, and CJ. We provide efficient and reliable transportation solutions for businesses and individuals.",
    "who are you?": "I'm HexaBot, your helpful AI assistant for HexaHaul. Ask me anything about our company or services!",
    "what services do you offer?": "HexaHaul offers truck, motorcycle, and car logistics for deliveries of all sizes. We ensure timely deliveries, real-time tracking, and excellent customer service.",
    "how can i track my shipment?": "You can track your shipment using the tracking page on our website by entering your tracking number. If you have lost your tracking number, please contact our support team.",
    "how do i contact support?": "For support, contact us at hexahaulprojects@gmail.com or call 123-456-7890. Our office hours are 9am to 6pm, Monday to Saturday."
}

QUICK_REPLY_ANSWERS_TL = {
    "about hexahaul": "Ang HexaHaul ay isang logistics company na itinatag at pinapatakbo ng anim na masigasig na tao: Jhered, Carl, Patricia, Kris, Sandrine, at CJ. Nagbibigay kami ng mahusay at maaasahang solusyon sa transportasyon para sa mga negosyo at indibidwal.",
    "who are you?": "Ako si HexaBot, ang iyong AI assistant para sa HexaHaul. Magtanong ka lang tungkol sa aming kumpanya o serbisyo!",
    "what services do you offer?": "Nag-aalok ang HexaHaul ng truck, motorsiklo, at car logistics para sa lahat ng laki ng deliveries. Tinitiyak namin ang maagap na paghahatid, real-time tracking, at mahusay na customer service.",
    "how can i track my shipment?": "Maaari mong subaybayan ang iyong shipment gamit ang tracking page sa aming website sa pamamagitan ng paglalagay ng iyong tracking number. Kung nawala mo ang iyong tracking number, mangyaring makipag-ugnayan sa aming support team.",
    "how do i contact support?": "Para sa suporta, kontakin kami sa hexahaulprojects@gmail.com o tumawag sa 123-456-7890. Ang aming opisina ay bukas mula 9am hanggang 6pm, Lunes hanggang Sabado."
}

FAQ_CONTEXT = """
HexaHaul is a logistics company founded and operated by a passionate team of six people: Jhered, Carl, Patricia, Kris, Sandrine, and CJ. We provide efficient and reliable transportation solutions for businesses and individuals.
Our services include truck, motorcycle, and car logistics for deliveries of all sizes. You can track your shipment using the tracking page on our website by entering your tracking number.
For support, contact us at hexahaulprojects@gmail.com or call 123-456-7890. Our office hours are 9am to 6pm, Monday to Saturday.
We ensure timely deliveries, real-time tracking, and excellent customer service. We operate in major cities and offer both same-day and scheduled delivery options.
If you have lost your tracking number, please contact our support team. For partnership or business inquiries, email us at hexahaulprojects@gmail.com.
HexaHaul is committed to safe, secure, and on-time delivery of your goods.
"""

PROFANITY_LIST = [
    "fuck", "shit", "bitch", "asshole", "bastard", "dick", "pussy", "motherfucker", "fucker", "cunt", "slut", "penis", "dimwit",
    "putangina", "tangina", "tanginamo", "taena", "taenamo", "gago", "ulol", "leche", "bwisit", "punyeta", "potangina", "pota",
    "pakshet", "puta", "pukinginamo", "kinginamo",
]

def contains_profanity(text):
    text = text.lower()
    for word in PROFANITY_LIST:
        if re.search(rf"\b{re.escape(word)}\b", text):
            return True
    return False

# Helper: Detect if input is Tagalog (very basic, can be improved)
def detect_language(text):
    tagalog_keywords = [
        "kamusta", "kumusta", "ano", "paano", "saan", "kailan", "bakit", "ikaw", "ako", "siya", "tayo", "kayo", "nila", "natin", "ng", "sa", "ang", "mga", "at", "hindi", "oo", "opo", "po"
    ]
    text = text.lower()
    for word in tagalog_keywords:
        if word in text:
            return "tl"
    # Default to English if not detected
    return "en"

# Helper: Translate text using LibreTranslate API
def libretranslate(text, source, target):
    if source == target:
        return text
    try:
        resp = requests.post(
            "https://libretranslate.de/translate",
            data={
                "q": text,
                "source": source,
                "target": target,
                "format": "text"
            },
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json()["translatedText"]
    except Exception:
        pass
    return text  # fallback

@hexabot_bp.route("/hexabot", methods=["POST"])
def faq_bot():
    user_question = request.form.get("question", "").strip()
    lang = request.form.get("lang", "en").lower()
    if not user_question:
        return jsonify({"answer": "Please provide a question."}), 400

    if contains_profanity(user_question):
        answer = "Let's keep our conversation respectful. Please avoid using inappropriate language."
        if lang == "tl":
            answer = "Panatilihin nating magalang ang ating usapan. Iwasan po natin ang paggamit ng hindi angkop na wika."
        return jsonify({"answer": answer})

    normalized = user_question.lower().strip(" ?!.")

    # Detect language if not explicitly set
    detected_lang = detect_language(normalized)
    if lang not in ["en", "tl"]:
        lang = detected_lang

    # Easter egg
    if "who is our professor" in normalized or "sino professor" in normalized or "sino ang professor" in normalized:
        answer = "Engr. Jerico Sarcillo, our outstanding professor! He inspires us to excel and brings out the best in every student. We are grateful for his dedication and guidance."
        if lang == "tl":
            answer = "Si Engr. Jerico Sarcillo, ang aming kahanga-hangang propesor! Inspirasyon siya sa amin upang magtagumpay at ilabas ang pinakamahusay sa bawat estudyante. Lubos kaming nagpapasalamat sa kanyang dedikasyon at paggabay."
        return jsonify({"answer": answer})

    # Support both English and Tagalog greetings
    greetings_keywords = CONVERSATION_PATTERNS["greetings"] + ["kamusta", "kumusta"]
    for pattern, keywords in CONVERSATION_PATTERNS.items():
        if any(normalized.startswith(word) or normalized == word for word in keywords):
            if pattern == "greetings" and (normalized in ["kamusta", "kumusta"] or normalized in keywords):
                answer = CONVERSATION_RESPONSES_TL["greetings"] if lang == "tl" else CONVERSATION_RESPONSES["greetings"]
            else:
                answer = CONVERSATION_RESPONSES_TL.get(pattern, CONVERSATION_RESPONSES[pattern]) if lang == "tl" else CONVERSATION_RESPONSES[pattern]
            return jsonify({"answer": answer})

    # Also check for Tagalog greetings
    if normalized in ["kamusta", "kumusta"]:
        answer = CONVERSATION_RESPONSES_TL["greetings"] if lang == "tl" else CONVERSATION_RESPONSES["greetings"]
        return jsonify({"answer": answer})

    # Quick replies (support both EN and TL triggers)
    for quick, answer in QUICK_REPLY_ANSWERS.items():
        if normalized == quick or normalized.rstrip("?!.") == quick.rstrip("?!."):
            if lang == "tl":
                answer = QUICK_REPLY_ANSWERS_TL.get(quick, answer)
            return jsonify({"answer": answer})

    # If not about HexaHaul, fallback
    allowed_keywords = [
        "hexahaul", "service", "services", "track", "tracking", "shipment", "support", "contact", "delivery", "truck", "motorcycle", "car", "logistics", "booking", "book", "parcel",
        "serbisyo", "padala", "subaybayan", "suporta", "kontak", "trak", "motorsiklo", "kotse", "logistik"
    ]
    if not any(word in normalized for word in allowed_keywords):
        answer = "I'm sorry, I don't have an answer for that. Please ask about HexaHaul's services, tracking, or support."
        if lang == "tl":
            answer = "Paumanhin, wala akong sagot diyan. Mangyaring magtanong tungkol sa mga serbisyo, tracking, o suporta ng HexaHaul."
        return jsonify({"answer": answer})

    # Use QA pipeline, then translate if needed
    result = qa_pipeline(question=user_question, context=FAQ_CONTEXT)
    answer = result["answer"].strip()

    if not answer or len(answer) < 5:
        answer = "I'm sorry, I don't have an answer for that. Please ask about HexaHaul's services, tracking, or support."
        if lang == "tl":
            answer = "Paumanhin, wala akong sagot diyan. Mangyaring magtanong tungkol sa mga serbisyo, tracking, o suporta ng HexaHaul."
    elif lang == "tl":
        answer = libretranslate(answer, "en", "tl")

    return jsonify({"answer": answer})