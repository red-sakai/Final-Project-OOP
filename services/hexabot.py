from flask import Blueprint, request, jsonify
import re
from transformers import pipeline
import requests
from abc import ABC, abstractmethod

hexabot_bp = Blueprint("hexabot", __name__)

# Initialize DistilBERT QA pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Abstraction: Base abstract class for chatbot features
class ChatBotFeature(ABC):
    @abstractmethod
    def process(self, text, lang="en"):
        pass

# Encapsulation: ProfanityFilter class encapsulates profanity detection logic
class ProfanityFilter(ChatBotFeature):
    def __init__(self):
        self.__profanity_list = [
            "fuck", "shit", "bitch", "asshole", "bastard", "dick", "pussy", "motherfucker", "fucker", "cunt", "slut", "penis", "dimwit",
            "putangina", "tangina", "tanginamo", "taena", "taenamo", "gago", "ulol", "leche", "bwisit", "punyeta", "potangina", "pota",
            "pakshet", "puta", "pukinginamo", "kinginamo",
        ]
    
    def process(self, text, lang="en"):
        has_profanity = self.__contains_profanity(text)
        if has_profanity:
            if lang == "tl":
                return "Panatilihin nating magalang ang ating usapan. Iwasan po natin ang paggamit ng hindi angkop na wika."
            return "Let's keep our conversation respectful. Please avoid using inappropriate language."
        return None
    
    def __contains_profanity(self, text):
        text = text.lower()
        for word in self.__profanity_list:
            if re.search(rf"\b{re.escape(word)}\b", text):
                return True
        return False

# Encapsulation: LanguageDetector class encapsulates language detection
class LanguageDetector(ChatBotFeature):
    def __init__(self):
        self.__tagalog_keywords = [
            "kamusta", "kumusta", "ano", "paano", "saan", "kailan", "bakit", "ikaw", "ako", "siya", "tayo", 
            "kayo", "nila", "natin", "ng", "sa", "ang", "mga", "at", "hindi", "oo", "opo", "po", "hoy"
        ]
    
    def process(self, text, lang="en"):
        return self.detect_language(text)
        
    def detect_language(self, text):
        text = text.lower()
        for word in self.__tagalog_keywords:
            if word in text:
                return "tl"
        return "en"

# Encapsulation: Translator class encapsulates translation functionality
class Translator(ChatBotFeature):
    def process(self, text, source="en", target="tl"):
        return self.translate(text, source, target)
        
    def translate(self, text, source, target):
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

# Base ChatBot class (parent)
class ChatBot:
    def __init__(self):
        self._lang_detector = LanguageDetector()
        self._profanity_filter = ProfanityFilter()
        self._translator = Translator()
        
    def _detect_language(self, text):
        return self._lang_detector.detect_language(text)
        
    def _check_profanity(self, text, lang="en"):
        return self._profanity_filter.process(text, lang)
        
    def _translate(self, text, source="en", target="tl"):
        return self._translator.translate(text, source, target)
    
    # Base method to be overridden by child classes
    def process_message(self, message, lang="en"):
        # Basic processing
        return "I am a chatbot."

# Inheritance: HexaBot inherits from ChatBot and extends its functionality
class HexaBot(ChatBot):
    def __init__(self):
        super().__init__()
        self.__conversation_patterns = {
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
        
        self.__conversation_responses = {
            "greetings": "Hello, I am HexaBot, your logistics assistant. What can I do for you today?",
            "thanks": "You're welcome! If you have more questions about HexaHaul, just ask.",
            "goodbye": "Goodbye! If you need anything else about HexaHaul, feel free to chat again."
        }
        
        self.__conversation_responses_tl = {
            "greetings": "Kumusta, ako si HexaBot, ang iyong logistics assistant. Ano ang maaari kong gawin para sa iyo ngayon?",
            "thanks": "Walang anuman! Kung may iba ka pang tanong tungkol sa HexaHaul, itanong mo lang.",
            "goodbye": "Paalam! Kung kailangan mo pa ng tulong tungkol sa HexaHaul, huwag mag-atubiling makipag-chat muli."
        }
        
        self.__quick_reply_answers = {
            "about hexahaul": "HexaHaul is a logistics company founded and operated by a passionate team of six people: Jhered, Carl, Patricia, Kris, Sandrine, and CJ. We provide efficient and reliable transportation solutions for businesses and individuals.",
            "who are you?": "I'm HexaBot, your helpful AI assistant for HexaHaul. Ask me anything about our company or services!",
            "what services do you offer?": "HexaHaul offers truck, motorcycle, and car logistics for deliveries of all sizes. We ensure timely deliveries, real-time tracking, and excellent customer service.",
            "how can i track my shipment?": "You can track your shipment using the tracking page on our website by entering your tracking number. If you have lost your tracking number, please contact our support team.",
            "how do i contact support?": "For support, contact us at hexahaulprojects@gmail.com or call 123-456-7890. Our office hours are 9am to 6pm, Monday to Saturday."
        }
        
        self.__quick_reply_answers_tl = {
            "about hexahaul": "Ang HexaHaul ay isang logistics company na itinatag at pinapatakbo ng anim na masigasig na tao: Jhered, Carl, Patricia, Kris, Sandrine, at CJ. Nagbibigay kami ng mahusay at maaasahang solusyon sa transportasyon para sa mga negosyo at indibidwal.",
            "who are you?": "Ako si HexaBot, ang iyong AI assistant para sa HexaHaul. Magtanong ka lang tungkol sa aming kumpanya o serbisyo!",
            "what services do you offer?": "Nag-aalok ang HexaHaul ng truck, motorsiklo, at car logistics para sa lahat ng laki ng deliveries. Tinitiyak namin ang maagap na paghahatid, real-time tracking, at mahusay na customer service.",
            "how can i track my shipment?": "Maaari mong subaybayan ang iyong shipment gamit ang tracking page sa aming website sa pamamagitan ng paglalagay ng iyong tracking number. Kung nawala mo ang iyong tracking number, mangyaring makipag-ugnayan sa aming support team.",
            "how do i contact support?": "Para sa suporta, kontakin kami sa hexahaulprojects@gmail.com o tumawag sa 123-456-7890. Ang aming opisina ay bukas mula 9am hanggang 6pm, Lunes hanggang Sabado."
        }
        
        self.__faq_context = """
HexaHaul is a logistics company founded and operated by a passionate team of six people: Jhered, Carl, Patricia, Kris, Sandrine, and CJ. We provide efficient and reliable transportation solutions for businesses and individuals.
Our services include truck, motorcycle, and car logistics for deliveries of all sizes. You can track your shipment using the tracking page on our website by entering your tracking number.
For support, contact us at hexahaulprojects@gmail.com or call 123-456-7890. Our office hours are 9am to 6pm, Monday to Saturday.
We ensure timely deliveries, real-time tracking, and excellent customer service. We operate in major cities and offer both same-day and scheduled delivery options.
If you have lost your tracking number, please contact our support team. For partnership or business inquiries, email us at hexahaulprojects@gmail.com.
HexaHaul is committed to safe, secure, and on-time delivery of your goods.
"""
        self.__allowed_keywords = [
            "hexahaul", "service", "services", "track", "tracking", "shipment", "support", "contact", "delivery", "truck", "motorcycle", "car", "logistics", "booking", "book", "parcel",
            "serbisyo", "padala", "subaybayan", "suporta", "kontak", "trak", "motorsiklo", "kotse", "logistik"
        ]

    # Polymorphism: Override the process_message method
    def process_message(self, message, lang="en"):
        if not message:
            return "Please provide a question."
            
        # Check for profanity
        profanity_response = self._check_profanity(message, lang)
        if profanity_response:
            return profanity_response
            
        # Process the message
        normalized = message.lower().strip(" ?!.")
        
        # Auto-detect language if not specified
        if lang not in ["en", "tl"]:
            lang = self._detect_language(normalized)
            
        # Easter egg
        easter_egg_response = self.__check_easter_egg(normalized, lang)
        if easter_egg_response:
            return easter_egg_response
            
        # Check for conversation patterns
        pattern_response = self.__check_conversation_patterns(normalized, lang)
        if pattern_response:
            return pattern_response
            
        # Check for quick replies
        quick_reply = self.__check_quick_replies(normalized, lang)
        if quick_reply:
            return quick_reply
            
        # Check if the question is about HexaHaul
        if not self.__is_about_hexahaul(normalized):
            if lang == "tl":
                return "Paumanhin, wala akong sagot diyan. Mangyaring magtanong tungkol sa mga serbisyo, tracking, o suporta ng HexaHaul."
            return "I'm sorry, I don't have an answer for that. Please ask about HexaHaul's services, tracking, or support."
            
        # Use QA pipeline for complex questions
        return self.__get_qa_answer(message, lang)
    
    def __check_easter_egg(self, normalized, lang):
        if "who is our professor" in normalized or "sino professor" in normalized or "sino ang professor" in normalized:
            answer = "Engr. Jerico Sarcillo, our outstanding professor! He inspires us to excel and brings out the best in every student. We are grateful for his dedication and guidance."
            if lang == "tl":
                answer = "Si Engr. Jerico Sarcillo, ang aming kahanga-hangang propesor! Inspirasyon siya sa amin upang magtagumpay at ilabas ang pinakamahusay sa bawat estudyante. Lubos kaming nagpapasalamat sa kanyang dedikasyon at paggabay."
            return answer
        return None
        
    def __check_conversation_patterns(self, normalized, lang):
        # Support both English and Tagalog greetings
        greetings_keywords = self.__conversation_patterns["greetings"] + ["kamusta", "kumusta"]
        for pattern, keywords in self.__conversation_patterns.items():
            if any(normalized.startswith(word) or normalized == word for word in keywords):
                if pattern == "greetings" and (normalized in ["kamusta", "kumusta"] or normalized in keywords):
                    answer = self.__conversation_responses_tl["greetings"] if lang == "tl" else self.__conversation_responses["greetings"]
                else:
                    answer = self.__conversation_responses_tl.get(pattern, self.__conversation_responses[pattern]) if lang == "tl" else self.__conversation_responses[pattern]
                return answer
                
        # Also check for Tagalog greetings
        if normalized in ["kamusta", "kumusta"]:
            answer = self.__conversation_responses_tl["greetings"] if lang == "tl" else self.__conversation_responses["greetings"]
            return answer
            
        return None
        
    def __check_quick_replies(self, normalized, lang):
        for quick, answer in self.__quick_reply_answers.items():
            if normalized == quick or normalized.rstrip("?!.") == quick.rstrip("?!."):
                if lang == "tl":
                    answer = self.__quick_reply_answers_tl.get(quick, answer)
                return answer
        return None
        
    def __is_about_hexahaul(self, normalized):
        return any(word in normalized for word in self.__allowed_keywords)
        
    def __get_qa_answer(self, question, lang):
        result = qa_pipeline(question=question, context=self.__faq_context)
        answer = result["answer"].strip()
        
        if not answer or len(answer) < 5:
            answer = "I'm sorry, I don't have an answer for that. Please ask about HexaHaul's services, tracking, or support."
            if lang == "tl":
                answer = "Paumanhin, wala akong sagot diyan. Mangyaring magtanong tungkol sa mga serbisyo, tracking, o suporta ng HexaHaul."
        elif lang == "tl":
            answer = self._translate(answer, "en", "tl")
            
        return answer

# Create a singleton instance of HexaBot
hexabot_instance = HexaBot()

@hexabot_bp.route("/hexabot", methods=["POST"])
def faq_bot():
    user_question = request.form.get("question", "").strip()
    lang = request.form.get("lang", "en").lower()
    
    if not user_question:
        return jsonify({"answer": "Please provide a question."}), 400
        
    # Process the message using our OOP approach
    answer = hexabot_instance.process_message(user_question, lang)
    
    return jsonify({"answer": answer})