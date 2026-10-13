"""
Market Basket Analysis & Recommendation Engine
Standalone, High-Performance Association Rule Mining Engine using Apriori algorithm.
Computes Support, Confidence, Lift, and generates cross-sell recommendations.
"""

import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
import os

class MarketBasketEngine:
    def __init__(self, data_path="data/retail_transactions.csv"):
        self.data_path = data_path
        self.df = None
        self.transactions = []
        self.num_transactions = 0
        self.frequent_itemsets = None
        self.rules = None

    def load_data(self):
        """Loads and pre-processes retail transactions."""
        self.df = pd.read_csv(self.data_path)
        # Group into list of itemsets per transaction
        grouped = self.df.groupby('TransactionID')['Item'].apply(lambda x: sorted(list(set(x))))
        self.transactions = grouped.tolist()
        self.num_transactions = len(self.transactions)
        return self.df

    def run_apriori(self, min_support=0.03, max_len=3):
        """
        Custom Apriori implementation for frequent itemset generation.
        """
        if not self.transactions:
            self.load_data()

        min_count = min_support * self.num_transactions
        item_counts = defaultdict(int)

        # 1-itemsets
        for txn in self.transactions:
            for item in txn:
                item_counts[frozenset([item])] += 1

        current_frequent = {
            itemset: count for itemset, count in item_counts.items() if count >= min_count
        }

        all_frequent = dict(current_frequent)
        k = 2

        while current_frequent and k <= max_len:
            # Generate candidate k-itemsets from (k-1)-itemsets
            prev_items = list(current_frequent.keys())
            candidates = set()
            for i in range(len(prev_items)):
                for j in range(i + 1, len(prev_items)):
                    union_set = prev_items[i] | prev_items[j]
                    if len(union_set) == k:
                        candidates.add(union_set)

            # Count candidates across transactions
            candidate_counts = defaultdict(int)
            for txn in self.transactions:
                txn_set = set(txn)
                for cand in candidates:
                    if cand.issubset(txn_set):
                        candidate_counts[cand] += 1

            # Filter by min_count
            current_frequent = {
                itemset: count for itemset, count in candidate_counts.items() if count >= min_count
            }
            all_frequent.update(current_frequent)
            k += 1

        # Build frequent itemsets DataFrame
        data = []
        for itemset, count in all_frequent.items():
            support = count / self.num_transactions
            data.append({
                "itemsets": itemset,
                "items_list": sorted(list(itemset)),
                "items_str": ", ".join(sorted(list(itemset))),
                "length": len(itemset),
                "count": count,
                "support": round(support, 4)
            })

        self.frequent_itemsets = pd.DataFrame(data).sort_values(by="support", ascending=False).reset_index(drop=True)
        return self.frequent_itemsets

    def generate_rules(self, min_confidence=0.20, min_lift=1.1):
        """
        Derives association rules from frequent itemsets with:
        - Support(A -> B) = P(A & B)
        - Confidence(A -> B) = P(B | A) = Support(A & B) / Support(A)
        - Lift(A -> B) = Confidence(A -> B) / Support(B)
        """
        if self.frequent_itemsets is None:
            self.run_apriori()

        itemset_support = dict(zip(self.frequent_itemsets['itemsets'], self.frequent_itemsets['support']))
        rules_list = []

        # Find rules for itemsets with length >= 2
        multi_items = self.frequent_itemsets[self.frequent_itemsets['length'] >= 2]

        for _, row in multi_items.iterrows():
            itemset = row['itemsets']
            itemset_sup = row['support']
            items = list(itemset)

            # Generate all non-empty antecedent combinations
            for i in range(1, len(items)):
                for ante in combinations(items, i):
                    antecedent = frozenset(ante)
                    consequent = itemset - antecedent

                    ante_sup = itemset_support.get(antecedent)
                    cons_sup = itemset_support.get(consequent)

                    if ante_sup and cons_sup:
                        confidence = itemset_sup / ante_sup
                        lift = confidence / cons_sup

                        if confidence >= min_confidence and lift >= min_lift:
                            rules_list.append({
                                "antecedents": antecedent,
                                "consequents": consequent,
                                "antecedents_str": ", ".join(sorted(list(antecedent))),
                                "consequents_str": ", ".join(sorted(list(consequent))),
                                "support": round(itemset_sup, 4),
                                "confidence": round(confidence, 4),
                                "lift": round(lift, 3),
                                "leverage": round(itemset_sup - (ante_sup * cons_sup), 4)
                            })

        if not rules_list:
            self.rules = pd.DataFrame(columns=["antecedents_str", "consequents_str", "support", "confidence", "lift", "leverage"])
        else:
            self.rules = pd.DataFrame(rules_list).sort_values(by="lift", ascending=False).reset_index(drop=True)

        return self.rules

    def get_recommendations(self, item_name, top_n=5):
        """
        Recommends products given a selected item based on highest lift and confidence.
        """
        if self.rules is None:
            self.generate_rules()

        matched = self.rules[
            self.rules['antecedents'].apply(lambda x: item_name in x)
        ]

        if matched.empty:
            return pd.DataFrame(columns=["Recommended Item", "Confidence (%)", "Lift", "Support (%)", "Rule"])

        results = []
        for _, row in matched.iterrows():
            for rec_item in row['consequents']:
                if rec_item != item_name:
                    results.append({
                        "Recommended Item": rec_item,
                        "Confidence (%)": round(row['confidence'] * 100, 1),
                        "Lift": row['lift'],
                        "Support (%)": round(row['support'] * 100, 2),
                        "Rule": f"{row['antecedents_str']}  ->  {row['consequents_str']}"
                    })

        res_df = pd.DataFrame(results).drop_duplicates(subset=["Recommended Item"])
        return res_df.sort_values(by="Lift", ascending=False).head(top_n).reset_index(drop=True)

    def get_summary_stats(self):
        """Computes summary statistics for executive dashboards."""
        if self.df is None:
            self.load_data()
        if self.rules is None:
            self.generate_rules()

        total_tx = self.df['TransactionID'].nunique()
        total_items = self.df['Item'].nunique()
        total_revenue = self.df['TotalAmount'].sum()
        avg_basket_value = self.df.groupby('TransactionID')['TotalAmount'].sum().mean()
        high_lift_rules = len(self.rules[self.rules['lift'] >= 1.5]) if self.rules is not None else 0

        return {
            "total_transactions": total_tx,
            "unique_items": total_items,
            "total_revenue": round(total_revenue, 2),
            "avg_basket_value": round(avg_basket_value, 2),
            "total_rules": len(self.rules) if self.rules is not None else 0,
            "high_lift_rules": high_lift_rules
        }

if __name__ == "__main__":
    engine = MarketBasketEngine()
    print("Loading data...")
    engine.load_data()
    print("Running Apriori algorithm...")
    frequent = engine.run_apriori(min_support=0.03)
    print(f"Discovered {len(frequent)} frequent itemsets.")
    
    print("Mining Association Rules (min_lift=1.2)...")
    rules = engine.generate_rules(min_confidence=0.25, min_lift=1.2)
    print(f"Generated {len(rules)} association rules.")
    print("\nTop 5 Rules by Lift:")
    print(rules[['antecedents_str', 'consequents_str', 'support', 'confidence', 'lift']].head())
    
    test_item = "Whole Milk"
    recs = engine.get_recommendations(test_item)
    print(f"\nTop Recommendations for '{test_item}':")
    print(recs)
