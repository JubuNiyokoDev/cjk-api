"""Analyse des hashtags saisis librement ("#paix #jeunesse, sport")."""
import re

SPLIT_RE = re.compile(r'[\s,;]+')


def parse_hashtags(raw):
    """Retourne la liste des hashtags normalisés (sans '#', sans doublons)."""
    if not raw:
        return []
    tags = []
    for token in SPLIT_RE.split(raw.strip()):
        tag = token.strip().lstrip('#')
        if tag and tag not in tags:
            tags.append(tag)
    return tags
