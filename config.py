import os
from dotenv import load_dotenv

load_dotenv()

# --- ENVIRONMENT VARIABLES ---
TOKEN = os.getenv("DISCORD_TOKEN")
PDF_CHANNEL_ID = int(os.getenv("PDF_CHANNEL_ID", "0"))  # Default to 0 if not set

# --- ALLOWED LANGUAGES ---
ALLOWED_LANGUAGES = ["en", "fr", "ar", "tr", "pr", "ur", "de"]

# --- CATEGORY LIST ---
ALLOWED_CATEGORIES = [
    "Philosophy", "Literature", "Math", "Science", "Traditional Islamic Studies", 
    "Politics", "Natural Sciences", "Computer Science", "Engineering", "History", "Art",
    "Western Islamic Studies"
]

# --- CATEGORY DESCRIPTIONS ---
CATEGORY_DESCRIPTIONS = {
    "Philosophy": "Texts dealing with philosophical concepts, thinkers, or traditions.",
    "Literature": "Novels, poetry, plays, and literary criticism.",
    "Math": "Mathematical theory, problem solving, or education.",
    "Science": "Scientific research or popular science works across all disciplines.",
    "Traditional Islamic Studies": "Books related to Islamic theology, law, history, and spirituality.",
    "Politics": "Political theory, commentary, and historical documents.",
    "Western Islamic Studies": "Islamic studies from Western academic perspectives.",
    "Natural Sciences": "Books related to biology, chemistry, physics, earth sciences, etc.",
    "Computer Science": "Texts related to programming, algorithms, data structures, and computing theory.",
    "Engineering": "Books related to various fields of engineering, including civil, electrical, mechanical, etc.",
    "History": "Historical accounts, events, and analysis from any time period.",
    "Art": "Books on visual arts, literature, music, and more."
}

# --- CATEGORY EMOJIS ---
CATEGORY_EMOJIS = {
    "Philosophy": "🧠",
    "Literature": "📚",
    "Math": "➗",
    "Science": "🔬",
    "Traditional Islamic Studies": "☪️",
    "Politics": "⚖️",
    "Western Islamic Studies": "🤓",
    "Natural Sciences": "🌿",
    "Computer Science": "💻",
    "Engineering": "🛠️",
    "History": "📜",
    "Art": "🎨"
}

# --- CATEGORY > SUBCATEGORIES ---
CATEGORY_SUBCATEGORIES = {
    "Philosophy": [
        "Greek Philosophy",
        "Islamic Philosophy (Falsafa)",
        "Medieval Christian & Jewish Thought",
        "Enlightenment & Rationalism",
        "German Idealism",
        "Postmodernism",
        "Critical Theory",
        "Phenomenology & Existentialism",
        "Logic & Epistemology",
        "Metaphysics",
        "Philosophy of Language",
        "Philosophy of Science",
        "Political Philosophy"
    ],
    "Literature": [
        "Classical Literature",
        "Modern Literature",
        "Poetry",
        "Drama",
        "Literary Criticism",
        "Fiction"
    ],
    "Math": [
        "Algebra",
        "Calculus",
        "Geometry",
        "Statistics",
        "Linear Algebra",
        "Number Theory",
        "Discrete Mathematics"
    ],
    "Science": [
        "Physics",
        "Chemistry",
        "Biology",
        "Astronomy",
        "Earth Sciences",
        "Environmental Science"
    ],
    "Traditional Islamic Studies": [
        "Islamic Theology",
        "Islamic History",
        "Islamic Law",
        "Islamic Mysticism (Sufism)",
        "Islamic Philosophy",
        "Quranic Studies"
    ],
    "Politics": [
        "Political Theory",
        "Political Economy",
        "Political Philosophy",
        "Public Policy",
        "International Relations",
        "Anthropology"
    ],
    "Western Islamic Studies": [
        "Academic Studies",
        "Historical Analysis",
        "Contemporary Studies",
        "Orientalist Works",
        "Critical Analysis"
    ],
    "Natural Sciences": [
        "Physics",
        "Chemistry",
        "Biology",
        "Earth Sciences",
        "Environmental Science"
    ],
    "Computer Science": [
        "Programming",
        "Algorithms",
        "Data Structures",
        "Machine Learning",
        "Artificial Intelligence",
        "Cybersecurity"
    ],
    "Engineering": [
        "Mechanical Engineering",
        "Electrical Engineering",
        "Civil Engineering",
        "Software Engineering",
        "Aerospace Engineering"
    ],
    "History": [
        "Ancient History",
        "Medieval History",
        "Modern History",
        "Contemporary History",
        "History of Civilizations"
    ],
    "Art": [
        "Visual Arts",
        "Music",
        "Literary Arts",
        "Performance Arts",
        "Art History"
    ]
}
