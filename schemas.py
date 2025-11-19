"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

class Module(BaseModel):
    """Study module uploaded by a student.
    Collection name: "module"
    """
    title: str = Field(..., description="Module title or topic")
    content: str = Field(..., description="Raw notes or text content provided by user")
    author: Optional[str] = Field(None, description="Name of the creator (optional)")
    game_type: Literal["cards", "quiz"] = Field("cards", description="Type of game to generate")

class Card(BaseModel):
    prompt: str
    answer: str

class Question(BaseModel):
    question: str
    options: List[str]
    correct_index: int

class Game(BaseModel):
    """Generated game for a module.
    Collection name: "game"
    """
    module_id: str
    game_type: Literal["cards", "quiz"]
    cards: Optional[List[Card]] = None
    questions: Optional[List[Question]] = None

class Score(BaseModel):
    """Score entries for leaderboards.
    Collection name: "score"
    """
    module_id: str
    player_name: str
    score: int = Field(..., ge=0)

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
