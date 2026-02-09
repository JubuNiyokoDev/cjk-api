import os
import json
from difflib import get_close_matches
from django.conf import settings
import google.generativeai as client
from blog.models import BlogPost
from activities.models import Activity
from members.models import Member

# Configure Gemini
client.configure(api_key=settings.GOOGLE_API_KEY)
model = client.GenerativeModel("gemini-2.0-flash-exp")

# Session memory
session_chats = {}


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
    
    # Derniers articles de blog publiés
    posts = BlogPost.objects.filter(is_published=True)[:5]
    for post in posts:
        context["blog_posts"].append({
            "title": post.title,
            "author": post.author.get_full_name(),
            "category": post.category.name if post.category else "Sans catégorie"
        })
    
    # Dernières activités publiées
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
    
    # Vérifier les salutations/remerciements
    for intent_data in intents:
        if intent_data["intent_name"] == "support_general":
            for phrase in intent_data["training_phrases"]:
                if get_close_matches(text.lower(), [phrase.lower()], n=1, cutoff=0.8):
                    if any(word in text.lower() for word in ["bonjour", "salut", "hello", "mwaramutse"]):
                        return "support_general", "greeting"
                    elif any(word in text.lower() for word in ["merci", "murakoze", "thank"]):
                        return "support_general", "thanks"
    
    # Chercher l'intention la plus proche
    best_match_score = 0.6
    matched_intent = None
    matched_key = None
    
    for intent_data in intents:
        for phrase in intent_data["training_phrases"]:
            matches = get_close_matches(text.lower(), [phrase.lower()], n=1, cutoff=best_match_score)
            if matches:
                matched_intent = intent_data["intent_name"]
                # Déterminer la clé de réponse
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


def find_language(text, chat):
    """Détecte la langue avec Gemini"""
    prompt = f"What is the language of this sentence: '{text}'? Respond with only one word: 'French', 'English', 'Kirundi', or 'Swahili'."
    try:
        response = chat.send_message(prompt).text.strip().lower()
        if "french" in response or "français" in response:
            return "fr"
        elif "kirundi" in response:
            return "rn"
        elif "english" in response or "anglais" in response:
            return "en"
        elif "swahili" in response:
            return "sw"
        return "fr"
    except Exception:
        return "fr"


def start_new_chat(session_key):
    """Démarre une nouvelle session chat"""
    chat = model.start_chat()
    session_chats[session_key] = chat
    return chat


def get_chat(session_key):
    """Récupère ou crée un chat"""
    return session_chats.get(session_key) or start_new_chat(session_key)


def send_message(text, session_key):
    """Logique principale du chatbot"""
    chat = get_chat(session_key)
    dataset = load_json_dataset()
    
    try:
        user_language = find_language(text, chat)
        intent_name, response_key = find_intent(text)
        
        # Récupérer le contexte de la DB
        db_context = get_database_context()
        
        dataset_response = get_response_for_intent(intent_name, response_key, user_language, dataset)
        
        lang_full = {"fr": "français", "rn": "kirundi", "en": "anglais"}.get(user_language, "français")
        
        if dataset_response:
            prompt = (
                f"L'utilisateur a posé la question suivante en {lang_full} : '{text}'. "
                f"Voici la réponse de référence du Centre Jeunes Kamenge : '{dataset_response}'. "
                f"Contexte supplémentaire de la base de données : "
                f"- Nombre de membres actifs : {db_context['members_count']} "
                f"- Derniers articles de blog : {db_context['blog_posts']} "
                f"- Dernières activités : {db_context['activities']} "
                f"Reformule cette réponse de manière naturelle et empathique en tant qu'assistant du CJK. "
                f"Réponds UNIQUEMENT en {lang_full}. Sois concis et direct."
            )
        else:
            prompt = (
                f"L'utilisateur a posé la question suivante en {lang_full} : '{text}'. "
                f"Tu es l'assistant virtuel du Centre Jeunes Kamenge (CJK), un centre social au Burundi. "
                f"Contexte de la base de données : "
                f"- Nombre de membres actifs : {db_context['members_count']} "
                f"- Derniers articles de blog : {db_context['blog_posts']} "
                f"- Dernières activités : {db_context['activities']} "
                f"Réponds de manière utile en {lang_full}. Si tu ne sais pas, propose de contacter le centre."
            )
        
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Erreur : {str(e)}"


def user_language_to_full_name(lang_code):
    return {"fr": "français", "rn": "kirundi", "en": "anglais", "sw": "swahili"}.get(lang_code, "français")
