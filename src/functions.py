from typing import Optional, List
from langchain_core.tools import tool
from states import State, Product

# Sample product inventory
product_inventory: List[Product] = [
    Product(name="shoes", quantity=6, price=5),
    Product(name="shirts", quantity=2, price=10),
]

@tool
def show_all_products() -> List[Product]:
    """Retrieves and displays all available products."""
    return product_inventory

@tool
def search_product(product_name: str) -> Optional[Product]:
    """Searches for a product in the inventory and returns it if found."""
    product_name = product_name.lower().rstrip("s")
    for product in product_inventory:
        if product.name.lower().rstrip("s") == product_name and product.quantity > 0:
            return product
    return None

@tool
def add_to_cart(state: State, product_name: str, quantity: int) -> str:
    """Adds a product to the shopping cart and updates inventory."""
    product_name_lower = product_name.lower()
    for inv_product in product_inventory:
        if inv_product.name.lower() == product_name_lower:
            if inv_product.quantity >= quantity:
                state.cart.append(Product(name=inv_product.name, quantity=quantity, price=inv_product.price))
                inv_product.quantity -= quantity
                return f"✅ Added {quantity} {product_name}(s) to your cart."
            else:
                return f"❌ Only {inv_product.quantity} {product_name}(s) left in stock."
    return f"❌ {product_name} is not available."

@tool
def see_cart(state: State) -> str | List[Product]:
    """Retrieves the current items in the shopping cart."""
    if not state.cart:
        return "🛒 Your cart is empty."
    return state.cart

@tool
def checkout(state: State) -> str:
    """Processes the checkout, calculates the total, and clears the cart."""
    total_price = sum(product.price * product.quantity for product in state.cart)
    state.cart = []
    return f"✅ Checkout complete! Your total is ${total_price:.2f}. Your order will arrive in 3 working days."

# Create a list and dictionary of tools
tools = [show_all_products, search_product, add_to_cart, see_cart, checkout]
toolkit = {tool.name: tool for tool in tools}