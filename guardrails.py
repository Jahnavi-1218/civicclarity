import re
from config import OFFICIAL_CHANNEL_TEXT

# ---------- Layer 1: input pre-filter ----------

REGISTER_RE = re.compile(
    r"(^\s*(please\s+|pls\s+|kindly\s+)?(can|could|will|would)?\s*(you\s+)?(please\s+)?"
    r"(register|file|lodge|raise|submit|log)\b)"
    r"|((register|file|lodge|raise|submit|log)\b.{0,40}\b(for me|on my behalf)\b)"
    r"|(\bi\s+(want|need|would like|wish)\s+to\s+(register|file|lodge|raise|submit)\b)"
    r"|(ignore\s+(all\s+)?(the\s+)?(previous|above|prior)\s+instructions)",
    re.IGNORECASE,
)

TRACK_RE = re.compile(
    r"\b(complaint|grievance|ticket|reference)\b[^0-9]{0,20}\d{4,}"
    r"|\b(status|track|tracking)\s+(of\s+)?my\s+(complaint|grievance|ticket)"
    r"|\bwhere\s+is\s+my\s+(complaint|grievance)\b",
    re.IGNORECASE,
)

DOMAIN_WORDS = [
    "complain", "grievance", "road", "pothole", "footpath", "water", "drain", "sewer",
    "sewage", "leak", "electric", "power", "streetlight", "light", "garbage", "waste",
    "sanitation", "toilet", "escalat", "resol", "timeline", "time", "department", "ward",
    "zone", "municipal", "city", "process", "officer", "helpline", "portal", "file",
    "filing", "document", "information", "info", "status", "ticket", "reference",
    "closure", "acknowledg", "verification", "level", "appeal", "ombudsman", "smart",
    "explain", "simpl", "detail", "step", "example", "again", "more", "elaborate",
    "shorter", "hindi", "telugu", "english", "translate",
]
DOMAIN_RE = re.compile(r"\b(" + "|".join(DOMAIN_WORDS) + r")", re.IGNORECASE)


def classify_intent(text):
    """Returns REGISTER, TRACK, OFFTOPIC or OK."""
    if REGISTER_RE.search(text):
        return "REGISTER"
    if TRACK_RE.search(text):
        return "TRACK"
    if len(text.split()) > 3 and not DOMAIN_RE.search(text):
        return "OFFTOPIC"
    return "OK"


def redirect_message(intent):
    if intent == "REGISTER":
        return (f"I can't register or file complaints, because I'm an explanation-only assistant. "
                f"I can explain how filing works, what details you'll need, and what happens next. "
                f"To actually file, please use {OFFICIAL_CHANNEL_TEXT}.")
    if intent == "TRACK":
        return (f"I can't look up or track complaint status, and I don't have access to any case data. "
                f"Please check your reference ID on {OFFICIAL_CHANNEL_TEXT}. "
                f"I can explain what each status stage typically means.")
    return ("I'm focused on explaining city grievance processes (roads, water, electricity and "
            "sanitation). Try asking about categories, resolution steps, timelines or escalation.")


# ---------- PII masking ----------

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
AADHAAR_RE = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
PHONE_RE = re.compile(r"\b(?:\+?91[-\s]?)?[6-9]\d{9}\b")


def mask_pii(text):
    masked = text
    found = False
    for pattern in (EMAIL_RE, AADHAAR_RE, PHONE_RE):
        masked, n = pattern.subn("[REDACTED]", masked)
        if n:
            found = True
    return masked, found


# ---------- Layer 3: output post-filter ----------

BAD_OUTPUT_RE = re.compile(
    r"i\s+(have|'ve)\s+(registered|filed|submitted|logged)"
    r"|your\s+(complaint|grievance)\s+(has been|is)\s+(registered|filed|submitted)"
    r"|i\s+(will|'ll)\s+(ensure|guarantee|make sure)"
    r"|\bi\s+promise\b"
    r"|\bguaranteed?\b"
    r"|will\s+be\s+(fixed|resolved)\s+(within|by|in)\b",
    re.IGNORECASE,
)

SAFETY_NOTE = ("\n\n> ⚠️ Note: I can't register complaints or promise outcomes. "
               "Timelines are indicative only.")


def postfilter(response):
    """Returns (response, flagged)."""
    if BAD_OUTPUT_RE.search(response):
        return response + SAFETY_NOTE, True
    return response, False