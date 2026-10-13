"""
Custom CSS for Task 05 Streamlit Chatbot Interface.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.5rem; padding-bottom: 2.5rem; }

.hero-banner {
    background: linear-gradient(135deg, #091e3a 0%, #0c4a6e 50%, #0369a1 100%);
    padding: 2rem 2rem 1.6rem;
    border-radius: 16px;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
}
.hero-title { font-size: 2rem; font-weight: 800; margin-bottom: 0.2rem; }
.hero-sub { color: #bae6fd; font-size: 0.95rem; }
.hero-badge {
    display: inline-block;
    background: rgba(14, 165, 233, 0.25);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #e0f2fe;
    padding: 0.18rem 0.65rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.35rem;
}

.intent-pill {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.intent-tool-use { background: #dbeafe; color: #1d4ed8; border: 1px solid #93c5fd; }
.intent-chitchat { background: #f3e8ff; color: #7e22ce; border: 1px solid #d8b4fe; }
.intent-question { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.intent-command { background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; }

.tool-trace-card {
    background: #f8fafc;
    border-left: 4px solid #0284c7;
    border-radius: 0 8px 8px 0;
    padding: 0.6rem 0.9rem;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    color: #334155;
}
</style>
"""
