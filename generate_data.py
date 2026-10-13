"""
Retail Transaction Data Generator
Generates realistic retail basket transactions with strong affinity associations
for Market Basket Analysis & Association Rule Mining.
"""

import random
import csv
import os
from datetime import datetime, timedelta

# Categories and Items
PRODUCT_CATALOG = {
    "Bakery & Dairy": ["Whole Milk", "White Bread", "Brown Bread", "Butter", "Cheese Slices", "Yogurt", "Eggs (12pk)", "Croissants"],
    "Snacks & Beverages": ["Potato Chips", "Soda Can", "Ground Coffee", "Green Tea", "Dark Chocolate", "Cookies", "Orange Juice"],
    "Cooking & Pantry": ["Pasta", "Olive Oil", "Tomato Sauce", "Basmati Rice", "Black Pepper", "Garlic Paste", "Onions", "Tomatoes"],
    "Personal Care": ["Shampoo", "Conditioner", "Body Wash", "Toothpaste", "Toothbrush", "Face Wash", "Hand Sanitizer"],
    "Electronics & Acc": ["Wireless Mouse", "Mechanical Keyboard", "Mouse Pad", "USB-C Cable", "Laptop Stand", "HDMI Cable"]
}

# Strong affinity combinations (frequent co-purchases)
AFFINITY_RULES = [
    (["Whole Milk", "White Bread"], ["Butter"], 0.75),
    (["White Bread", "Butter"], ["Eggs (12pk)"], 0.65),
    (["Ground Coffee"], ["Cookies"], 0.70),
    (["Pasta", "Olive Oil"], ["Tomato Sauce"], 0.80),
    (["Potato Chips"], ["Soda Can"], 0.72),
    (["Wireless Mouse"], ["Mouse Pad"], 0.78),
    (["Mechanical Keyboard", "Wireless Mouse"], ["Laptop Stand"], 0.60),
    (["Shampoo"], ["Conditioner"], 0.85),
    (["Toothbrush"], ["Toothpaste"], 0.82),
    (["Dark Chocolate"], ["Green Tea"], 0.50),
    (["Basmati Rice", "Onions"], ["Tomatoes"], 0.70)
]

ALL_ITEMS = [item for sublist in PRODUCT_CATALOG.values() for item in sublist]

def generate_transactions(num_transactions=15000, output_path="data/retail_transactions.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    start_date = datetime(2025, 1, 1)
    rows = []
    
    for tx_id in range(1001, 1001 + num_transactions):
        tx_date = (start_date + timedelta(minutes=random.randint(0, 525600))).strftime("%Y-%m-%d %H:%M:%S")
        basket = set()
        
        # Decide if this transaction will trigger an affinity pattern
        for antecedents, consequents, prob in AFFINITY_RULES:
            if random.random() < 0.18:  # 18% chance to consider this pattern
                basket.update(antecedents)
                if random.random() < prob:
                    basket.update(consequents)
        
        # Add 1 to 4 random noise items
        noise_count = random.randint(1, 4)
        for _ in range(noise_count):
            basket.add(random.choice(ALL_ITEMS))
            
        # Ensure minimum basket size of 2
        while len(basket) < 2:
            basket.add(random.choice(ALL_ITEMS))
            
        # Write rows
        for item in basket:
            # Generate unit price based on category
            price = round(random.uniform(2.5, 45.0), 2)
            quantity = random.choices([1, 2, 3, 4], weights=[0.7, 0.2, 0.07, 0.03])[0]
            rows.append({
                "TransactionID": f"TXN-{tx_id}",
                "Date": tx_date,
                "Item": item,
                "Quantity": quantity,
                "UnitPrice": price,
                "TotalAmount": round(price * quantity, 2)
            })

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["TransactionID", "Date", "Item", "Quantity", "UnitPrice", "TotalAmount"])
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Generated {len(rows)} items across {num_transactions} transactions saved to {output_path}")

if __name__ == "__main__":
    generate_transactions(num_transactions=15000, output_path="data/retail_transactions.csv")
