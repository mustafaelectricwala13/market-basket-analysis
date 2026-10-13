"""
Market Basket Visualizer
Generates publication-quality charts for reports and GitHub README:
1. Top Rules by Lift (Bar Chart)
2. Support vs Confidence vs Lift (Scatter Plot)
3. Top Item Frequencies
4. Association Network Graph (NetworkX)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import networkx as nx
import pandas as pd
import numpy as np

# Use clean modern plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

def plot_item_frequency(df, output_path="reports/figures/item_frequency.png", top_n=15):
    """Plots top purchased items."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    item_counts = df['Item'].value_counts().head(top_n)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(item_counts.index[::-1], item_counts.values[::-1], color='#2563eb', edgecolor='#1d4ed8', height=0.65)
    
    ax.set_title(f"Top {top_n} Most Purchased Products (Frequency)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Number of Transactions", fontsize=11, fontweight='bold')
    ax.set_ylabel("Product Name", fontsize=11, fontweight='bold')
    
    # Add data labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 80, bar.get_y() + bar.get_height()/2, f'{int(width):,}',
                va='center', ha='left', fontsize=9, color='#1e293b', fontweight='bold')
        
    ax.set_xlim(0, max(item_counts.values) * 1.15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_top_rules_by_lift(rules_df, output_path="reports/figures/top_rules_by_lift.png", top_n=10):
    """Plots top association rules sorted by Lift."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    top_rules = rules_df.head(top_n).copy()
    
    top_rules['rule_label'] = top_rules.apply(
        lambda r: f"{r['antecedents_str']}  ->  {r['consequents_str']}", axis=1
    )
    top_rules = top_rules.iloc[::-1] # Reverse for horizontal bar chart
    
    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(top_rules['rule_label'], top_rules['lift'], color='#059669', edgecolor='#047857', height=0.6)
    
    ax.set_title(f"Top {top_n} Association Rules by Lift Ratio", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Lift Ratio (Values > 1.0 indicate strong affinity)", fontsize=11, fontweight='bold')
    ax.axvline(x=1.0, color='#dc2626', linestyle='--', linewidth=1.5, label='Baseline Independence (Lift = 1.0)')
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.05, bar.get_y() + bar.get_height()/2, f'{width:.2f}x',
                va='center', ha='left', fontsize=9.5, color='#0f172a', fontweight='bold')
        
    ax.set_xlim(0, max(top_rules['lift']) * 1.15)
    ax.legend(loc='lower right', frameon=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_lift_vs_confidence(rules_df, output_path="reports/figures/lift_vs_confidence.png"):
    """Scatter plot of Support vs Confidence colored by Lift."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        rules_df['support'] * 100,
        rules_df['confidence'] * 100,
        c=rules_df['lift'],
        cmap='viridis',
        alpha=0.75,
        s=60,
        edgecolors='none'
    )
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Lift Ratio', fontsize=11, fontweight='bold')
    
    ax.set_title("Association Rules: Support vs Confidence vs Lift", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Support (%)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Confidence (%)", fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def plot_network_graph(rules_df, output_path="reports/figures/network_graph.png", top_n=20):
    """Creates a directed network graph of high-lift association rules."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    top_rules = rules_df.head(top_n)
    
    G = nx.DiGraph()
    for _, row in top_rules.iterrows():
        antecedents = row['antecedents_str'].split(', ')
        consequents = row['consequents_str'].split(', ')
        lift = row['lift']
        
        for ant in antecedents:
            for cons in consequents:
                G.add_edge(ant, cons, weight=lift)
                
    fig, ax = plt.subplots(figsize=(12, 10))
    pos = nx.spring_layout(G, k=0.9, iterations=60, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=2400, node_color='#e0e7ff', edgecolors='#4338ca', linewidths=2, ax=ax)
    # Draw edges
    weights = [G[u][v]['weight'] for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=[w * 0.7 for w in weights], edge_color='#6366f1', alpha=0.6,
                           arrows=True, arrowsize=18, arrowstyle='-|>', ax=ax)
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=9, font_family='sans-serif', font_weight='bold', ax=ax)
    
    ax.set_title("Cross-Selling Product Affinity Network Graph", fontsize=15, fontweight='bold', pad=15)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    from engine import MarketBasketEngine
    engine = MarketBasketEngine()
    df = engine.load_data()
    rules = engine.generate_rules(min_confidence=0.25, min_lift=1.2)
    
    plot_item_frequency(df)
    plot_top_rules_by_lift(rules)
    plot_lift_vs_confidence(rules)
    plot_network_graph(rules)
