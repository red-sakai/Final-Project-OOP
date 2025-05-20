from flask import Blueprint, request, jsonify
import re
from transformers import pipeline

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

QUICK_REPLY_ANSWERS = {
    "about hexahaul": "HexaHaul is a logistics company founded and operated by a passionate team of six people: Jhered, Carl, Patricia, Kris, Sandrine, and CJ. We provide efficient and reliable transportation solutions for businesses and individuals.",
    "who are you?": "I'm HexaBot, your helpful AI assistant for HexaHaul. Ask me anything about our company or services!",
    "what services do you offer?": "HexaHaul offers truck, motorcycle, and car logistics for deliveries of all sizes. We ensure timely deliveries, real-time tracking, and excellent customer service.",
    "how can i track my shipment?": "You can track your shipment using the tracking page on our website by entering your tracking number. If you have lost your tracking number, please contact our support team.",
    "how do i contact support?": "For support, contact us at hexahaulprojects@gmail.com or call 123-456-7890. Our office hours are 9am to 6pm, Monday to Saturday."
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

@hexabot_bp.route("/hexabot", methods=["POST"])
def faq_bot():
    user_question = request.form.get("question", "").strip()
    if not user_question:
        return jsonify({"answer": "Please provide a question."}), 400

    if contains_profanity(user_question):
        return jsonify({"answer": "Let's keep our conversation respectful. Please avoid using inappropriate language."})

    normalized = user_question.lower().strip(" ?!.")

    # Easter egg
    if "who is our professor" in normalized or "sino professor" in normalized or "sino ang professor" in normalized:
        return jsonify({
            "answer": "Engr. Jerico Sarcillo, our outstanding professor! He inspires us to excel and brings out the best in every student. We are grateful for his dedication and guidance."
        })

    for pattern, keywords in CONVERSATION_PATTERNS.items():
        if any(normalized.startswith(word) or normalized == word for word in keywords):
            return jsonify({"answer": CONVERSATION_RESPONSES[pattern]})

    for quick, answer in QUICK_REPLY_ANSWERS.items():
        if normalized == quick or normalized.rstrip("?!.") == quick.rstrip("?!."):
            return jsonify({"answer": answer})

    allowed_keywords = [
        "hexahaul", "service", "services", "track", "tracking", "shipment", "support", "contact", "delivery", "truck", "motorcycle", "car", "logistics", "booking", "book", "parcel"
    ]
    if not any(word in normalized for word in allowed_keywords):
        return jsonify({"answer": "I'm sorry, I don't have an answer for that. Please ask about HexaHaul's services, tracking, or support."})

    result = qa_pipeline(question=user_question, context=FAQ_CONTEXT)
    answer = result["answer"].strip()

    if not answer or len(answer) < 5:
        answer = "I'm sorry, I don't have an answer for that. Please ask about HexaHaul's services, tracking, or support."
    return jsonify({"answer": answer})