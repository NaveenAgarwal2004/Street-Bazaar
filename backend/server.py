from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import os
import logging
import bcrypt
import jwt
from dotenv import load_dotenv
from pathlib import Path
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Security
security = HTTPBearer()

# Create FastAPI app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class UserBase(BaseModel):
    email: str
    name: str
    phone: str = ""
    userType: str  # "vendor" or "supplier"

class UserCreate(UserBase):
    password: str
    businessName: str = ""
    city: str = ""
    state: str = ""

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: str
    businessName: str = ""
    city: str = ""
    state: str = ""
    createdAt: datetime

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    description: str = ""
    price: float
    unit: str
    stock: int
    minOrderQty: int = 1
    maxOrderQty: int = 1000
    supplierId: str
    supplierName: str = ""
    isAvailable: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    category: str
    description: str = ""
    price: float
    unit: str
    stock: int
    minOrderQty: int = 1
    maxOrderQty: int = 1000

class CartItem(BaseModel):
    productId: str
    productName: str
    quantity: int
    unitPrice: float
    totalPrice: float
    supplierId: str
    supplierName: str

class OrderCreate(BaseModel):
    items: List[CartItem]
    deliveryAddress: str = ""

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    orderNumber: str
    vendorId: str
    vendorName: str = ""
    supplierId: str
    supplierName: str = ""
    items: List[CartItem]
    totalAmount: float
    status: str = "pending"
    deliveryAddress: str = ""
    createdAt: datetime = Field(default_factory=datetime.utcnow)

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Initialize sample data
async def init_sample_data():
    # Check if data already exists
    existing_users = await db.users.count_documents({})
    if existing_users > 0:
        return
    
    # Sample vendors
    vendors = [
        {
            "id": str(uuid.uuid4()),
            "email": "rajesh.dosa@gmail.com",
            "password": hash_password("demo123"),
            "name": "Rajesh Kumar",
            "phone": "9876543210",
            "userType": "vendor",
            "businessName": "Rajesh Dosa Corner",
            "city": "Delhi",
            "state": "Delhi",
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "sunita.chaat@gmail.com",
            "password": hash_password("demo123"),
            "name": "Sunita Sharma",
            "phone": "9876543211",
            "userType": "vendor",
            "businessName": "Sunita's Chaat Bhandaar",
            "city": "Mumbai",
            "state": "Maharashtra",
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "vikram.paratha@gmail.com",
            "password": hash_password("demo123"),
            "name": "Vikram Singh",
            "phone": "9876543212",
            "userType": "vendor",
            "businessName": "Vikram Paratha Point",
            "city": "Jaipur",
            "state": "Rajasthan",
            "createdAt": datetime.utcnow()
        }
    ]
    
    # Sample suppliers
    suppliers = [
        {
            "id": str(uuid.uuid4()),
            "email": "delhi.agro@gmail.com",
            "password": hash_password("demo123"),
            "name": "Amit Gupta",
            "phone": "9876543213",
            "userType": "supplier",
            "businessName": "Delhi Agro Supplies",
            "city": "Delhi",
            "state": "Delhi",
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "mumbai.oils@gmail.com",
            "password": hash_password("demo123"),
            "name": "Priya Patel",
            "phone": "9876543214",
            "userType": "supplier",
            "businessName": "Mumbai Oil Traders",
            "city": "Mumbai",
            "state": "Maharashtra",
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "punjab.fresh@gmail.com",
            "password": hash_password("demo123"),
            "name": "Harjeet Singh",
            "phone": "9876543215",
            "userType": "supplier",
            "businessName": "Punjab Fresh Supply",
            "city": "Chandigarh",
            "state": "Punjab",
            "createdAt": datetime.utcnow()
        }
    ]
    
    # Insert users
    all_users = vendors + suppliers
    await db.users.insert_many(all_users)
    
    # Sample products
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Premium Basmati Rice",
            "category": "grains",
            "description": "Long grain premium quality rice from Punjab",
            "price": 45.0,
            "unit": "kg",
            "stock": 500,
            "minOrderQty": 10,
            "maxOrderQty": 100,
            "supplierId": suppliers[0]["id"],
            "supplierName": suppliers[0]["businessName"],
            "isAvailable": True,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Refined Sunflower Oil",
            "category": "oils",
            "description": "Cold-pressed refined cooking oil",
            "price": 120.0,
            "unit": "liter",
            "stock": 200,
            "minOrderQty": 5,
            "maxOrderQty": 50,
            "supplierId": suppliers[1]["id"],
            "supplierName": suppliers[1]["businessName"],
            "isAvailable": True,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Fresh Red Onions",
            "category": "vegetables",
            "description": "Farm-fresh red onions from Punjab",
            "price": 25.0,
            "unit": "kg",
            "stock": 300,
            "minOrderQty": 20,
            "maxOrderQty": 100,
            "supplierId": suppliers[2]["id"],
            "supplierName": suppliers[2]["businessName"],
            "isAvailable": True,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Turmeric Powder",
            "category": "spices",
            "description": "Pure organic turmeric powder",
            "price": 180.0,
            "unit": "kg",
            "stock": 80,
            "minOrderQty": 2,
            "maxOrderQty": 20,
            "supplierId": suppliers[0]["id"],
            "supplierName": suppliers[0]["businessName"],
            "isAvailable": True,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pure Ghee",
            "category": "dairy",
            "description": "Traditional cow milk ghee",
            "price": 450.0,
            "unit": "kg",
            "stock": 50,
            "minOrderQty": 1,
            "maxOrderQty": 10,
            "supplierId": suppliers[2]["id"],
            "supplierName": suppliers[2]["businessName"],
            "isAvailable": True,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cumin Seeds",
            "category": "spices",
            "description": "Whole cumin seeds from Rajasthan",
            "price": 320.0,
            "unit": "kg",
            "stock": 100,
            "minOrderQty": 5,
            "maxOrderQty": 25,
            "supplierId": suppliers[0]["id"],
            "supplierName": suppliers[0]["businessName"],
            "isAvailable": True,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Refined Wheat Flour",
            "category": "grains",
            "description": "Fine quality wheat flour for rotis",
            "price": 35.0,
            "unit": "kg",
            "stock": 400,
            "minOrderQty": 25,
            "maxOrderQty": 100,
            "supplierId": suppliers[1]["id"],
            "supplierName": suppliers[1]["businessName"],
            "isAvailable": True,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Fresh Tomatoes",
            "category": "vegetables",
            "description": "Ripe red tomatoes from local farms",
            "price": 30.0,
            "unit": "kg",
            "stock": 150,
            "minOrderQty": 10,
            "maxOrderQty": 50,
            "supplierId": suppliers[2]["id"],
            "supplierName": suppliers[2]["businessName"],
            "isAvailable": True,
            "createdAt": datetime.utcnow()
        }
    ]
    
    await db.products.insert_many(products)

# API Routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_dict = user.dict()
    user_dict["id"] = str(uuid.uuid4())
    user_dict["password"] = hash_password(user.password)
    user_dict["createdAt"] = datetime.utcnow()
    
    await db.users.insert_one(user_dict)
    
    # Return user without password
    user_dict.pop("password")
    return UserResponse(**user_dict)

@api_router.post("/auth/login")
async def login(user: UserLogin):
    # Find user
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token(data={"sub": db_user["id"]})
    
    # Return user data and token
    db_user.pop("password")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**db_user)
    }

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None, search: Optional[str] = None):
    query = {"isAvailable": True}
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    products = await db.products.find(query).to_list(1000)
    return [Product(**product) for product in products]

@api_router.get("/products/categories")
async def get_categories():
    categories = await db.products.distinct("category")
    return {"categories": categories}

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate, current_user: dict = Depends(get_current_user)):
    if current_user["userType"] != "supplier":
        raise HTTPException(status_code=403, detail="Only suppliers can create products")
    
    product_dict = product.dict()
    product_dict["id"] = str(uuid.uuid4())
    product_dict["supplierId"] = current_user["id"]
    product_dict["supplierName"] = current_user["businessName"]
    product_dict["isAvailable"] = True
    product_dict["createdAt"] = datetime.utcnow()
    
    await db.products.insert_one(product_dict)
    return Product(**product_dict)

@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate, current_user: dict = Depends(get_current_user)):
    if current_user["userType"] != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can create orders")
    
    # Calculate total amount
    total_amount = sum(item.totalPrice for item in order_data.items)
    
    # Create order
    order_dict = {
        "id": str(uuid.uuid4()),
        "orderNumber": f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "vendorId": current_user["id"],
        "vendorName": current_user["businessName"],
        "supplierId": order_data.items[0].supplierId if order_data.items else "",
        "supplierName": order_data.items[0].supplierName if order_data.items else "",
        "items": [item.dict() for item in order_data.items],
        "totalAmount": total_amount,
        "status": "pending",
        "deliveryAddress": order_data.deliveryAddress,
        "createdAt": datetime.utcnow()
    }
    
    await db.orders.insert_one(order_dict)
    return Order(**order_dict)

@api_router.get("/orders", response_model=List[Order])
async def get_orders(current_user: dict = Depends(get_current_user)):
    if current_user["userType"] == "vendor":
        orders = await db.orders.find({"vendorId": current_user["id"]}).to_list(1000)
    else:
        orders = await db.orders.find({"supplierId": current_user["id"]}).to_list(1000)
    
    return [Order(**order) for order in orders]

@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str, current_user: dict = Depends(get_current_user)):
    if current_user["userType"] != "supplier":
        raise HTTPException(status_code=403, detail="Only suppliers can update order status")
    
    result = await db.orders.update_one(
        {"id": order_id, "supplierId": current_user["id"]},
        {"$set": {"status": status}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Order status updated successfully"}

# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "StreetBazaar API is running!"}

# Include router
app.include_router(api_router)

# Initialize sample data on startup
@app.on_event("startup")
async def startup_event():
    await init_sample_data()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    client.close()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)