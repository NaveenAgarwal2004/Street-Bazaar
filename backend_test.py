#!/usr/bin/env python3
"""
StreetBazaar Backend API Testing Suite
Tests all backend endpoints comprehensively
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://0cede680-dc33-4764-a457-9c0b2c5dd951.preview.emergentagent.com/api"

# Demo credentials
DEMO_VENDOR = {"email": "rajesh.dosa@gmail.com", "password": "demo123"}
DEMO_SUPPLIER = {"email": "delhi.agro@gmail.com", "password": "demo123"}

class StreetBazaarTester:
    def __init__(self):
        self.vendor_token = None
        self.supplier_token = None
        self.vendor_user = None
        self.supplier_user = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_api_health(self):
        """Test if API is running"""
        try:
            response = requests.get(f"{BASE_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", True, f"API is running: {data.get('message', 'OK')}")
                return True
            else:
                self.log_test("API Health Check", False, f"API returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Failed to connect to API: {str(e)}")
            return False
    
    def test_vendor_login(self):
        """Test vendor login with demo credentials"""
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=DEMO_VENDOR, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.vendor_token = data["access_token"]
                    self.vendor_user = data["user"]
                    user_type = data["user"].get("userType")
                    business_name = data["user"].get("businessName")
                    self.log_test("Vendor Login", True, f"Login successful for {user_type}: {business_name}")
                    return True
                else:
                    self.log_test("Vendor Login", False, "Missing access_token or user in response")
                    return False
            else:
                self.log_test("Vendor Login", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Vendor Login", False, f"Login request failed: {str(e)}")
            return False
    
    def test_supplier_login(self):
        """Test supplier login with demo credentials"""
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=DEMO_SUPPLIER, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.supplier_token = data["access_token"]
                    self.supplier_user = data["user"]
                    user_type = data["user"].get("userType")
                    business_name = data["user"].get("businessName")
                    self.log_test("Supplier Login", True, f"Login successful for {user_type}: {business_name}")
                    return True
                else:
                    self.log_test("Supplier Login", False, "Missing access_token or user in response")
                    return False
            else:
                self.log_test("Supplier Login", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Supplier Login", False, f"Login request failed: {str(e)}")
            return False
    
    def test_jwt_validation(self):
        """Test JWT token validation with protected endpoint"""
        if not self.vendor_token:
            self.log_test("JWT Validation", False, "No vendor token available for testing")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.vendor_token}"}
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("email") == DEMO_VENDOR["email"]:
                    self.log_test("JWT Validation", True, "Token validation successful")
                    return True
                else:
                    self.log_test("JWT Validation", False, "Token returned wrong user data")
                    return False
            else:
                self.log_test("JWT Validation", False, f"Token validation failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("JWT Validation", False, f"JWT validation request failed: {str(e)}")
            return False
    
    def test_invalid_token(self):
        """Test API behavior with invalid token"""
        try:
            headers = {"Authorization": "Bearer invalid_token_here"}
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            if response.status_code == 401:
                self.log_test("Invalid Token Handling", True, "API correctly rejected invalid token")
                return True
            else:
                self.log_test("Invalid Token Handling", False, f"API should return 401 for invalid token, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Invalid Token Handling", False, f"Invalid token test failed: {str(e)}")
            return False
    
    def test_get_products(self):
        """Test getting all products"""
        try:
            response = requests.get(f"{BASE_URL}/products", timeout=10)
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) > 0:
                    self.log_test("Get Products", True, f"Retrieved {len(products)} products")
                    return products
                else:
                    self.log_test("Get Products", False, "No products found or invalid response format")
                    return []
            else:
                self.log_test("Get Products", False, f"Failed to get products, status {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Get Products", False, f"Get products request failed: {str(e)}")
            return []
    
    def test_get_categories(self):
        """Test getting product categories"""
        try:
            response = requests.get(f"{BASE_URL}/products/categories", timeout=10)
            if response.status_code == 200:
                data = response.json()
                categories = data.get("categories", [])
                if isinstance(categories, list) and len(categories) > 0:
                    self.log_test("Get Categories", True, f"Retrieved categories: {', '.join(categories)}")
                    return categories
                else:
                    self.log_test("Get Categories", False, "No categories found")
                    return []
            else:
                self.log_test("Get Categories", False, f"Failed to get categories, status {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Get Categories", False, f"Get categories request failed: {str(e)}")
            return []
    
    def test_product_search(self):
        """Test product search functionality"""
        try:
            # Test search by name
            response = requests.get(f"{BASE_URL}/products?search=rice", timeout=10)
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list):
                    rice_products = [p for p in products if 'rice' in p.get('name', '').lower()]
                    if len(rice_products) > 0:
                        self.log_test("Product Search", True, f"Found {len(rice_products)} rice products")
                        return True
                    else:
                        self.log_test("Product Search", False, "Search returned products but none contain 'rice'")
                        return False
                else:
                    self.log_test("Product Search", False, "Invalid search response format")
                    return False
            else:
                self.log_test("Product Search", False, f"Search failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Product Search", False, f"Product search request failed: {str(e)}")
            return False
    
    def test_category_filter(self):
        """Test product filtering by category"""
        try:
            response = requests.get(f"{BASE_URL}/products?category=grains", timeout=10)
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list):
                    grain_products = [p for p in products if p.get('category') == 'grains']
                    if len(grain_products) > 0:
                        self.log_test("Category Filter", True, f"Found {len(grain_products)} grain products")
                        return True
                    else:
                        self.log_test("Category Filter", False, "No grain products found")
                        return False
                else:
                    self.log_test("Category Filter", False, "Invalid filter response format")
                    return False
            else:
                self.log_test("Category Filter", False, f"Category filter failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Category Filter", False, f"Category filter request failed: {str(e)}")
            return False
    
    def test_create_product(self):
        """Test product creation by supplier"""
        if not self.supplier_token:
            self.log_test("Create Product", False, "No supplier token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.supplier_token}"}
            new_product = {
                "name": "Test Organic Lentils",
                "category": "grains",
                "description": "Premium organic lentils for testing",
                "price": 85.0,
                "unit": "kg",
                "stock": 100,
                "minOrderQty": 5,
                "maxOrderQty": 50
            }
            
            response = requests.post(f"{BASE_URL}/products", json=new_product, headers=headers, timeout=10)
            if response.status_code == 200:
                product = response.json()
                if product.get("name") == new_product["name"]:
                    self.log_test("Create Product", True, f"Created product: {product.get('name')}")
                    return product
                else:
                    self.log_test("Create Product", False, "Product created but data mismatch")
                    return None
            else:
                self.log_test("Create Product", False, f"Product creation failed with status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Create Product", False, f"Create product request failed: {str(e)}")
            return None
    
    def test_vendor_create_product_forbidden(self):
        """Test that vendors cannot create products"""
        if not self.vendor_token:
            self.log_test("Vendor Product Creation (Forbidden)", False, "No vendor token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.vendor_token}"}
            new_product = {
                "name": "Test Product by Vendor",
                "category": "test",
                "description": "This should fail",
                "price": 100.0,
                "unit": "kg",
                "stock": 10,
                "minOrderQty": 1,
                "maxOrderQty": 10
            }
            
            response = requests.post(f"{BASE_URL}/products", json=new_product, headers=headers, timeout=10)
            if response.status_code == 403:
                self.log_test("Vendor Product Creation (Forbidden)", True, "Correctly blocked vendor from creating products")
                return True
            else:
                self.log_test("Vendor Product Creation (Forbidden)", False, f"Should return 403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Vendor Product Creation (Forbidden)", False, f"Request failed: {str(e)}")
            return False
    
    def test_create_order(self):
        """Test order creation by vendor"""
        if not self.vendor_token:
            self.log_test("Create Order", False, "No vendor token available")
            return False
        
        # First get a product to order
        products = self.test_get_products()
        if not products:
            self.log_test("Create Order", False, "No products available to create order")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.vendor_token}"}
            product = products[0]  # Use first product
            
            order_data = {
                "items": [
                    {
                        "productId": product["id"],
                        "productName": product["name"],
                        "quantity": 10,
                        "unitPrice": product["price"],
                        "totalPrice": product["price"] * 10,
                        "supplierId": product["supplierId"],
                        "supplierName": product["supplierName"]
                    }
                ],
                "deliveryAddress": "123 Test Street, Delhi"
            }
            
            response = requests.post(f"{BASE_URL}/orders", json=order_data, headers=headers, timeout=10)
            if response.status_code == 200:
                order = response.json()
                if order.get("orderNumber") and order.get("totalAmount"):
                    self.log_test("Create Order", True, f"Created order {order.get('orderNumber')} for ₹{order.get('totalAmount')}")
                    return order
                else:
                    self.log_test("Create Order", False, "Order created but missing required fields")
                    return None
            else:
                self.log_test("Create Order", False, f"Order creation failed with status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Create Order", False, f"Create order request failed: {str(e)}")
            return None
    
    def test_get_vendor_orders(self):
        """Test getting orders for vendor"""
        if not self.vendor_token:
            self.log_test("Get Vendor Orders", False, "No vendor token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.vendor_token}"}
            response = requests.get(f"{BASE_URL}/orders", headers=headers, timeout=10)
            if response.status_code == 200:
                orders = response.json()
                if isinstance(orders, list):
                    self.log_test("Get Vendor Orders", True, f"Retrieved {len(orders)} orders for vendor")
                    return orders
                else:
                    self.log_test("Get Vendor Orders", False, "Invalid orders response format")
                    return []
            else:
                self.log_test("Get Vendor Orders", False, f"Failed to get orders, status {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Get Vendor Orders", False, f"Get orders request failed: {str(e)}")
            return []
    
    def test_get_supplier_orders(self):
        """Test getting orders for supplier"""
        if not self.supplier_token:
            self.log_test("Get Supplier Orders", False, "No supplier token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.supplier_token}"}
            response = requests.get(f"{BASE_URL}/orders", headers=headers, timeout=10)
            if response.status_code == 200:
                orders = response.json()
                if isinstance(orders, list):
                    self.log_test("Get Supplier Orders", True, f"Retrieved {len(orders)} orders for supplier")
                    return orders
                else:
                    self.log_test("Get Supplier Orders", False, "Invalid orders response format")
                    return []
            else:
                self.log_test("Get Supplier Orders", False, f"Failed to get orders, status {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Get Supplier Orders", False, f"Get orders request failed: {str(e)}")
            return []
    
    def test_sample_data_validation(self):
        """Test that sample data exists as expected"""
        # Test vendor login with all demo accounts
        demo_vendors = [
            "rajesh.dosa@gmail.com",
            "sunita.chaat@gmail.com", 
            "vikram.paratha@gmail.com"
        ]
        
        demo_suppliers = [
            "delhi.agro@gmail.com",
            "mumbai.oils@gmail.com",
            "punjab.fresh@gmail.com"
        ]
        
        vendor_count = 0
        supplier_count = 0
        
        # Test vendor accounts
        for email in demo_vendors:
            try:
                response = requests.post(f"{BASE_URL}/auth/login", 
                                       json={"email": email, "password": "demo123"}, 
                                       timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("user", {}).get("userType") == "vendor":
                        vendor_count += 1
            except:
                pass
        
        # Test supplier accounts
        for email in demo_suppliers:
            try:
                response = requests.post(f"{BASE_URL}/auth/login", 
                                       json={"email": email, "password": "demo123"}, 
                                       timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("user", {}).get("userType") == "supplier":
                        supplier_count += 1
            except:
                pass
        
        # Test products
        products = self.test_get_products()
        product_count = len(products)
        
        # Test categories
        categories = self.test_get_categories()
        category_count = len(categories)
        
        success = vendor_count >= 3 and supplier_count >= 3 and product_count >= 8 and category_count >= 4
        
        self.log_test("Sample Data Validation", success, 
                     f"Found {vendor_count}/3 vendors, {supplier_count}/3 suppliers, {product_count} products, {category_count} categories")
        
        return success
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting StreetBazaar Backend API Tests")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_api_health():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        # Authentication tests
        print("\n🔐 Authentication Tests")
        print("-" * 30)
        self.test_vendor_login()
        self.test_supplier_login()
        self.test_jwt_validation()
        self.test_invalid_token()
        
        # Product management tests
        print("\n📦 Product Management Tests")
        print("-" * 30)
        self.test_get_products()
        self.test_get_categories()
        self.test_product_search()
        self.test_category_filter()
        self.test_create_product()
        self.test_vendor_create_product_forbidden()
        
        # Order management tests
        print("\n🛒 Order Management Tests")
        print("-" * 30)
        self.test_create_order()
        self.test_get_vendor_orders()
        self.test_get_supplier_orders()
        
        # Sample data validation
        print("\n📊 Sample Data Validation")
        print("-" * 30)
        self.test_sample_data_validation()
        
        # Summary
        print("\n📋 Test Summary")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # List failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = StreetBazaarTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)