"""
Automated insights generation module.
Identifies patterns, anomalies, trends, and key findings in the data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta


class InsightGenerator:
    """Generate automated insights from data."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize insight generator with DataFrame.
        
        Args:
            df: pandas DataFrame to analyze
        """
        self.df = df
        self.insights = []
    
    def generate_all_insights(self) -> List[str]:
        """
        Generate all available insights.
        
        Returns:
            List of insight strings
        """
        self.insights = []
        
        # Generate different types of insights
        self.insights.extend(self._get_top_bottom_insights())
        self.insights.extend(self._get_trend_insights())
        self.insights.extend(self._get_missing_data_insights())
        self.insights.extend(self._get_outlier_insights())
        self.insights.extend(self._get_correlation_insights())
        self.insights.extend(self._get_distribution_insights())
        
        return self.insights
    
    def _get_top_bottom_insights(self, n: int = 5) -> List[str]:
        """
        Identify top and bottom performers across numerical columns.
        
        Args:
            n: Number of top/bottom items to identify
            
        Returns:
            List of insights
        """
        insights = []
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols:
            if self.df[col].isna().all():
                continue
            
            # Top performers
            top_value = self.df[col].max()
            top_count = (self.df[col] == top_value).sum()
            
            if pd.notna(top_value):
                insights.append(
                    f"**Highest {col}**: {top_value:,.2f} "
                    f"({top_count} record{'s' if top_count > 1 else ''})"
                )
            
            # Bottom performers
            bottom_value = self.df[col].min()
            bottom_count = (self.df[col] == bottom_value).sum()
            
            if pd.notna(bottom_value):
                insights.append(
                    f"**Lowest {col}**: {bottom_value:,.2f} "
                    f"({bottom_count} record{'s' if bottom_count > 1 else ''})"
                )
            
            # Average value
            avg_value = self.df[col].mean()
            if pd.notna(avg_value):
                insights.append(
                    f"**Average {col}**: {avg_value:,.2f}"
                )
        
        return insights[:6]  # Limit to top 6 insights
    
    def _get_trend_insights(self) -> List[str]:
        """
        Identify trends in time series data.
        
        Returns:
            List of insights
        """
        insights = []
        
        # Find date columns
        date_cols = self.df.select_dtypes(include=['datetime64']).columns
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(date_cols) == 0 or len(numerical_cols) == 0:
            return insights
        
        date_col = date_cols[0]  # Use first date column
        
        for num_col in numerical_cols[:2]:  # Analyze first 2 numerical columns
            try:
                # Sort by date
                sorted_df = self.df.sort_values(date_col)
                
                # Calculate trend
                sorted_df = sorted_df.dropna(subset=[date_col, num_col])
                if len(sorted_df) < 2:
                    continue
                
                # Compare first and last periods
                first_quarter = sorted_df.head(len(sorted_df) // 4)
                last_quarter = sorted_df.tail(len(sorted_df) // 4)
                
                first_avg = first_quarter[num_col].mean()
                last_avg = last_quarter[num_col].mean()
                
                if pd.notna(first_avg) and pd.notna(last_avg) and first_avg != 0:
                    pct_change = ((last_avg - first_avg) / abs(first_avg)) * 100
                    
                    if abs(pct_change) > 5:  # Only report significant changes
                        direction = "increased" if pct_change > 0 else "decreased"
                        insights.append(
                            f"**Trend**: {num_col} has {direction} by "
                            f"{abs(pct_change):.1f}% over the time period"
                        )
                
                # Find best and worst periods
                grouped = sorted_df.groupby(sorted_df[date_col].dt.to_period('M'))[num_col].sum()
                if len(grouped) > 0:
                    best_period = grouped.idxmax()
                    worst_period = grouped.idxmin()
                    
                    insights.append(
                        f"**Best Period for {num_col}**: {best_period} "
                        f"({grouped[best_period]:,.2f})"
                    )
                    insights.append(
                        f"**Lowest Period for {num_col}**: {worst_period} "
                        f"({grouped[worst_period]:,.2f})"
                    )
                
            except Exception:
                continue
        
        return insights[:4]  # Limit insights
    
    def _get_missing_data_insights(self) -> List[str]:
        """
        Identify columns with significant missing data.
        
        Returns:
            List of insights
        """
        insights = []
        
        missing_pct = (self.df.isna().sum() / len(self.df) * 100).sort_values(ascending=False)
        
        # Report columns with >10% missing data
        significant_missing = missing_pct[missing_pct > 10].head(3)
        
        for col, pct in significant_missing.items():
            insights.append(
                f"**Data Quality**: {col} has {pct:.1f}% missing values "
                f"({self.df[col].isna().sum():,} records)"
            )
        
        # Report if data is mostly complete
        if missing_pct.max() < 5:
            insights.append(
                f"**Data Quality**: Dataset is {100 - missing_pct.mean():.1f}% complete"
            )
        
        return insights
    
    def _get_outlier_insights(self) -> List[str]:
        """
        Identify potential outliers in numerical columns.
        
        Returns:
            List of insights
        """
        insights = []
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols[:2]:  # Check first 2 numerical columns
            try:
                # Calculate IQR
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                # Define outlier bounds
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Count outliers
                outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
                outlier_count = len(outliers)
                
                if outlier_count > 0:
                    outlier_pct = (outlier_count / len(self.df)) * 100
                    insights.append(
                        f"**Outliers Detected**: {col} has {outlier_count} potential outliers "
                        f"({outlier_pct:.1f}% of data)"
                    )
            except Exception:
                continue
        
        return insights[:2]
    
    def _get_correlation_insights(self) -> List[str]:
        """
        Identify strong correlations between numerical variables.
        
        Returns:
            List of insights
        """
        insights = []
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return insights
        
        try:
            # Calculate correlation matrix
            corr_matrix = self.df[numerical_cols].corr()
            
            # Find strong correlations (excluding diagonal)
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:  # Strong correlation threshold
                        strong_corr.append((
                            corr_matrix.columns[i],
                            corr_matrix.columns[j],
                            corr_val
                        ))
            
            # Sort by absolute correlation
            strong_corr.sort(key=lambda x: abs(x[2]), reverse=True)
            
            # Report top correlations
            for col1, col2, corr_val in strong_corr[:2]:
                relationship = "positively" if corr_val > 0 else "negatively"
                insights.append(
                    f"**Strong Correlation**: {col1} and {col2} are strongly "
                    f"{relationship} correlated (r={corr_val:.2f})"
                )
        except Exception:
            pass
        
        return insights
    
    def _get_distribution_insights(self) -> List[str]:
        """
        Analyze distributions of numerical columns.
        
        Returns:
            List of insights
        """
        insights = []
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols[:2]:  # Analyze first 2 columns
            try:
                # Check for skewness
                skewness = self.df[col].skew()
                
                if abs(skewness) > 1:
                    direction = "right" if skewness > 0 else "left"
                    insights.append(
                        f"**Distribution**: {col} is highly skewed to the {direction} "
                        f"(skewness: {skewness:.2f})"
                    )
                
                # Check coefficient of variation
                mean_val = self.df[col].mean()
                std_val = self.df[col].std()
                
                if mean_val != 0 and pd.notna(mean_val) and pd.notna(std_val):
                    cv = (std_val / abs(mean_val)) * 100
                    
                    if cv > 100:
                        insights.append(
                            f"**Variability**: {col} shows high variability "
                            f"(CV: {cv:.1f}%)"
                        )
            except Exception:
                continue
        
        return insights[:2]
    
    def get_categorical_insights(self, top_n: int = 3) -> List[str]:
        """
        Generate insights about categorical variables.
        
        Args:
            top_n: Number of top categories to report
            
        Returns:
            List of insights
        """
        insights = []
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols[:2]:  # Analyze first 2 categorical columns
            try:
                value_counts = self.df[col].value_counts()
                
                if len(value_counts) > 0:
                    # Report most common category
                    top_category = value_counts.index[0]
                    top_count = value_counts.iloc[0]
                    top_pct = (top_count / len(self.df)) * 100
                    
                    insights.append(
                        f"**Most Common {col}**: '{top_category}' "
                        f"({top_count:,} records, {top_pct:.1f}%)"
                    )
                
                # Report diversity
                unique_count = self.df[col].nunique()
                insights.append(
                    f"**Diversity in {col}**: {unique_count} unique values"
                )
                
            except Exception:
                continue
        
        return insights[:4]
    
    def format_insights(self) -> str:
        """
        Format all insights into organized tables with executive summary.
        
        Returns:
            Formatted insights text with tables and summary
        """
        if not self.insights:
            self.generate_all_insights()
        
        if not self.insights:
            return "No significant insights found in the data."
        
        # Add categorical insights
        self.insights.extend(self.get_categorical_insights())
        
        # Organize insights by category
        top_bottom = []
        trends = []
        anomalies = []
        
        for insight in self.insights:
            clean = insight.replace('**', '')  # Remove markdown bold
            
            if 'Highest' in clean or 'Lowest' in clean:
                if 'Period' not in clean and 'Month' not in clean:
                    top_bottom.append(clean)
                else:
                    trends.append(clean)
            elif 'Average' in clean:
                top_bottom.append(clean)
            elif 'Trend' in clean or 'increased' in clean or 'decreased' in clean or 'Best Period' in clean or 'Lowest Period' in clean:
                trends.append(clean)
            elif 'Outliers' in clean or 'Data Quality' in clean or 'missing' in clean or 'skewed' in clean or 'Variability' in clean:
                anomalies.append(clean)
        
        formatted = "## Automated Insights\n\n"
        
        # Generate executive summary
        summary = self._generate_executive_summary(top_bottom, trends, anomalies)
        formatted += f"**Executive Summary**\n\n{summary}\n\n---\n\n"
        
        # Section 1: Top/Bottom Performers
        if top_bottom:
            formatted += "### 1. Top/Bottom Performers\n\n"
            formatted += "| Metric | Best | Worst |\n"
            formatted += "|:-------|:-----|:------|\n"
            
            # Group by metric
            metrics = {}
            for item in top_bottom:
                if 'Highest' in item:
                    parts = item.split('Highest')
                    if len(parts) > 1:
                        metric_and_rest = parts[1].split(':', 1)  # Split only on first colon
                        if len(metric_and_rest) > 1:
                            metric = metric_and_rest[0].strip()
                            value = metric_and_rest[1].strip()
                            # Extract just the number (remove everything in parentheses)
                            if '(' in value:
                                value = value.split('(')[0].strip()
                            if metric not in metrics:
                                metrics[metric] = {'best': '', 'worst': ''}
                            metrics[metric]['best'] = value
                elif 'Lowest' in item:
                    parts = item.split('Lowest')
                    if len(parts) > 1:
                        metric_and_rest = parts[1].split(':', 1)  # Split only on first colon
                        if len(metric_and_rest) > 1:
                            metric = metric_and_rest[0].strip()
                            value = metric_and_rest[1].strip()
                            # Extract just the number (remove everything in parentheses)
                            if '(' in value:
                                value = value.split('(')[0].strip()
                            if metric not in metrics:
                                metrics[metric] = {'best': '', 'worst': ''}
                            metrics[metric]['worst'] = value
            
            for metric, values in metrics.items():
                best_val = values.get('best', 'N/A')
                worst_val = values.get('worst', 'N/A')
                formatted += f"| {metric} | {best_val} | {worst_val} |\n"
            
            formatted += "\n"
        
        # Section 2: Trends & Patterns
        if trends:
            formatted += "### 2. Trends & Patterns\n\n"
            formatted += "| Insight | Value |\n"
            formatted += "|:--------|:------|\n"
            
            for item in trends:
                if 'Average' in item:
                    parts = item.split(':')
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        formatted += f"| {key} | {value} |\n"
                elif 'Best Period' in item or 'Lowest Period' in item:
                    parts = item.split(':')
                    if len(parts) >= 2:
                        key = parts[0].strip().replace('Best Period for', 'Best Month').replace('Lowest Period for', 'Worst Month')
                        value = parts[1].strip()
                        # Simplify the value
                        if '(' in value and ')' in value:
                            month = value.split('(')[0].strip()
                            amount = value.split('(')[1].split(')')[0]
                            # Shorten large numbers
                            try:
                                num = float(amount.replace(',', ''))
                                if num >= 1000000:
                                    amount = f"{num/1000000:.1f}M"
                                elif num >= 1000:
                                    amount = f"{num/1000:.0f}k"
                            except:
                                pass
                            value = f"{month} ({amount})"
                        formatted += f"| {key} | {value} |\n"
                elif 'Trend' in item:
                    if 'has' in item:
                        parts = item.split('has')
                        if len(parts) >= 2:
                            metric = parts[0].replace('Trend:', '').strip()
                            trend = parts[1].strip()
                            # Add arrow
                            if 'increased' in trend:
                                trend = '↑ ' + trend.replace('increased by', '').strip()
                            elif 'decreased' in trend:
                                trend = '↓ ' + trend.replace('decreased by', '').strip()
                            formatted += f"| {metric} Trend | {trend} |\n"
            
            formatted += "\n"
        
        # Section 3: Anomalies & Data Quality
        if anomalies:
            formatted += "### 3. Anomalies & Data Quality\n\n"
            formatted += "| Issue | Details |\n"
            formatted += "|:------|:--------|\n"
            
            has_content = False
            for item in anomalies:
                if 'Data Quality' in item and 'missing' in item:
                    # Extract column name and complete details
                    if ':' in item:
                        parts = item.split(':', 1)
                        if len(parts) >= 2:
                            rest = parts[1]
                            if 'has' in rest:
                                column = rest.split('has')[0].strip()
                                details_full = 'has' + rest.split('has', 1)[1] if len(rest.split('has', 1)) > 1 else rest
                                # Clean up the details - just get percentage and count
                                formatted += f"| Missing {column} | {details_full} |\n"
                                has_content = True
                elif 'Outliers Detected' in item:
                    if ':' in item:
                        parts = item.split(':', 1)
                        if len(parts) >= 2:
                            column = parts[0].replace('Outliers Detected', '').strip()
                            details = parts[1].strip()
                            # Make sure we get complete details
                            formatted += f"| {column} Outliers | {details} |\n"
                            has_content = True
                elif 'Variability' in item:
                    if ':' in item:
                        parts = item.split(':', 1)
                        if len(parts) >= 2:
                            column = parts[0].replace('Variability', '').strip()
                            details = parts[1].strip()
                            # Complete variability info
                            formatted += f"| {column} Variability | {details} |\n"
                            has_content = True
                elif 'Distribution' in item and 'skewed' in item:
                    if ':' in item:
                        parts = item.split(':', 1)
                        if len(parts) >= 2:
                            column = parts[0].replace('Distribution', '').strip()
                            details = parts[1].strip()
                            # Complete skewness information
                            formatted += f"| Skewed Distribution | {column} - {details} |\n"
                            has_content = True
            
            # If no anomalies were added, show a message
            if not has_content:
                formatted += "| Data Quality | No significant data quality issues detected |\n"
            
            formatted += "\n"
        else:
            # If no anomalies at all, still show the section with good news
            formatted += "### 3. Anomalies & Data Quality\n\n"
            formatted += "| Issue | Details |\n"
            formatted += "|:------|:--------|\n"
            formatted += "| Data Quality | No significant data quality issues detected |\n\n"
        
        return formatted
    
    def _generate_executive_summary(self, top_bottom: List[str], trends: List[str], anomalies: List[str]) -> str:
        """
        Generate a straightforward executive summary based on actual data findings.
        
        Args:
            top_bottom: List of top/bottom performer insights
            trends: List of trend insights
            anomalies: List of anomaly insights
            
        Returns:
            Concise summary of key findings
        """
        summary_points = []
        
        # Extract actual numbers and metrics from insights
        num_records = len(self.df) if self.df is not None else 0
        num_cols = len(self.df.columns) if self.df is not None else 0
        
        summary_points.append(f"This dataset contains **{num_records:,} records** across **{num_cols} columns**.")
        
        # Key value ranges
        ranges_found = []
        for item in top_bottom:
            if 'Highest' in item and 'Average' not in item:
                try:
                    metric = item.split('Highest')[1].split(':')[0].strip()
                    high_val = item.split(':')[1].split('(')[0].strip()
                    # Find corresponding lowest
                    for item2 in top_bottom:
                        if f'Lowest {metric}' in item2:
                            low_val = item2.split(':')[1].split('(')[0].strip()
                            ranges_found.append(f"**{metric}** ranges from {low_val} to {high_val}")
                            break
                except:
                    pass
        
        if ranges_found:
            summary_points.append(". ".join(ranges_found) + ".")
        
        # Trends if present
        for item in trends:
            if 'increased' in item or 'decreased' in item:
                try:
                    if 'decreased' in item:
                        metric = item.split('has')[0].replace('Trend:', '').strip()
                        pct = item.split('by')[1].split('%')[0].strip()
                        summary_points.append(f"**{metric}** shows a declining trend of **{pct}%** over the period.")
                    elif 'increased' in item:
                        metric = item.split('has')[0].replace('Trend:', '').strip()
                        pct = item.split('by')[1].split('%')[0].strip()
                        summary_points.append(f"**{metric}** shows an increasing trend of **{pct}%** over the period.")
                except:
                    pass
        
        # Time periods if present
        best_period = None
        worst_period = None
        for item in trends:
            if 'Best Period' in item:
                try:
                    period = item.split(':')[1].split('(')[0].strip()
                    best_period = period
                except:
                    pass
            if 'Lowest Period' in item or 'Worst Period' in item:
                try:
                    period = item.split(':')[1].split('(')[0].strip()
                    worst_period = period
                except:
                    pass
        
        if best_period and worst_period:
            summary_points.append(f"Peak performance occurred in **{best_period}**, while **{worst_period}** showed the weakest results.")
        elif best_period:
            summary_points.append(f"Peak performance occurred in **{best_period}**.")
        
        # Data quality issues
        quality_issues = []
        for item in anomalies:
            if 'missing' in item.lower() and '%' in item:
                try:
                    pct_str = item.split('%')[0].split()[-1]
                    pct = float(pct_str)
                    if pct > 20:
                        if 'CustomerID' in item or 'Customer' in item:
                            field = 'customer data'
                        else:
                            field = item.split(':')[1].split('has')[0].strip() if ':' in item else 'some fields'
                        quality_issues.append(f"**{pct:.1f}%** missing values in {field}")
                except:
                    pass
            
            if 'Outliers' in item:
                try:
                    if '%' in item:
                        pct_str = item.split('%')[0].split('(')[-1].strip()
                        pct = float(pct_str)
                        if pct > 5:
                            quality_issues.append(f"**{pct:.1f}%** potential outliers detected")
                            break  # Only mention once
                except:
                    pass
        
        if quality_issues:
            summary_points.append(f"Data quality concerns: {', '.join(quality_issues[:2])}.")
        else:
            summary_points.append("**Data quality is good** with no significant issues detected.")
        
        # Join with line breaks for better readability
        return "\n\n".join(summary_points)