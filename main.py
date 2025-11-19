import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Module, Game, Score, Card, Question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Gamified Study Backend running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Utility to convert ObjectId to str for responses

def _stringify_id(doc):
    if not doc:
        return doc
    d = dict(doc)
    if d.get("_id"):
        d["id"] = str(d.pop("_id"))
    return d

# Simple placeholder AI generator (rule-based) – no external packages
# Converts text into either cards (Q/A) or quiz questions

def _generate_from_text(text: str, game_type: str):
    # Split into sentences and derive simple prompts
    parts = [p.strip() for p in text.replace("\n", " ").split(".") if p.strip()]
    items = parts[:10] if parts else [text]
    if game_type == "cards":
        cards = []
        for i, p in enumerate(items, 1):
            prompt = f"Explain: {p[:80]}"
            answer = p
            cards.append({"prompt": prompt, "answer": answer})
        return {"cards": cards}
    else:
        questions = []
        for i, p in enumerate(items, 1):
            q = f"What best describes this idea: {p[:60]}?"
            correct = "".join(p.split()[:4])
            options = [correct, "Definition", "Example", "Opposite"]
            questions.append({"question": q, "options": options, "correct_index": 0})
        return {"questions": questions}

# Routes

class CreateModuleRequest(BaseModel):
    title: str
    content: str
    author: Optional[str] = None
    game_type: str = "cards"

@app.post("/modules")
def create_module(req: CreateModuleRequest):
    module = Module(title=req.title, content=req.content, author=req.author, game_type=req.game_type)
    module_id = create_document("module", module)

    # Generate a game from the notes
    gen = _generate_from_text(req.content, req.game_type)
    game_doc = {"module_id": module_id, "game_type": req.game_type, **gen}
    game_id = create_document("game", game_doc)

    return {"module_id": module_id, "game_id": game_id}

@app.get("/modules")
def list_modules():
    modules = get_documents("module")
    return [_stringify_id(m) for m in modules]

@app.get("/games/{module_id}")
def get_game(module_id: str):
    # Find the game by module_id
    game = db["game"].find_one({"module_id": module_id})
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return _stringify_id(game)

class SubmitScoreRequest(BaseModel):
    player_name: str
    score: int

@app.post("/scores/{module_id}")
def submit_score(module_id: str, req: SubmitScoreRequest):
    score_doc = Score(module_id=module_id, player_name=req.player_name, score=req.score)
    score_id = create_document("score", score_doc)
    return {"score_id": score_id}

@app.get("/leaderboard/{module_id}")
def leaderboard(module_id: str, limit: int = 10):
    scores = db["score"].find({"module_id": module_id}).sort("score", -1).limit(limit)
    return [_stringify_id(s) for s in scores]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
