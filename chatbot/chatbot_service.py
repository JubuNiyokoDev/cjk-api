import os
import json
import re
from difflib import get_close_matches
from django.conf import settings
import cohere
import httpx
from blog.models import BlogPost
from activities.models import Activity
from members.models import Member

def _require_ascii(value, name):
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = value.strip()
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(
            f"{name} must contain only ASCII characters. "
            f"Check your environment variable for hidden accents or spaces."
        ) from exc
    return value


# Configure Cohere avec httpx client UTF-8
httpx_client = httpx.Client(
    headers={"Content-Type": "application/json; charset=utf-8"},
    timeout=30.0
)
_cohere_api_key = _require_ascii(settings.COHERE_API_KEY, "COHERE_API_KEY")
client = cohere.Client(
    api_key=_cohere_api_key,
    client_name="cjk-api",
    httpx_client=httpx_client
)
COHERE_MODEL = getattr(settings, "COHERE_MODEL", "command-r-08-2024")

# Session memory
session_chats = {}

EMPATHY_LINES = {
    "fr": "Merci pour votre message.",
    "rn": "Murakoze kutwandikira.",
    "en": "Thank you for your message.",
    "sw": "Asante kwa ujumbe wako."
}

CONTACT_LINES = {
    "fr": "Si besoin, l'equipe CJK reste a votre disposition.",
    "rn": "Nimba hakenewe ibindi, twiteguye kugufasha kuri CJK.",
    "en": "If needed, the CJK team remains available to help.",
    "sw": "Ikihitajika, timu ya CJK iko tayari kukusaidia."
}

GREETING_RESPONSES = {
    "fr": "Bonjour.\nComment puis-je vous aider aujourd'hui ?",
    "rn": "Namahoro.\nNdagufasha iki uyu munsi?",
    "en": "Hello.\nHow can I help you today?",
    "sw": "Habari.\nNinaweza kukusaidia vipi leo?"
}


def load_json_dataset():
    json_path = os.path.join(settings.BASE_DIR, "cjk_dataset.json")
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_database_context():
    """Récupère les données publiques de la DB pour enrichir le contexte"""
    context = {
        "blog_posts": [],
        "activities": [],
        "members_count": Member.objects.filter(is_active_member=True).count()
    }

    posts = BlogPost.objects.filter(is_published=True)[:5]
    for post in posts:
        context["blog_posts"].append({
            "title": post.title,
            "author": post.author.get_full_name(),
            "category": post.category.name if post.category else "Sans categorie"
        })

    activities = Activity.objects.filter(is_published=True)[:5]
    for activity in activities:
        context["activities"].append({
            "title": activity.title,
            "type": activity.get_activity_type_display(),
            "date": activity.date_activite.strftime("%d/%m/%Y")
        })

    return context


def find_intent(text):
    """Identifie l'intention de l'utilisateur"""
    dataset = load_json_dataset()
    intents = dataset.get("intents", [])

    for intent_data in intents:
        if intent_data["intent_name"] == "support_general":
            for phrase in intent_data["training_phrases"]:
                if get_close_matches(text.lower(), [phrase.lower()], n=1, cutoff=0.8):
                    if any(word in text.lower() for word in ["bonjour", "salut", "hello", "mwaramutse"]):
                        return "support_general", "greeting"
                    elif any(word in text.lower() for word in ["merci", "murakoze", "thank"]):
                        return "support_general", "thanks"

    best_match_score = 0.6
    matched_intent = None
    matched_key = None

    for intent_data in intents:
        for phrase in intent_data["training_phrases"]:
            matches = get_close_matches(text.lower(), [phrase.lower()], n=1, cutoff=best_match_score)
            if matches:
                matched_intent = intent_data["intent_name"]
                if "responses" in intent_data:
                    matched_key = list(intent_data["responses"].keys())[0]
                return matched_intent, matched_key

    return "general_inquiry", None


def get_response_for_intent(intent_name, response_key, lang, dataset):
    """Récupère la réponse du dataset"""
    for intent_data in dataset["intents"]:
        if intent_data["intent_name"] == intent_name:
            responses = intent_data["responses"]
            if response_key and response_key in responses:
                return responses[response_key].get(lang, "")
            elif "default" in responses:
                return responses["default"].get(lang, "")
    return None


def find_language(text, chat_history):
    """Détecte la langue avec Cohere"""
    prompt = "What is the language of this sentence: '" + str(text) + "'? Respond with only one word: 'French', 'English', 'Kirundi', or 'Swahili'."

    try:
        response = client.chat(
            message=prompt,
            model=COHERE_MODEL,
            chat_history=[],  # Sans historique pour la détection
            temperature=0.1
        )

        answer = str(response.text).strip().lower()

        if "french" in answer or "francais" in answer:
            return "fr"
        elif "kirundi" in answer:
            return "rn"
        elif "english" in answer or "anglais" in answer:
            return "en"
        elif "swahili" in answer:
            return "sw"
        return "fr"
    except:
        return "fr"  # Pas de logging


def quick_language_guess(text):
    t = (text or "").lower()
    if any(w in t for w in ["bonjour", "salut", "merci", "svp", "s'il", "mais ", "pourquoi", "comment", "je "]):
        return "fr"
    if any(w in t for w in ["hello", "hi", "thanks", "please"]):
        return "en"
    if any(w in t for w in ["mwaramutse", "murakoze", "urakoze"]):
        return "rn"
    if any(w in t for w in ["habari", "asante", "tafadhali"]):
        return "sw"
    return None


def _normalize_line(text):
    return " ".join((text or "").strip().split())


def _is_greeting_only(text):
    t = (text or "").strip().lower()
    if not t:
        return False
    t_clean = re.sub(r"[^\w\s']+", " ", t)
    t_clean = re.sub(r"\s+", " ", t_clean).strip()

    greeting_phrases = {
        "bonjour",
        "salut",
        "bonsoir",
        "hello",
        "hi",
        "good morning",
        "good afternoon",
        "good evening",
        "mwaramutse",
        "namahoro",
        "habari",
        "hujambo",
        "shikamoo",
        "how are you",
        "are you good",
        "comment vas tu",
        "comment vas tu?",
        "comment allez vous",
        "comment allez vous?",
        "ca va",
        "ça va",
        "amakuru yawe",
        "umeamkaje"
    }
    if t_clean in greeting_phrases:
        return True

    greeting_tokens = {
        "bonjour",
        "salut",
        "bonsoir",
        "hello",
        "hi",
        "good",
        "morning",
        "afternoon",
        "evening",
        "mwaramutse",
        "namahoro",
        "habari",
        "hujambo",
        "shikamoo",
        "comment",
        "vas",
        "tu",
        "allez",
        "vous",
        "ca",
        "ça",
        "va",
        "how",
        "are",
        "you",
        "are",
        "good",
        "amakuru",
        "yawe",
        "umeamkaje"
    }
    tokens = t_clean.split()
    return bool(tokens) and all(tok in greeting_tokens for tok in tokens)


def _strip_greetings(text):
    t = (text or "").strip()
    if not t:
        return t
    # Remove common greetings and "how are you" style openers
    t = re.sub(
        r"^(bonjour|salut|hello|hi|good morning|good afternoon|good evening|mwaramutse|namahoro|habari)[.!?\\s-]*",
        "",
        t,
        flags=re.IGNORECASE,
    )
    t = re.sub(
        r"^(comment allez-vous|comment tu vas|comment vas-tu|ca va|ça va|how are you|amakuru yawe|umeamkaje)[.!?\\s-]*",
        "",
        t,
        flags=re.IGNORECASE,
    )
    return t.strip()


def _limit_sentences(text, max_sentences=2):
    if not text:
        return text
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(parts[:max_sentences]).strip()


def _clean_model_answer(text, lang):
    t = _strip_greetings(text)
    # remove any accidental empathy line duplication
    empathy = EMPATHY_LINES.get(lang, EMPATHY_LINES["fr"])
    t = t.replace(empathy, "").strip()
    t = _limit_sentences(t, max_sentences=2)
    return _normalize_line(t)


def _compose_reply(main_text, lang, add_contact=False):
    lines = []
    lines.append(EMPATHY_LINES.get(lang, EMPATHY_LINES["fr"]))
    lines.append(_normalize_line(main_text))
    if add_contact:
        lines.append(CONTACT_LINES.get(lang, CONTACT_LINES["fr"]))
    # Remove empty lines
    lines = [l for l in lines if l]
    return "\n".join(lines)


def start_new_chat(session_key):
    """Démarre une nouvelle session chat"""
    session_chats[session_key] = []
    return session_chats[session_key]


def get_chat(session_key):
    """Récupère ou crée un chat"""
    if session_key not in session_chats:
        start_new_chat(session_key)
    return session_chats[session_key]


def send_message(text, session_key):
    """Logique principale du chatbot"""
    chat_history = get_chat(session_key)
    dataset = load_json_dataset()

    try:
        user_text = (text or "").strip()
        user_language = quick_language_guess(user_text) or find_language(user_text, chat_history)
        if _is_greeting_only(user_text):
            bot_response = GREETING_RESPONSES.get(user_language, GREETING_RESPONSES["fr"])
            chat_history.append({"role": "USER", "message": user_text})
            chat_history.append({"role": "CHATBOT", "message": bot_response})
            return bot_response
        intent_name, response_key = find_intent(user_text)
        db_context = get_database_context()
        dataset_response = get_response_for_intent(intent_name, response_key, user_language, dataset)

        lang_full = {"fr": "francais", "rn": "kirundi", "en": "anglais", "sw": "swahili"}.get(
            user_language, "francais"
        )

        system_preamble = (
            "Tu es l'assistant officiel du Centre Jeunes Kamenge (CJK). "
            f"Reponds uniquement en {lang_full}. "
            "Ne salue pas. Ne pose pas de questions. "
            "Donne uniquement la reponse factuelle en 1 a 2 phrases. "
            "N'ajoute pas d'informations qui ne sont pas dans le contexte."
        )

        # Si on a une réponse du dataset, on la reformule en style pro
        # en restant strictement dans la langue.
        if dataset_response:
            prompt = (
                f"Question: {user_text}\n"
                f"Reponse de reference (a conserver sur le fond): {dataset_response}\n"
                "Reformule de maniere professionnelle et concise."
            )
            response = client.chat(
                message=prompt,
                model=COHERE_MODEL,
                preamble=system_preamble,
                chat_history=[],
                temperature=0.2,
                max_tokens=300
            )
            main_answer = _clean_model_answer(response.text, user_language)
            if not main_answer:
                main_answer = dataset_response.strip()
            bot_response = _compose_reply(
                main_answer,
                user_language,
                add_contact=False
            )
            chat_history.append({"role": "USER", "message": user_text})
            chat_history.append({"role": "CHATBOT", "message": bot_response})
            return bot_response

        # Contexte condensé
        posts = "; ".join(
            f"{p['title']} ({p['author']}, {p['category']})" for p in db_context.get("blog_posts", [])
        )
        activities = "; ".join(
            f"{a['title']} ({a['type']}, {a['date']})" for a in db_context.get("activities", [])
        )
        context_lines = [
            f"Membres actifs: {db_context.get('members_count', 0)}.",
        ]
        if posts:
            context_lines.append(f"Articles recents: {posts}.")
        if activities:
            context_lines.append(f"Activites recentes: {activities}.")
        context_block = " ".join(context_lines)

        prompt = f"Contexte: {context_block}\nQuestion: {user_text}\nReponse:"

        response = client.chat(
            message=prompt,
            model=COHERE_MODEL,
            preamble=system_preamble,
            chat_history=chat_history[-6:],
            temperature=0.3,
            max_tokens=400
        )

        main_answer = _clean_model_answer(response.text, user_language)
        bot_response = _compose_reply(
            main_answer,
            user_language,
            add_contact=True
        )
        chat_history.append({"role": "USER", "message": user_text})
        chat_history.append({"role": "CHATBOT", "message": bot_response})

        return bot_response

    except Exception as e:
        import traceback
        print("=" * 50)
        print("ERREUR:", str(e))
        traceback.print_exc()
        print("=" * 50)
        return f"Desole, une erreur s'est produite. Veuillez reessayer."


def user_language_to_full_name(lang_code):
    return {"fr": "francais", "rn": "kirundi", "en": "anglais", "sw": "swahili"}.get(lang_code, "francais")
