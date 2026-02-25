# 🤖 Agentic RAG - Workflow v3

מערכת RAG (Retrieval-Augmented Generation) שמנתבת אוטומטית בין **שיחה חופשית** ל**חילוץ נתונים מובנה** מתוך תיעוד הפרויקט.

---

## מטרת הפרויקט

- **תשאול חכם על תיעוד:** שאלות על מסמכי הפרויקט (למשל מתיקיית `agent_docs`) מקבלות תשובות מבוססות חיפוש סמנטי (Pinecone + Cohere).
- **ניתוב אוטומטי:** לפי כוונת השאלה המערכת בוחרת:
  - **מסלול צ'אט** — תשובה טקסטואלית חופשית.
  - **מסלול חילוץ** — רשימה מובנית של החלטות/כללים/אזהרות (עם ID, מקור, תאריך) ושמירה ל־JSON.
- **חילוץ מובנה:** כשמבקשים רשימה או סיכום — הנתונים נחלצים לסכמה מוגדרת (decisions, rules, warnings) ונשמרים בקובץ `extracted_insights.json`.

---

## דרישות מקדימות

- Python 3.10+
- מפתחות API:
  - **Cohere** (`COHERE_API_KEY`) — למודל השפה ול־embeddings
  - **Pinecone** (`PINECONE_API_KEY`) — לאחסון וקטורים

---

## התקנה והרצה

### 1. התקנת תלויות

```bash
cd agentic-rag-project
python -m venv venv
venv\Scripts\activate   # Windows
# או: source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

(אם אין `requirements.txt`, התקיני ידנית: `gradio`, `python-dotenv`, `llama-index-*`, `pinecone-client`, וכו'.)

### 2. הגדרת משתני סביבה

צרי קובץ `.env` בשורש הפרויקט:

```env
COHERE_API_KEY=your_cohere_key
PINECONE_API_KEY=your_pinecone_key
```

### 3. טעינת התיעוד ל־Pinecone (פעם ראשונה)

הניחי את קבצי התיעוד (למשל `.md`) בתיקייה `agent_docs` (מעל תיקיית הפרויקט, או התאמי את הנתיב ב־`ingest_data.py`), ואז:

```bash
python ingest_data.py
```

### 4. הרצת האפליקציה

```bash
python app.py
```

בטרמינל יופיע קישור מקומי (למשל `http://127.0.0.1:7860`). פתחי בדפדפן כדי להשתמש בצ'אט.

---

## דוגמאות לשאלות שה-Agent יודע לענות עליהן

### מסלול צ'אט (תשובה חופשית)

- "מה סוכם לגבי ה-Frontend?"
- "מה הוחלט לגבי השרת?"
- "תסבירי מה נכתב בתיעוד על הארכיטקטורה."
- "אילו טכנולוגיות משתמשים בפרויקט?"

### מסלול חילוץ (רשימה מובנית + שמירה ל־JSON)

- "תביאי רשימה של החלטות טכניות."
- "חלצי כל הכללים וההנחיות מהתיעוד."
- "סיכום של כל ההחלטות, הכללים והאזהרות בפרויקט."
- "רשימת אזהרות והנחיות חשובות."

אחרי חילוץ — התוצאה מוצגת בממשק **ונשמרת** גם בקובץ `extracted_insights.json` בתיקיית הפרויקט.

---

## מבנה הפרויקט (תמצית)

| קובץ / תיקייה      | תפקיד |
|--------------------|--------|
| `app.py`           | Workflow ראשי: שליפה → ולידציה → ניתוב → צ'אט או חילוץ; ממשק Gradio. |
| `schema.py`        | סכמת החילוץ: `TechnicalPoint` (id, category, title, content, priority, source, observed_at), `ProjectInsights`. |
| `ingest_data.py`   | טעינת מסמכים מ־`agent_docs`, chunking והעלאה ל־Pinecone. |
| `.env`             | מפתחות Cohere ו־Pinecone (לא להעלות ל־Git). |
| `extracted_insights.json` | נוצר אוטומטית בכל ריצת חילוץ מוצלחת. |
| `workflow_graph.html`    | תרשים ה־workflow (נוצר בהרצת `app.py`). |

---

## רישיון והערות

פרויקט לימוד/הדגמה. יש להקפיד על שימוש אחראי ב־API keys ולא להעלות אותם ל־repo ציבורי.
