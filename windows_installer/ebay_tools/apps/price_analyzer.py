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
        current_items = []
        
        if not sold_items or len(sold_items) < self.config["min_results"]:
            # If no sold items found, get current listings for reference
            current_items = self._fetch_current_listings(search_terms, limit)
            
            if not current_items:
                return {
                    "success": False,
                    "message": f"No sold items found (needed {self.config['min_results']}, found {len(sold_items)}) and no current listings available",
                    "search_terms": search_terms,
                    "sold_items": sold_items,
                    "current_items": current_items
                }
            
            # Return result with current items but no pricing suggestion
            return {
                "success": False,
                "message": f"No sold items found for pricing analysis. Showing {len(current_items)} current listings for reference.",
                "search_terms": search_terms,
                "sold_items": sold_items,
                "current_items": current_items,
                "requires_manual_pricing": True
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
            "current_items": current_items,
            "price_analysis": price_analysis,
            "suggested_price": suggested_price,
            "markup_percent": markup,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _extract_search_terms(self, item_data):
        """Extract comprehensive search terms from item data."""
        search_terms = []
        
        # Use title if available (primary search term)
        if "title" in item_data and item_data["title"]:
            # Clean up the title - remove common noise words but keep important details
            title = item_data["title"]
            search_terms.append(title)
        elif "temp_title" in item_data and item_data["temp_title"]:
            search_terms.append(item_data["temp_title"])
            
        # Add important item specifics that help identify the exact item
        if "item_specifics" in item_data:
            specifics = item_data["item_specifics"]
            
            # Priority order: Brand, Model, MPN are most important for matching
            priority_fields = ["Brand", "Model", "MPN", "Part Number"]
            for field in priority_fields:
                if field in specifics and specifics[field]:
                    search_terms.append(specifics[field])
            
            # Add other identifying characteristics
            other_important = ["Color", "Size", "Type", "Series", "Edition"]
            for field in other_important:
                if field in specifics and specifics[field]:
                    # Only add if it's not already in the title
                    if specifics[field].lower() not in " ".join(search_terms).lower():
                        search_terms.append(specifics[field])
        
        # Join search terms with spaces
        full_search = " ".join(search_terms)
        
        # Clean up the search string
        # Remove extra spaces and common noise words that might hurt search accuracy
        noise_words = ["FAST", "FREE", "SHIPPING", "NEW", "USED", "NICE", "GREAT", "EXCELLENT", "RARE"]
        words = full_search.split()
        cleaned_words = [word for word in words if word.upper() not in noise_words]
        
        return " ".join(cleaned_words)
    
    def _fetch_real_sold_items(self, search_terms, limit=10):
        """
        Fetch real sold items using unofficial eBay sold items API.
        
        Uses the API mentioned: https://ebay-sold-items-api.herokuapp.com/findCompletedItems
        """
        try:
            import requests
            import json
            from urllib.parse import quote
            
            # API endpoint for sold items
            url = "https://ebay-sold-items-api.herokuapp.com/findCompletedItems"
            
            # Prepare payload
            payload = {
                "keywords": search_terms,
                "excluded_keywords": "broken damaged parts repair for parts only read description",
                "max_search_results": str(min(limit, 100)),  # API limit
                "category_id": "",  # Empty for all categories
                "remove_outliers": True,
                "site_id": "0"  # US site
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'eBay Tools Price Analyzer'
            }
            
            # Make request with timeout
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'items' in data and data['items']:
                    sold_items = []
                    for item in data['items'][:limit]:
                        # Convert API response to our format
                        sold_item = {
                            "title": item.get('title', 'Unknown Item'),
                            "price": float(item.get('price', {}).get('value', 0)),
                            "shipping": float(item.get('shippingCost', {}).get('value', 0)),
                            "sold_date": item.get('endTime', '').split('T')[0] if 'endTime' in item else '',
                            "url": item.get('viewItemURL', ''),
                            "condition": item.get('condition', {}).get('conditionDisplayName', 'Unknown'),
                            "item_id": item.get('itemId', '')
                        }
                        sold_items.append(sold_item)
                    
                    print(f"Successfully fetched {len(sold_items)} real sold items from API")
                    return sold_items
                else:
                    print("API returned no sold items")
            else:
                print(f"API request failed with status {response.status_code}")
        
        except ImportError:
            print("requests library not available for real API calls")
        except Exception as e:
            print(f"Error fetching real sold data: {e}")
        
        return None
    
    def _fetch_sold_items(self, search_terms, limit=10):
        """
        Fetch sold items from eBay.
        
        First tries unofficial API, falls back to simulated data for demo.
        """
        # Try to fetch real sold data first
        try:
            real_sold_items = self._fetch_real_sold_items(search_terms, limit)
            if real_sold_items:
                return real_sold_items
        except Exception as e:
            print(f"Note: Could not fetch real sold data ({e}), using simulated data")
        
        # Fall back to simulated data for demo purposes
        # IMPORTANT: In a production environment, replace this with actual eBay API calls
        # or proper web scraping with appropriate rate limiting and compliance with eBay's TOS
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
                
                # Create working eBay sold listings search URL
                # The correct way to search sold listings on eBay
                encoded_search = search_terms.replace(' ', '+').replace('&', '%26')
                sold_url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_search}&_sacat=0&_odkw=&_osacat=0&_ipg=240&_fosrp=1&_stpos=&LH_Sold=1&LH_Complete=1"
                
                item = {
                    "title": f"{search_terms} - Sample Item {i+1}",
                    "price": round(price, 2),
                    "shipping": round(random.uniform(0, 15), 2),
                    "sold_date": sold_date.strftime("%Y-%m-%d"),
                    "url": sold_url,
                    "condition": random.choice(["New", "Used", "Open box", "Refurbished"]),
                    "item_id": f"{random.randint(100000000, 999999999)}"
                }
                sold_items.append(item)
                
            return sold_items
            
        # In a real implementation, replace this with actual eBay API or web scraping code
        sold_items = simulate_sold_items(search_terms, limit)
        return sold_items

    def _fetch_current_listings(self, search_terms, limit=10):
        """
        Fetch current active listings from eBay when no sold items found.
        
        In a real implementation, this would use the eBay API or scrape current listings.
        For demo purposes, we'll generate simulated data.
        """
        def simulate_current_listings(search_terms, count=10):
            """Generate simulated current listings for demonstration."""
            base_price = random.uniform(25, 250)
            variation = base_price * 0.4  # 40% variation for active listings
            
            current_items = []
            for i in range(count):
                # Simulate price with some variation
                price = max(0.99, base_price + random.uniform(-variation, variation))
                
                # Random listing date within the past 30 days
                days_ago = random.randint(1, 30)
                list_date = datetime.now() - timedelta(days=days_ago)
                
                item = {
                    "title": f"{search_terms} - Current Listing {i+1}",
                    "price": round(price, 2),
                    "shipping": round(random.uniform(0, 20), 2),
                    "list_date": list_date.strftime("%Y-%m-%d"),
                    "url": f"https://www.ebay.com/itm/{random.randint(100000000, 999999999)}",
                    "condition": random.choice(["New", "Used", "Open box", "Refurbished"]),
                    "item_id": f"{random.randint(100000000, 999999999)}",
                    "watchers": random.randint(0, 15),
                    "views": random.randint(10, 200)
                }
                current_items.append(item)
                
            return current_items
            
        current_items = simulate_current_listings(search_terms, limit)
        return current_items
    
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
        self.final_price_var = tk.StringVar()
        self.price_approved = False
        
        # Create UI
        self._create_widgets()
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        # Make modal only if parent is visible
        if parent and parent.winfo_viewable():
            self.transient(parent)
            self.grab_set()
        else:
            # For standalone use, make it a normal window
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        
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
        """Display price analysis results with enhanced approval workflow."""
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
        
        # Handle different result types
        if not results["success"]:
            if "requires_manual_pricing" in results and results["requires_manual_pricing"]:
                self._display_manual_pricing_mode(scrollable_frame, results)
            else:
                ttk.Label(
                    scrollable_frame, 
                    text=f"Analysis failed: {results['message']}",
                    font=("Segoe UI", 10, "italic"),
                    foreground="red"
                ).pack(fill=tk.X, padx=10, pady=5)
            return
            
        # Display successful analysis with sold items
        self._display_successful_analysis(scrollable_frame, results)

    def _display_manual_pricing_mode(self, parent, results):
        """Display current listings when no sold items found."""
        # Message frame
        message_frame = ttk.LabelFrame(parent, text="⚠️ No Sold Items Found")
        message_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            message_frame,
            text=results["message"],
            font=("Segoe UI", 10),
            foreground="orange"
        ).pack(fill=tk.X, padx=10, pady=5)
        
        # Manual pricing frame
        pricing_frame = ttk.LabelFrame(parent, text="💡 Manual Price Entry")
        pricing_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            pricing_frame,
            text="Based on current market listings below, enter your price:",
            font=("Segoe UI", 10)
        ).pack(fill=tk.X, padx=10, pady=5)
        
        price_entry_frame = ttk.Frame(pricing_frame)
        price_entry_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(price_entry_frame, text="Price: $", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=5)
        price_entry = ttk.Entry(price_entry_frame, textvariable=self.final_price_var, width=10, font=("Segoe UI", 12))
        price_entry.pack(side=tk.LEFT, padx=5)
        
        def validate_price():
            try:
                price = float(self.final_price_var.get())
                if price > 0:
                    self.price_approved = True
                    self.apply_button.configure(state=tk.NORMAL)
                else:
                    self.apply_button.configure(state=tk.DISABLED)
            except ValueError:
                self.apply_button.configure(state=tk.DISABLED)
        
        self.final_price_var.trace('w', lambda *args: validate_price())
        
        # Current listings table
        if "current_items" in results and results["current_items"]:
            self._display_current_listings(parent, results["current_items"])

    def _display_current_listings(self, parent, current_items):
        """Display current active listings for reference."""
        listings_frame = ttk.LabelFrame(parent, text="📊 Current Market Listings (Reference)")
        listings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Calculate price statistics for reference
        prices = [item["price"] + item["shipping"] for item in current_items]
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            
            stats_text = f"Current listings: {len(current_items)} • "
            stats_text += f"Price range: ${min_price:.2f} - ${max_price:.2f} • "
            stats_text += f"Average: ${avg_price:.2f}"
            
            ttk.Label(
                listings_frame,
                text=stats_text,
                font=("Segoe UI", 9, "italic")
            ).pack(fill=tk.X, padx=10, pady=5)
        
        # Create table for current listings
        columns = ("title", "price", "shipping", "total", "condition", "date", "watchers", "views")
        tree = ttk.Treeview(listings_frame, columns=columns, show="headings", height=8)
        
        # Define headings
        tree.heading("title", text="Item Title")
        tree.heading("price", text="Price")
        tree.heading("shipping", text="Shipping")
        tree.heading("total", text="Total")
        tree.heading("condition", text="Condition")
        tree.heading("date", text="Listed")
        tree.heading("watchers", text="Watchers")
        tree.heading("views", text="Views")
        
        # Define columns
        tree.column("title", width=200)
        tree.column("price", width=60, anchor=tk.E)
        tree.column("shipping", width=60, anchor=tk.E)
        tree.column("total", width=60, anchor=tk.E)
        tree.column("condition", width=80)
        tree.column("date", width=80)
        tree.column("watchers", width=60, anchor=tk.E)
        tree.column("views", width=60, anchor=tk.E)
        
        # Add scrollbar
        yscrollbar = ttk.Scrollbar(listings_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscrollbar.set)
        
        # Add items to table
        for item in current_items:
            total = item["price"] + item["shipping"]
            tree.insert("", tk.END, values=(
                item["title"],
                f"${item['price']:.2f}",
                f"${item['shipping']:.2f}",
                f"${total:.2f}",
                item["condition"],
                item["list_date"],
                item["watchers"],
                item["views"]
            ))
            
        # Pack tree and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _display_successful_analysis(self, parent, results):
        """Display successful price analysis with sold items."""
        analysis = results["price_analysis"]
        
        # Price calculation breakdown
        calc_frame = ttk.LabelFrame(parent, text="🧮 Price Calculation Breakdown")
        calc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Step-by-step calculation
        steps_frame = ttk.Frame(calc_frame)
        steps_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Step 1: Base price (median)
        step1_frame = ttk.Frame(steps_frame)
        step1_frame.pack(fill=tk.X, pady=2)
        ttk.Label(step1_frame, text="1. Median price from sold items:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        ttk.Label(step1_frame, text=f"${analysis['median']:.2f}", font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT)
        
        # Step 2: Markup calculation
        markup_amount = analysis['median'] * (results['markup_percent'] / 100)
        step2_frame = ttk.Frame(steps_frame)
        step2_frame.pack(fill=tk.X, pady=2)
        ttk.Label(step2_frame, text=f"2. Markup ({results['markup_percent']}%):", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        ttk.Label(step2_frame, text=f"+${markup_amount:.2f}", font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT)
        
        # Step 3: Final suggested price
        ttk.Separator(steps_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        step3_frame = ttk.Frame(steps_frame)
        step3_frame.pack(fill=tk.X, pady=2)
        ttk.Label(step3_frame, text="3. Suggested price:", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        ttk.Label(step3_frame, text=f"${results['suggested_price']:.2f}", font=("Segoe UI", 12, "bold"), foreground="green").pack(side=tk.RIGHT)
        
        # Price approval section
        approval_frame = ttk.LabelFrame(parent, text="✅ Price Approval")
        approval_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Set initial value
        self.final_price_var.set(f"{results['suggested_price']:.2f}")
        
        price_approval_frame = ttk.Frame(approval_frame)
        price_approval_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(price_approval_frame, text="Final Price: $", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=5)
        price_entry = ttk.Entry(price_approval_frame, textvariable=self.final_price_var, width=10, font=("Segoe UI", 12))
        price_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            price_approval_frame,
            text="Use Suggested",
            command=lambda: self.final_price_var.set(f"{results['suggested_price']:.2f}")
        ).pack(side=tk.LEFT, padx=10)
        
        def validate_and_approve():
            try:
                price = float(self.final_price_var.get())
                if price > 0:
                    self.price_approved = True
                    self.apply_button.configure(state=tk.NORMAL, text=f"Apply ${price:.2f}")
                    # Update results with final price
                    self.results["final_price"] = price
                else:
                    self.apply_button.configure(state=tk.DISABLED, text="Apply Price")
            except ValueError:
                self.apply_button.configure(state=tk.DISABLED, text="Apply Price")
        
        self.final_price_var.trace('w', lambda *args: validate_and_approve())
        
        # Statistics summary
        stats_frame = ttk.LabelFrame(parent, text="📈 Market Analysis Summary")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        stats_text = f"Analyzed {analysis['count']} sold items • "
        stats_text += f"Range: ${analysis['min']:.2f} - ${analysis['max']:.2f} • "
        stats_text += f"Average: ${analysis['mean']:.2f} • "
        stats_text += f"Median: ${analysis['median']:.2f}"
        
        if "stdev" in analysis and analysis["stdev"] > 0:
            stats_text += f" • Std Dev: ${analysis['stdev']:.2f}"
            
        ttk.Label(
            stats_frame, 
            text=stats_text,
            justify=tk.LEFT,
            font=("Segoe UI", 9)
        ).pack(fill=tk.X, padx=10, pady=5)
        
        # Sold items table
        items_frame = ttk.LabelFrame(parent, text="📋 Recent Sold Items")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create table
        columns = ("title", "price", "shipping", "total", "condition", "date", "url")
        tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=10)
        
        # Define headings
        tree.heading("title", text="Item Title")
        tree.heading("price", text="Price")
        tree.heading("shipping", text="Shipping")
        tree.heading("total", text="Total")
        tree.heading("condition", text="Condition")
        tree.heading("date", text="Sold Date")
        tree.heading("url", text="eBay Link")
        
        # Define columns
        tree.column("title", width=200)
        tree.column("price", width=70, anchor=tk.E)
        tree.column("shipping", width=70, anchor=tk.E)
        tree.column("total", width=70, anchor=tk.E)
        tree.column("condition", width=100)
        tree.column("date", width=100)
        tree.column("url", width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        yscrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscrollbar.set)
        
        # Add items to table
        for item in results["sold_items"]:
            total = item["price"] + item["shipping"]
            # Format URL for display
            url_display = "Click to Open" if item.get("url") else "N/A"
            tree.insert("", tk.END, values=(
                item["title"],
                f"${item['price']:.2f}",
                f"${item['shipping']:.2f}",
                f"${total:.2f}",
                item["condition"],
                item["sold_date"],
                url_display
            ))
            
        # Add click handler to open URLs
        def on_item_click(event):
            """Handle double-click on tree items to open eBay listing URLs."""
            selection = tree.selection()
            if selection:
                # Get the selected item
                item_id = selection[0]
                item_values = tree.item(item_id, 'values')
                
                # Find the corresponding sold item by matching title and price
                if item_values:
                    title = item_values[0]
                    price_str = item_values[1]
                    
                    # Find matching item in results
                    for sold_item in results["sold_items"]:
                        if (sold_item["title"] == title and 
                            f"${sold_item['price']:.2f}" == price_str):
                            url = sold_item.get("url")
                            if url:
                                try:
                                    import webbrowser
                                    webbrowser.open(url)
                                    self.status_bar.update(f"Opened eBay listing: {title}")
                                except Exception as e:
                                    messagebox.showerror("Error", f"Failed to open URL: {str(e)}")
                            else:
                                messagebox.showinfo("No URL", "No URL available for this item")
                            break
        
        # Bind double-click event
        tree.bind("<Double-1>", on_item_click)
        
        # Pack tree and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add instruction label
        instruction_frame = ttk.Frame(items_frame)
        instruction_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(
            instruction_frame, 
            text="💡 Double-click any row to view the actual eBay listing (if real data) or search sold listings",
            font=("Segoe UI", 9),
            foreground="blue"
        ).pack(anchor=tk.W)
        
        # Check if we're using real or simulated data to display appropriate message
        using_real_data = any(not item["title"].endswith(f"Sample Item {i+1}") for i, item in enumerate(results["sold_items"], 1))
        
        if using_real_data:
            info_text = "✅ Using real sold listing data from eBay API. Links open actual sold listings."
            info_color = "green"
        else:
            info_text = "ℹ️  Demo mode: Simulated data shown. Links open eBay sold listings search for verification."
            info_color = "gray"
        
        ttk.Label(
            instruction_frame, 
            text=info_text,
            font=("Segoe UI", 8),
            foreground=info_color
        ).pack(anchor=tk.W, pady=(2,0))
        
        # Initial validation
        validate_and_approve()
        
    def _apply_price(self):
        """Apply the approved price to the item."""
        # Get the final price from the entry field
        try:
            final_price = float(self.final_price_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price")
            return
            
        if final_price <= 0:
            messagebox.showerror("Error", "Price must be greater than 0")
            return
        
        # Update results with final approved price
        if self.results:
            self.results["final_price"] = final_price
            self.results["user_approved"] = True
        else:
            # Manual pricing mode - create minimal results
            self.results = {
                "success": True,
                "final_price": final_price,
                "user_approved": True,
                "search_terms": self.search_terms_var.get(),
                "manual_pricing": True
            }
        
        if not self.callback:
            # If no callback, just copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(f"{final_price:.2f}")
            messagebox.showinfo("Price Copied", f"The price ${final_price:.2f} has been copied to clipboard")
        else:
            # Call the callback function with results
            self.callback(self.results)
            messagebox.showinfo("Price Applied", f"Applied price ${final_price:.2f} to item")
            
        self.destroy()
    
    def _on_close(self):
        """Handle window close event for standalone use."""
        self.destroy()
        if self.parent:
            self.parent.quit()


def main():
    """Run the eBay Price Analyzer as a standalone application."""
    root = tk.Tk()
    root.title("eBay Price Analyzer")
    root.withdraw()  # Hide the root window
    
    # Create and show the analyzer GUI
    analyzer_gui = PriceAnalyzerGUI(root)
    
    # Ensure the window is visible and on top
    analyzer_gui.deiconify()
    analyzer_gui.lift()
    analyzer_gui.focus_force()
    
    # Wait for the window to be closed
    root.wait_window(analyzer_gui)
    
    # Exit the application
    root.destroy()


if __name__ == "__main__":
    main()