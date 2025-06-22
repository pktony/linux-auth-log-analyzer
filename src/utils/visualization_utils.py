"""
Visualization utilities for creating charts and graphs
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from typing import Optional, List, Dict, Any
from collections import Counter


class ChartRenderer:
    """Handles chart rendering operations"""
    
    @staticmethod
    def save_chart(save_path: Optional[str], filename: str, dpi: int = 150) -> None:
        """Save chart to file if save_path is provided"""
        if save_path:
            plt.savefig(f"{save_path}_{filename}.png", dpi=dpi, bbox_inches='tight')
    
    @staticmethod
    def show_chart() -> None:
        """Display the current chart"""
        plt.show()


class BarChartRenderer(ChartRenderer):
    """Renders bar charts"""
    
    @staticmethod
    def render_vertical_bar(data: Dict[str, int], title: str, xlabel: str, ylabel: str, 
                           save_path: Optional[str] = None, filename: str = "chart") -> None:
        """Render vertical bar chart"""
        if not data:
            print(f"No data to plot for {title}")
            return
            
        plt.figure(figsize=(10, 6))
        labels = list(data.keys())
        values = list(data.values())
        
        plt.bar(labels, values, color='blue', alpha=0.7)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for i, value in enumerate(values):
            plt.text(i, value + max(values) * 0.01, str(value), ha='center', va='bottom')
        
        plt.tight_layout()
        BarChartRenderer.save_chart(save_path, filename)
        BarChartRenderer.show_chart()
    
    @staticmethod
    def render_horizontal_bar(data: Dict[str, int], title: str, xlabel: str, ylabel: str,
                             save_path: Optional[str] = None, filename: str = "chart") -> None:
        """Render horizontal bar chart"""
        if not data:
            print(f"No data to plot for {title}")
            return
            
        plt.figure(figsize=(12, 8))
        labels = list(data.keys())
        values = list(data.values())
        
        plt.barh(labels, values, color='orange', alpha=0.7)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        # Add value labels on bars
        for i, value in enumerate(values):
            plt.text(value + max(values) * 0.01, i, str(value), va='center')
        
        plt.tight_layout()
        BarChartRenderer.save_chart(save_path, filename)
        BarChartRenderer.show_chart()


class LineChartRenderer(ChartRenderer):
    """Renders line charts"""
    
    @staticmethod
    def render_line_chart(data: Dict[str, int], title: str, xlabel: str, ylabel: str,
                         save_path: Optional[str] = None, filename: str = "chart") -> None:
        """Render line chart"""
        if not data:
            print(f"No data to plot for {title}")
            return
            
        plt.figure(figsize=(14, 6))
        labels = sorted(data.keys())
        values = [data[label] for label in labels]
        
        plt.plot(labels, values, marker='o', linewidth=2, markersize=4, color='red')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Show every nth label to avoid overcrowding
        n = max(1, len(labels) // 10)
        plt.xticks(labels[::n])
        
        plt.tight_layout()
        LineChartRenderer.save_chart(save_path, filename)
        LineChartRenderer.show_chart()


class PieChartRenderer(ChartRenderer):
    """Renders pie charts"""
    
    @staticmethod
    def render_pie_chart(data: Dict[str, int], title: str,
                        save_path: Optional[str] = None, filename: str = "chart") -> None:
        """Render pie chart"""
        if not data:
            print(f"No data to plot for {title}")
            return
            
        plt.figure(figsize=(12, 8))
        labels = list(data.keys())
        values = list(data.values())
        
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title(title)
        plt.axis('equal')
        
        plt.tight_layout()
        PieChartRenderer.save_chart(save_path, filename)
        PieChartRenderer.show_chart()


class TimeSeriesRenderer(ChartRenderer):
    """Renders time series charts"""
    
    @staticmethod
    def render_hourly_chart(data: Dict[int, int], title: str,
                           save_path: Optional[str] = None, filename: str = "chart") -> None:
        """Render hourly distribution chart"""
        if not data:
            print(f"No data to plot for {title}")
            return
            
        plt.figure(figsize=(12, 6))
        hours = sorted(data.keys())
        values = [data[hour] for hour in hours]
        
        plt.plot(hours, values, marker='o', linewidth=2, markersize=6, color='red')
        plt.fill_between(hours, values, alpha=0.3, color='red')
        plt.title(title)
        plt.xlabel('Hour')
        plt.ylabel('Count')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 24))
        
        plt.tight_layout()
        TimeSeriesRenderer.save_chart(save_path, filename)
        TimeSeriesRenderer.show_chart() 