#!/usr/bin/env python3
"""
Metrics Calculator - Calculate ad performance metrics and revenue impact

Computes:
- ROAS (Return on Ad Spend)
- Revenue Impact with ad spend consideration
- Wasted ad spend on sold-out products
- Performance scores for ranking
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate comprehensive ad performance metrics"""

    def __init__(self, csv_path: str = "URLS_enhanced.csv"):
        """Initialize with product data"""
        self.csv_path = csv_path
        self.df = None
        self.load_data()

    def load_data(self):
        """Load product data from CSV"""
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} products from {self.csv_path}")
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            self.df = pd.DataFrame()

    def calculate_roas(self, revenue: float, ad_spend: float) -> float:
        """
        Calculate Return on Ad Spend

        Args:
            revenue: Revenue generated
            ad_spend: Amount spent on ads

        Returns:
            ROAS ratio (revenue / ad_spend)
        """
        if ad_spend <= 0:
            return 0.0
        return round(revenue / ad_spend, 2)

    def calculate_revenue_impact(
        self,
        days_out: int,
        price: float,
        conversion_rate: float,
        ad_spend: float
    ) -> Dict[str, float]:
        """
        Calculate comprehensive revenue impact with ad spend consideration

        Args:
            days_out: Number of days product was out of stock
            price: Product price in PKR
            conversion_rate: Conversion rate (0.0-1.0)
            ad_spend: Ad spend during stockout period

        Returns:
            Dictionary with all metrics
        """
        # Calculate lost revenue
        lost_revenue = days_out * price * conversion_rate

        # Net impact (revenue - ad spend)
        net_impact = lost_revenue - ad_spend

        # ROAS calculation
        roas = self.calculate_roas(lost_revenue, ad_spend) if ad_spend > 0 else 0.0

        # Wasted ad spend percentage
        wasted_percentage = (ad_spend / (ad_spend + lost_revenue) * 100) if (ad_spend + lost_revenue) > 0 else 0.0

        return {
            'lost_revenue': round(lost_revenue, 2),
            'wasted_ad_spend': round(ad_spend, 2),
            'net_impact': round(net_impact, 2),
            'roas': round(roas, 2),
            'wasted_percentage': round(wasted_percentage, 2)
        }

    def calculate_product_score(
        self,
        total_stockout_days: int,
        price: float,
        ad_spend_daily: float,
        sales_count: int,
        conversion_rate: float
    ) -> float:
        """
        Calculate overall product performance score

        Factors:
        - Stockout frequency (negative weight)
        - Sales volume (positive weight)
        - Ad spend efficiency (positive weight)

        Returns:
            Score from 0-100 (higher is better)
        """
        score = 50.0  # Base score

        # Penalty for stockouts (max -30 points)
        stockout_penalty = min(total_stockout_days * 0.5, 30)
        score -= stockout_penalty

        # Bonus for sales (max +30 points)
        sales_bonus = min(sales_count * 0.5, 30)
        score += sales_bonus

        # Bonus for high price items (max +10 points)
        price_bonus = min((price / 100) * 2, 10)
        score += price_bonus

        # Bonus for good conversion rate (max +10 points)
        if conversion_rate > 0.03:  # > 3%
            conversion_bonus = 10
        elif conversion_rate > 0.02:  # > 2%
            conversion_bonus = 5
        else:
            conversion_bonus = 0
        score += conversion_bonus

        return round(max(0, min(100, score)), 1)

    def get_top_products(
        self,
        metric: str = 'sales_count',
        n: int = 10
    ) -> pd.DataFrame:
        """
        Get top N products by specified metric

        Args:
            metric: Column to sort by
            n: Number of products to return

        Returns:
            DataFrame of top products
        """
        if self.df.empty:
            return pd.DataFrame()

        df_sorted = self.df.sort_values(by=metric, ascending=False)
        return df_sorted.head(n)[['Ad Name', metric, 'Product_Price', 'Category']].copy()

    def get_worst_products(
        self,
        metric: str = 'total_stockout_days',
        n: int = 10
    ) -> pd.DataFrame:
        """
        Get worst N products by specified metric

        Args:
            metric: Column to sort by
            n: Number of products to return

        Returns:
            DataFrame of worst products
        """
        if self.df.empty:
            return pd.DataFrame()

        # For worst products, we want:
        # - Highest stockout days
        # - Lowest sales
        # - Lowest revenue

        df_sorted = self.df.sort_values(by=metric, ascending=True)

        # If metric is stockout_days, sort descending
        if metric == 'total_stockout_days':
            df_sorted = self.df.sort_values(by=metric, ascending=False)

        return df_sorted.head(n)[['Ad Name', metric, 'Product_Price', 'Category']].copy()

    def generate_performance_summary(self) -> Dict:
        """
        Generate comprehensive performance summary

        Returns:
            Dictionary with all key metrics
        """
        if self.df.empty:
            return {}

        # Calculate totals
        total_ad_spend = self.df['ad_spend_actual'].sum()
        total_sales = self.df['sales_count'].sum()
        total_revenue = (self.df['Product_Price'] * self.df['sales_count']).sum()
        total_stockout_days = self.df['total_stockout_days'].sum()

        # Calculate overall ROAS
        overall_roas = self.calculate_roas(total_revenue, total_ad_spend)

        # Find top and worst products
        top_by_sales = self.get_top_products('sales_count', 5)
        worst_by_stockout = self.get_worst_products('total_stockout_days', 5)

        return {
            'total_ad_spend': round(total_ad_spend, 2),
            'total_sales': int(total_sales),
            'total_revenue': round(total_revenue, 2),
            'total_stockout_days': int(total_stockout_days),
            'overall_roas': round(overall_roas, 2),
            'top_products_by_sales': top_by_sales.to_dict('records'),
            'worst_products_by_stockout': worst_by_stockout.to_dict('records'),
            'product_count': len(self.df)
        }

    def generate_heatmap_data(
        self,
        metric: str = 'ad_spend_actual',
        period: str = 'daily'
    ) -> pd.DataFrame:
        """
        Generate data for heatmap visualization

        Args:
            metric: Metric to visualize
            period: Time period (not implemented, using current data)

        Returns:
            DataFrame formatted for heatmap
        """
        if self.df.empty:
            return pd.DataFrame()

        # Create heatmap data
        heatmap_data = self.df[['Ad Name', metric]].copy()

        # Normalize values to 0-100 scale for color coding
        max_val = heatmap_data[metric].max()
        min_val = heatmap_data[metric].min()
        val_range = max_val - min_val if max_val != min_val else 1

        heatmap_data['normalized'] = ((heatmap_data[metric] - min_val) / val_range * 100).round(1)

        # Assign color categories based on normalized values
        conditions = [
            heatmap_data['normalized'] <= 20,
            (heatmap_data['normalized'] > 20) & (heatmap_data['normalized'] <= 40),
            (heatmap_data['normalized'] > 40) & (heatmap_data['normalized'] <= 60),
            (heatmap_data['normalized'] > 60) & (heatmap_data['normalized'] <= 80),
            heatmap_data['normalized'] > 80
        ]
        labels = ['Low', 'Below Average', 'Average', 'Above Average', 'High']
        heatmap_data['color_category'] = np.select(conditions, labels, default='Average')

        return heatmap_data

    def calculate_priority_score(
        self,
        days_out: int,
        wasted_ad_spend: float,
        revenue_impact: float
    ) -> float:
        """
        Calculate priority score for action items

        Higher score = more urgent attention needed

        Args:
            days_out: Days out of stock
            wasted_ad_spend: Money wasted on ads
            revenue_impact: Revenue lost

        Returns:
            Priority score (0-100+)
        """
        # Weighted score
        score = (
            (days_out * 2.0) +           # Stockout duration (weight: 2)
            (wasted_ad_spend / 100 * 1.5) +  # Ad waste (weight: 1.5)
            (revenue_impact / 1000 * 1.0)  # Revenue impact (weight: 1.0)
        )

        return round(score, 2)


def test_metrics_calculator():
    """Test the metrics calculator"""
    print("Testing Metrics Calculator...")

    calc = MetricsCalculator()

    # Test data load
    print(f"Products loaded: {len(calc.df)}")

    # Test ROAS calculation
    roas = calc.calculate_roas(1000, 200)
    print(f"ROAS (1000 revenue / 200 spend): {roas}")

    # Test revenue impact
    impact = calc.calculate_revenue_impact(
        days_out=5,
        price=495.0,
        conversion_rate=0.02,
        ad_spend=250.0
    )
    print(f"Revenue impact: {impact}")

    # Test performance summary
    summary = calc.generate_performance_summary()
    print(f"\nPerformance Summary:")
    print(f"  Total Ad Spend: PKR {summary.get('total_ad_spend', 0):,.2f}")
    print(f"  Total Sales: {summary.get('total_sales', 0)}")
    print(f"  Total Revenue: PKR {summary.get('total_revenue', 0):,.2f}")
    print(f"  Overall ROAS: {summary.get('overall_roas', 0)}")

    print("\n[OK] Metrics Calculator test completed")


if __name__ == "__main__":
    test_metrics_calculator()
