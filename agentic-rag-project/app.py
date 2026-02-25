import os
import gradio as gr
from dotenv import load_dotenv
from schema import ProjectInsights, TechnicalPoint, ExtractionEvent, ChatEvent
from llama_index.core.workflow import Workflow, step, StartEvent, StopEvent, Event
from llama_index.core.base.llms.types import ChatMessage, MessageRole

load_dotenv()

# --- הגדרות בסיס ---
MY_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

_retriever = None
_response_synthesizer = None
_llm = None # הוספתי כדי שנוכל להשתמש בו ב-Extraction

def _init_rag_components():
    global _retriever, _response_synthesizer, _llm
    if _retriever is not None and _response_synthesizer is not None:
        return _retriever, _response_synthesizer, _llm

    from llama_index.core import VectorStoreIndex, get_response_synthesizer
    from llama_index.embeddings.cohere import CohereEmbedding
    from llama_index.llms.cohere import Cohere  # וודאי שזה מיובא מ-llms.cohere
    from llama_index.vector_stores.pinecone import PineconeVectorStore
    from pinecone import Pinecone

    embed_model = CohereEmbedding(api_key=MY_API_KEY, model_name="embed-multilingual-v3.0")
    
    # התיקון כאן: שימוש במודל עדכני + timeout כדי לא להיתקע על קריאות API ארוכות
    _llm = Cohere(
        api_key=MY_API_KEY,
        model="command-r-08-2024",
        timeout=120.0,
    )

    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index("agentic-docs-index")
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)
    _retriever = index.as_retriever(similarity_top_k=5)
    
    # חשוב: לוודא שהסינתיסייזר משתמש ב-LLM המעודכן
    _response_synthesizer = get_response_synthesizer(llm=_llm)
    
    return _retriever, _response_synthesizer, _llm

# --- הגדרת אירועים (Events) ---
class RetrievalEvent(Event):
    nodes: list
    query: str

class ValidationEvent(Event):
    nodes: list
    query: str

class ExtractionEvent(Event): # אירוע למסלול חילוץ
    nodes: list
    query: str

class ChatEvent(Event): # אירוע למסלול צ'אט רגיל
    nodes: list
    query: str

# --- הגדרת ה-Workflow ---
class RAGWorkflow(Workflow):
    
    @step
    async def retrieve_step(self, ev: StartEvent) -> RetrievalEvent | StopEvent:
        query = ev.get("query")
        if not query or query.strip() == "":
            return StopEvent(result="השאילתה ריקה, אנא נסו שוב.")
        
        print(f"🔎 מחפש מידע עבור: {query}")
        retriever, _, _ = _init_rag_components()
        nodes = retriever.retrieve(query)
        return RetrievalEvent(nodes=nodes, query=query)

    @step
    async def validate_step(self, ev: RetrievalEvent) -> ValidationEvent | StopEvent:
        if not ev.nodes:
            return StopEvent(result="לא מצאתי מידע רלוונטי בתיעוד הפרויקט.")
        return ValidationEvent(nodes=ev.nodes, query=ev.query)
    @step
    async def router_step(self, ev: ValidationEvent) -> ExtractionEvent | ChatEvent:
        """נתב חכם המשתמש ב-LLM כדי להבין את כוונת המשתמש"""
        print(f"🧠 ה-LLM מנתח את כוונת השאלה: '{ev.query}'")
        
        _, _, llm = _init_rag_components()
        
        # בניית פרומפט קצר וחד לניתוב
        router_prompt = (
            "You are a router agent. Categorize the user's query into one of two categories:\n"
            "1. 'EXTRACTION': If the user wants a structured list, a summary of decisions, rules, or insights.\n"
            "2. 'CHAT': If the user is asking a general question, seeking an explanation, or just chatting.\n\n"
            f"Query: {ev.query}\n"
            "Answer only with the word 'EXTRACTION' or 'CHAT'."
        )
        
        chat_response = await llm.achat(
            [ChatMessage(role=MessageRole.USER, content=router_prompt)]
        )
        decision = (chat_response.message.content or "").strip().upper()
        
        if "EXTRACTION" in decision:
            print("🔀 ה-LLM החליט: ניתוב למסלול חילוץ נתונים (Extraction)")
            return ExtractionEvent(nodes=ev.nodes, query=ev.query)
        else:
            print("🔀 ה-LLM החליט: ניתוב למסלול שיחה (Chat)")
            return ChatEvent(nodes=ev.nodes, query=ev.query)
    @step
    async def extract_insights(self, ev: ExtractionEvent) -> StopEvent:
        """חילוץ נתונים מובנים ושמירה לקובץ JSON"""
        print("📊 מחלץ נתונים מובנים מהטקסט...")
        
        _, _, llm = _init_rag_components()
        
        # איחוד הטקסט מה-Nodes + הגבלה כדי שהבקשה ל-LLM לא תהיה ענקית (מקור לעיכובים)
        MAX_CONTEXT_CHARS = 8_000  # קטן יותר = תשובה מהירה יותר מ-Cohere
        raw_context = "\n".join([n.get_content() for n in ev.nodes])
        context_str = raw_context[:MAX_CONTEXT_CHARS]
        if len(raw_context) > MAX_CONTEXT_CHARS:
            context_str += "\n\n[... טקסט קוצר לצורך חילוץ ...]"
        
        # פרומפט מפורט כדי לקבל את כל השדות של המטלה
        prompt = (
            "Based on the text below, extract technical insights as a JSON object.\n"
            "Format the output exactly like this JSON structure:\n"
            "{\n"
            "  'items': [\n"
            "    {\n"
            "      'id': 'unique string like dec-001',\n"
            "      'category': 'decisions', 'rules', or 'warnings',\n"
            "      'title': 'short title',\n"
            "      'content': 'description',\n"
            "      'priority': 'High/Medium/Low',\n"
            "      'source': {'file': 'filename', 'anchor': 'section'},\n"
            "      'observed_at': '2026-02-25'\n"
            "    }\n"
            "  ]\n"
            "}\n"
            f"Text content:\n{context_str}"
        )

        try:
            # שימוש ב-Chat API הישיר (הכי יציב)
            from llama_index.core.llms import ChatMessage
            response = await llm.achat([ChatMessage(role="user", content=prompt)])

            # ניקוי התשובה מסימני Markdown אם ה-LLM הוסיף כאלו
            raw = response.message.content or ""
            res_text = raw.replace("```json", "").replace("```", "").strip()

            # שמירה פיזית לקובץ JSON (json.dump)
            import json
            try:
                data = json.loads(res_text)
            except json.JSONDecodeError:
                with open("extracted_insights.json", "w", encoding="utf-8") as f:
                    f.write(res_text)
                print("💾 נתונים גולמיים נשמרו (JSON לא תקני)")
                return StopEvent(result="החילוץ הסתיים אך התשובה אינה JSON תקני. הנתונים הגולמיים נשמרו ל־`extracted_insights.json`.")

            with open("extracted_insights.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print("💾 הנתונים נשמרו בהצלחה ל-extracted_insights.json")

            # בניית דוח קריא למשתמש (עברית, ממוין לפי קטגוריה)
            items = data.get("items") or []
            by_cat = {"decisions": [], "rules": [], "warnings": []}
            for it in items:
                cat = (it.get("category") or "").lower().strip()
                if cat in by_cat:
                    by_cat[cat].append(it)

            n_dec, n_rules, n_warn = len(by_cat["decisions"]), len(by_cat["rules"]), len(by_cat["warnings"])

            def _priority_emoji(p):
                if not p:
                    return "🟡"
                p = str(p).lower()
                if "high" in p:
                    return "🔴"
                if "low" in p:
                    return "🟢"
                return "🟡"

            def _format_item(it):
                title = it.get("title") or "(ללא כותרת)"
                content = it.get("content") or ""
                priority = it.get("priority") or "Medium"
                src = it.get("source") or {}
                src_file = src.get("file") if isinstance(src, dict) else ""
                emoji = _priority_emoji(priority)
                meta = f"{emoji} עדיפות: {priority}"
                if src_file:
                    meta += f"  •  מקור: {src_file}"
                return f"**{title}**\n\n> {content}\n\n_{meta}_"

            lines = []
            # סיכום מנהלים
            lines.append("ניתחתי את התיעוד ומצאתי **{}** החלטות, **{}** כללים ו-**{}** אזהרות.\n".format(
                n_dec, n_rules, n_warn
            ))

            # קטגוריות עם כותרות בעברית
            if by_cat["decisions"]:
                lines.append("### 🎯 החלטות\n")
                for it in by_cat["decisions"]:
                    lines.append(_format_item(it))
                    lines.append("")
            if by_cat["rules"]:
                lines.append("### 📋 כללים\n")
                for it in by_cat["rules"]:
                    lines.append(_format_item(it))
                    lines.append("")
            if by_cat["warnings"]:
                lines.append("### ⚠️ אזהרות\n")
                for it in by_cat["warnings"]:
                    lines.append(_format_item(it))
                    lines.append("")

            lines.append("---")
            lines.append("_הנתונים המבניים המלאים נשמרו לקובץ `extracted_insights.json`._")

            formatted_res = "\n".join(lines).strip()
            return StopEvent(result=formatted_res)
            
        except Exception as e:
            print(f"❌ שגיאה בחילוץ: {e}")
            return StopEvent(result=f"נכשלתי בחילוץ הנתונים. שגיאה: {str(e)}")

    @step
    async def synthesize_step(self, ev: ChatEvent) -> StopEvent:
        """ניסוח תשובת צ'אט רגילה"""
        print("✍️ מנסח תשובה...")
        _, response_synthesizer, _ = _init_rag_components()
        response = response_synthesizer.synthesize(
            query=ev.query,
            nodes=ev.nodes
        )
        return StopEvent(result=str(response))

# יצירת מופע של ה-Workflow (timeout 300s: retrieve + router + extract עלולים לקחת זמן)
rag_wf = RAGWorkflow(timeout=300)

async def chat_function(message, history):
    try:
        result = await rag_wf.run(query=message)
        return str(result)
    except Exception as e:
        return f"❌ שגיאה בתהליך: {str(e)}"

# --- ממשק Gradio ---
demo = gr.ChatInterface(
    fn=chat_function,
    title="🤖 Agentic RAG - Workflow v3",
    description="מערכת חכמה המנתבת בין תשובות רגילות לחילוץ נתונים מובנה. שאלו שאלה או בקשו רשימת החלטות/כללים/אזהרות."
)

if __name__ == "__main__":
    try:
        from llama_index.utils.workflow import draw_all_possible_flows
        draw_all_possible_flows(rag_wf, filename="workflow_graph.html")
        print("🎨 Workflow graph saved to: workflow_graph.html")
    except Exception as e:
        print(f"⚠️ Failed to generate workflow graph. Error: {e}")

    demo.launch()