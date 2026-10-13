"""
Export Analysis Deliverables
Exports frequent itemsets, association rules, and cross-sell recommendations
into CSV and JSON formats for stakeholder review.
"""

import json
import os
import pandas as pd
from src.engine import MarketBasketEngine

def export_all():
    os.makedirs("reports", exist_ok=True)
    engine = MarketBasketEngine()
    print("Loading retail dataset...")
    df = engine.load_data()
    
    print("Mining frequent itemsets...")
    itemsets = engine.run_apriori(min_support=0.03)
    itemsets_export = itemsets[['items_str', 'length', 'count', 'support']].copy()
    itemsets_export.to_csv("reports/frequent_itemsets.csv", index=False)
    print(f"Exported {len(itemsets_export)} frequent itemsets to reports/frequent_itemsets.csv")
    
    print("Generating association rules...")
    rules = engine.generate_rules(min_confidence=0.25, min_lift=1.2)
    rules_export = rules[['antecedents_str', 'consequents_str', 'support', 'confidence', 'lift', 'leverage']].copy()
    rules_export.to_csv("reports/association_rules.csv", index=False)
    print(f"Exported {len(rules_export)} association rules to reports/association_rules.csv")
    
    # Generate top cross-sell recommendations for all unique items
    all_items = sorted(df['Item'].unique())
    cross_sell_list = []
    for item in all_items:
        recs = engine.get_recommendations(item, top_n=3)
        for _, r in recs.iterrows():
            cross_sell_list.append({
                "Primary Item": item,
                "Recommended Add-On": r['Recommended Item'],
                "Confidence (%)": r['Confidence (%)'],
                "Lift": r['Lift'],
                "Support (%)": r['Support (%)'],
                "Strategy": f"Display '{r['Recommended Item']}' when customer adds '{item}' to cart"
            })
            
    cross_sells_df = pd.DataFrame(cross_sell_list)
    cross_sells_df.to_csv("reports/top_cross_sells.csv", index=False)
    print(f"Exported {len(cross_sells_df)} cross-sell strategies to reports/top_cross_sells.csv")
    
    # Summary JSON
    stats = engine.get_summary_stats()
    with open("reports/summary_metrics.json", "w") as f:
        json.dump(stats, f, indent=2)
    print("Exported summary metrics to reports/summary_metrics.json")

if __name__ == "__main__":
    export_all()
