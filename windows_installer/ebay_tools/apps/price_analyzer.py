#!/usr/bin/env python3
"""
eBay Price Analyzer

This module provides functionality to analyze eBay pricing based on 
similar sold items. It can be used standalone or integrated with
the eBay processing workflow.
"""

import json
import re
import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
from datetime import datetime, timedelta
import threading
import urllib.parse
import statistics

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Required packages not found. Install with: pip install requests beautifulsoup4")

# Import from ebay_tools package
try:
    from ebay_tools.core import schema, config, exceptions
    from ebay_tools.utils import ui_utils, background_utils
except ImportError:
    # For standalone use
    print("Running in standalone mode without ebay_tools package")


class PriceAnalyzer:
    """eBay price analyzer that finds similar sold items and recommends pricing."""
    
    def __init__(self, config_file=None):
        """Initialize the price analyzer with optional config file."""
        self.config = self._load_config(config_file)
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
    def _load_config(self, config_file=None):
        """Load configuration from file or use defaults."""
        default_config = {
            "default_markup": 15,  # Percentage markup above average
            "max_results": 10,     # Maximum number of results to analyze
            "min_results": 3,      # Minimum results needed for analysis
            "days_back": 90,       # How far back to look for sold items
            "exclude_words": ["broken", "for parts", "not working", "damaged"],
            "price_threshold": 0.3  # Threshold for excluding outliers (30% from median)
        }
        
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Update default config with loaded values
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config file: {e}")
                
        return default_config
    
    def analyze_item(self, search_terms=None, item_data=None, markup_percent=None, sample_limit=None):
        """
        Analyze eBay pricing for an item.
        
        Args:
            search_terms: Search terms to use for finding similar items
            item_data: Dictionary containing item data (optional)
            markup_percent: Custom markup percentage (overrides config)
            sample_limit: Limit the number of samples to analyze
            
        Returns:
            Dictionary with pricing analysis results
        """
        if not search_terms and item_data:
            # Extract search terms from item data
            search_terms = self._extract_search_terms(item_data)
        
        if not search_terms:
            raise ValueError("Search terms or item data must be provided")
            
        # Use provided markup or default from config
        markup = markup_percent if markup_percent is not None else self.config["default_markup"]
        
        # Set sample limit
        limit = sample_limit if sample_limit is not None else self.config["max_results"]
        
        # Get sold items
        sold_items = self._fetch_sold_items(search_terms, limit)
        
        if not sold_items or len(sold_items) < self.config["min_results"]:
            return {
                "success": False,
                "message": f"Not enough sold items found (needed {self.config['min_results']}, found {len(sold_items)})",
                "search_terms": search_terms,
                "sold_items": sold_items
            }
            
        # Analyze prices
        price_analysis = self._analyze_prices(sold_items)
        
        # Calculate suggested price
        suggested_price = self._calculate_suggested_price(price_analysis, markup)
        
        # Return complete results
        return {
            "success": True,
            "search_terms": search_terms,
            "sold_items": sold_items,
            "price_analysis": price_analysis,
            "suggested_price": suggested_price,
            "markup_percent": markup,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _extract_search_terms(self, item_data):
        """Extract search terms from item data."""
        search_terms = []
        
        # Use title if available
        if "title" in item_data and item_data["title"]:
            search_terms.append(item_data["title"])
            
        # Use brand and model if available in item specifics
        if "item_specifics" in item_data:
            specifics = item_data["item_specifics"]
            if "Brand" in specifics and specifics["Brand"]:
                search_terms.append(specifics["Brand"])
            if "Model" in specifics and specifics["Model"]:
                search_terms.append(specifics["Model"])
                
        # Join search terms
        return " ".join(search_terms)
    
    def _fetch_sold_items(self, search_terms, limit=10):
        """
        Fetch sold items from eBay.
        
        In a real implementation, this would use the eBay API or scrape eBay sold listings.
        For demo purposes, we'll generate simulated data.
        """
        # IMPORTANT: In a production environment, replace this with actual eBay API calls
        # or proper web scraping with appropriate rate limiting and compliance with eBay's TOS
        
        # For demonstration purposes only, generate simulated sold items
        # In a real implementation, you would use the eBay API or properly scrape eBay
        def simulate_sold_items(search_terms, count=10):
            """Generate simulated sold items for demonstration."""
            base_price = random.uniform(20, 200)
            variation = base_price * 0.3  # 30% variation
            
            sold_items = []
            for i in range(count):
                # Simulate price with some variation
                price = max(0.99, base_price + random.uniform(-variation, variation))
                
                # Random date within the past 90 days
                days_ago = random.randint(1, 90)
                sold_date = datetime.now() - timedelta(days=days_ago)
                
                item = {
                    "title": f"{search_terms} - Sample Item {i+1}",
                    "price": round(price, 2),
                    "shipping": round(random.uniform(0, 15), 2),
                    "sold_date": sold_date.strftime("%Y-%m-%d"),
                    "url": f"https://www.ebay.com/itm/{random.randint(100000000, 999999999)}",
                    "condition": random.choice(["New", "Used", "Open box", "Refurbished"]),
                    "item_id": f"{random.randint(100000000, 999999999)}"
                }
                sold_items.append(item)
                
            return sold_items
            
        # In a real implementation, replace this with actual eBay API or web scraping code
        sold_items = simulate_sold_items(search_terms, limit)
        return sold_items
    
    def _analyze_prices(self, sold_items):
        """Analyze prices from sold items."""
        if not sold_items:
            return None
            
        # Extract prices (item price + shipping)
        prices = [item["price"] + item["shipping"] for item in sold_items]
        
        # Calculate statistics
        stats = {
            "count": len(prices),
            "min": min(prices),
            "max": max(prices),
            "mean": statistics.mean(prices),
            "median": statistics.median(prices)
        }
        
        # Calculate standard deviation if we have enough data points
        if len(prices) >= 2:
            stats["stdev"] = statistics.stdev(prices)
        else:
            stats["stdev"] = 0
            
        return stats
    
    def _calculate_suggested_price(self, price_analysis, markup_percent):
        """Calculate suggested price based on analysis and markup."""
        if not price_analysis:
            return None
            
        # Use median price as baseline (more robust than mean against outliers)
        baseline = price_analysis["median"]
        
        # Calculate markup amount
        markup_amount = baseline * (markup_percent / 100)
        
        # Calculate suggested price
        suggested_price = baseline + markup_amount
        
        # Round to nearest $0.99
        suggested_price = round(suggested_price - 0.01, 0) + 0.99
        
        return suggested_price


class PriceAnalyzerGUI(tk.Toplevel):
    """GUI for the eBay Price Analyzer."""
    
    def __init__(self, parent, item_data=None, callback=None):
        """Initialize the price analyzer GUI."""
        super().__init__(parent)
        self.title("eBay Price Analyzer")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        self.parent = parent
        self.item_data = item_data or {}
        self.callback = callback
        self.analyzer = PriceAnalyzer()
        self.results = None
        
        # Set up variables
        self.search_terms_var = tk.StringVar()
        if item_data:
            self.search_terms_var.set(self.analyzer._extract_search_terms(item_data))
            
        self.markup_var = tk.StringVar(value=str(self.analyzer.config["default_markup"]))
        self.sample_limit_var = tk.StringVar(value=str(self.analyzer.config["max_results"]))
        
        # Create UI
        self._create_widgets()
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
    def _create_widgets(self):
        """Create GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Search")
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search Terms:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_terms_var, width=50)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Options frame
        options_frame = ttk.Frame(search_frame)
        options_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(options_frame, text="Markup %:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(options_frame, textvariable=self.markup_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(options_frame, text="Sample Limit:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(options_frame, textvariable=self.sample_limit_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(options_frame, text="Analyze", command=self._analyze_pricing).pack(side=tk.RIGHT, padx=5)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(main_frame, text="Results")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Initial message
        ttk.Label(
            self.results_frame, 
            text="Enter search terms and click Analyze to get price recommendations",
            font=("Segoe UI", 10, "italic")
        ).pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.apply_button = ttk.Button(
            button_frame, 
            text="Apply Price", 
            command=self._apply_price,
            state=tk.DISABLED
        )
        self.apply_button.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
    def _analyze_pricing(self):
        """Analyze pricing based on search terms."""
        search_terms = self.search_terms_var.get().strip()
        if not search_terms:
            messagebox.showerror("Error", "Please enter search terms")
            return
            
        try:
            markup = float(self.markup_var.get())
            sample_limit = int(self.sample_limit_var.get())
        except ValueError:
            messagebox.showerror("Error", "Markup and sample limit must be valid numbers")
            return
            
        # Show loading indicator
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        loading_label = ttk.Label(
            self.results_frame, 
            text="Analyzing prices...",
            font=("Segoe UI", 10, "italic")
        )
        loading_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.update_idletasks()
        
        # Run analysis in background thread
        def run_analysis():
            try:
                results = self.analyzer.analyze_item(
                    search_terms=search_terms,
                    item_data=self.item_data,
                    markup_percent=markup,
                    sample_limit=sample_limit
                )
                self.after(0, lambda: self._display_results(results))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {str(e)}"))
                
        threading.Thread(target=run_analysis).start()
        
    def _display_results(self, results):
        """Display price analysis results."""
        self.results = results
        
        # Clear results frame
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        # Create scrollable frame
        container = ttk.Frame(self.results_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Display results
        if not results["success"]:
            ttk.Label(
                scrollable_frame, 
                text=f"Analysis failed: {results['message']}",
                font=("Segoe UI", 10, "italic"),
                foreground="red"
            ).pack(fill=tk.X, padx=10, pady=5)
            return
            
        # Summary section
        summary_frame = ttk.LabelFrame(scrollable_frame, text="Price Summary")
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        analysis = results["price_analysis"]
        
        # Display statistics
        stats_text = f"Found {analysis['count']} sold items\n"
        stats_text += f"Price Range: ${analysis['min']:.2f} - ${analysis['max']:.2f}\n"
        stats_text += f"Average Price: ${analysis['mean']:.2f}\n"
        stats_text += f"Median Price: ${analysis['median']:.2f}\n"
        
        if "stdev" in analysis and analysis["stdev"] > 0:
            stats_text += f"Standard Deviation: ${analysis['stdev']:.2f}"
            
        ttk.Label(
            summary_frame, 
            text=stats_text,
            justify=tk.LEFT,
            font=("Segoe UI", 10)
        ).pack(fill=tk.X, padx=10, pady=5)
        
        # Suggested price (highlighted)
        suggested_frame = ttk.Frame(summary_frame)
        suggested_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            suggested_frame, 
            text="Suggested Price:",
            font=("Segoe UI", 12, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            suggested_frame, 
            text=f"${results['suggested_price']:.2f}",
            font=("Segoe UI", 14, "bold"),
            foreground="green"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            suggested_frame, 
            text=f"(+{results['markup_percent']}% markup)",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        # Sold items table
        items_frame = ttk.LabelFrame(scrollable_frame, text="Similar Sold Items")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create table
        columns = ("title", "price", "shipping", "total", "condition", "date")
        tree = ttk.Treeview(items_frame, columns=columns, show="headings")
        
        # Define headings
        tree.heading("title", text="Item Title")
        tree.heading("price", text="Price")
        tree.heading("shipping", text="Shipping")
        tree.heading("total", text="Total")
        tree.heading("condition", text="Condition")
        tree.heading("date", text="Sold Date")
        
        # Define columns
        tree.column("title", width=250)
        tree.column("price", width=70, anchor=tk.E)
        tree.column("shipping", width=70, anchor=tk.E)
        tree.column("total", width=70, anchor=tk.E)
        tree.column("condition", width=100)
        tree.column("date", width=100)
        
        # Add scrollbar
        yscrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscrollbar.set)
        
        # Add items to table
        for item in results["sold_items"]:
            total = item["price"] + item["shipping"]
            tree.insert("", tk.END, values=(
                item["title"],
                f"${item['price']:.2f}",
                f"${item['shipping']:.2f}",
                f"${total:.2f}",
                item["condition"],
                item["sold_date"]
            ))
            
        # Pack tree and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enable apply button
        self.apply_button.configure(state=tk.NORMAL)
        
    def _apply_price(self):
        """Apply the suggested price to the item."""
        if not self.results or not self.results["success"]:
            return
            
        suggested_price = self.results["suggested_price"]
        
        if not self.callback:
            # If no callback, just copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(f"{suggested_price:.2f}")
            messagebox.showinfo("Price Copied", f"The suggested price ${suggested_price:.2f} has been copied to clipboard")
        else:
            # Call the callback function with results
            self.callback(self.results)
            messagebox.showinfo("Price Applied", f"Applied price ${suggested_price:.2f} to item")
            
        self.destroy()


def main():
    """Run the eBay Price Analyzer as a standalone application."""
    root = tk.Tk()
    root.title("eBay Price Analyzer")
    root.withdraw()  # Hide the root window
    
    # Create and show the analyzer GUI
    analyzer_gui = PriceAnalyzerGUI(root)
    
    # Wait for the window to be closed
    root.wait_window(analyzer_gui)
    
    # Exit the application
    root.destroy()


if __name__ == "__main__":
    main()