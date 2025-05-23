import sqlite3
import json
import pandas as pd
from datetime import datetime
from textblob import TextBlob
import threading

class InventorySystem:
    def __init__(self, db_name='inventory.db', risk_config_path='data/analysis_results.json'):
        self.db_name = db_name
        self.risk_config_path = risk_config_path
        self.local = threading.local()
        self._create_tables()
        self._load_initial_inventory()
        self._load_risk_configuration()

    def get_connection(self):
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_name)
        return self.local.conn

    def get_cursor(self):
        if not hasattr(self.local, 'cursor'):
            self.local.cursor = self.get_connection().cursor()
        return self.local.cursor

    def _create_tables(self):
        conn = self.get_connection()
        cursor = self.get_cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                product_id TEXT PRIMARY KEY,
                product_name TEXT,
                total_stock INTEGER,
                min_threshold INTEGER,
                max_capacity INTEGER,
                unit_price REAL,
                risk_factor REAL DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS damage_log (
                log_id INTEGER PRIMARY KEY,
                product_id TEXT,
                quantity_damaged INTEGER,
                damage_reason TEXT,
                timestamp DATETIME
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transport_delays (
                delay_id INTEGER PRIMARY KEY,
                product_id TEXT,
                expected_delivery DATETIME,
                actual_delivery DATETIME,
                delay_reason TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_log (
                sale_id INTEGER PRIMARY KEY,
                product_id TEXT,
                quantity_sold INTEGER,
                sale_timestamp DATETIME,
                sale_status TEXT
            )
        ''')

        conn.commit()

    def _load_initial_inventory(self):
        conn = self.get_connection()
        cursor = self.get_cursor()
        initial_inventory = [
            ('LIB001', 'Standard Lithium Battery', 5000, 1000, 10000, 50.0),
            ('LIB002', 'High-Capacity Battery', 3000, 500, 7000, 75.0),
            ('LIB003', 'EV Battery Module', 1500, 250, 4000, 200.0)
        ]

        for product in initial_inventory:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO inventory
                    (product_id, product_name, total_stock, min_threshold, max_capacity, unit_price)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', product)
            except sqlite3.IntegrityError:
                print(f"Product {product[0]} already exists")

        conn.commit()

    def _load_risk_configuration(self):
        try:
            with open(self.risk_config_path, 'r') as f:
                risk_data = json.load(f)

            sentiment_scores = [
                article['sentiment_analysis']['score']
                for article in risk_data
                if 'sentiment_analysis' in article
            ]

            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.5

            self.risk_config = {
                'inventory_risk_weights': {
                    'inventory_level': 0.3,
                    'lead_time': 0.2,
                    'news_sentiment': avg_sentiment,
                    'textual_risk': 1 - avg_sentiment
                }
            }
        except (FileNotFoundError, json.JSONDecodeError):
            self.risk_config = {
                'inventory_risk_weights': {
                    'inventory_level': 0.3,
                    'lead_time': 0.2,
                    'news_sentiment': 0.3,
                    'textual_risk': 0.2
                }
            }

    def predict_risk(self, inventory_level, lead_time, news_text, textual_risk):
        sentiment_score = TextBlob(news_text).sentiment.polarity
        
        norm_inventory = min(max(inventory_level / 5000, 0), 1)
        norm_lead_time = min(max(lead_time / 30, 0), 1)
        norm_sentiment = (sentiment_score + 1) / 2
        norm_textual_risk = min(max(textual_risk / 10, 0), 1)

        weights = self.risk_config['inventory_risk_weights']
        risk_score = (
            (1 - norm_inventory) * weights['inventory_level'] +
            (1 - norm_lead_time) * weights['lead_time'] +
            (1 - norm_sentiment) * weights['news_sentiment'] +
            norm_textual_risk * weights['textual_risk']
        )

        if risk_score > 0.7:
            return 'High', risk_score
        elif risk_score > 0.3:
            return 'Medium', risk_score
        else:
            return 'Low', risk_score

    def update_inventory(self, product_id, quantity, action="add"):
        try:
            cursor = self.get_cursor()
            conn = self.get_connection()
            
            if action.lower() == "add":
                cursor.execute('''
                    UPDATE inventory
                    SET total_stock = total_stock + ?
                    WHERE product_id = ?
                ''', (quantity, product_id))
            else:
                cursor.execute('''
                    UPDATE inventory
                    SET total_stock = total_stock - ?
                    WHERE product_id = ?
                ''', (quantity, product_id))
            
            conn.commit()
            return True, "Inventory updated successfully"
        except Exception as e:
            return False, f"Error updating inventory: {str(e)}"

    def log_damage(self, product_id, quantity_damaged, damage_reason):
        timestamp = datetime.now()
        try:
            cursor = self.get_cursor()
            conn = self.get_connection()
            
            cursor.execute('''
                INSERT INTO damage_log
                (product_id, quantity_damaged, damage_reason, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (product_id, quantity_damaged, damage_reason, timestamp))

            self.update_inventory(product_id, quantity_damaged, "remove")
            conn.commit()
            return True, "Damage logged successfully"
        except Exception as e:
            return False, f"Error logging damage: {str(e)}"

    def log_transport_delay(self, product_id, expected_delivery, actual_delivery, delay_reason):
        try:
            cursor = self.get_cursor()
            conn = self.get_connection()
            
            cursor.execute('''
                INSERT INTO transport_delays
                (product_id, expected_delivery, actual_delivery, delay_reason)
                VALUES (?, ?, ?, ?)
            ''', (product_id, expected_delivery, actual_delivery, delay_reason))

            conn.commit()
            return True, "Transport delay logged successfully"
        except Exception as e:
            return False, f"Error logging transport delay: {str(e)}"

    def log_sales(self, product_id, quantity_sold):
        timestamp = datetime.now()
        try:
            cursor = self.get_cursor()
            conn = self.get_connection()
            
            # Check current stock
            cursor.execute('SELECT total_stock FROM inventory WHERE product_id = ?', (product_id,))
            current_stock = cursor.fetchone()[0]
            
            if current_stock < quantity_sold:
                return False, "Insufficient stock"

            # Update inventory
            success, message = self.update_inventory(product_id, quantity_sold, "remove")
            if not success:
                return False, message

            # Log sale
            cursor.execute('''
                INSERT INTO sales_log
                (product_id, quantity_sold, sale_timestamp, sale_status)
                VALUES (?, ?, ?, ?)
            ''', (product_id, quantity_sold, timestamp, 'Normal'))

            conn.commit()
            return True, "Sale logged successfully"
        except Exception as e:
            return False, f"Error logging sale: {str(e)}"

    def get_current_inventory(self):
        """Get current inventory as DataFrame"""
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM inventory")
        columns = [description[0] for description in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

    def get_damage_log(self):
        """Get damage log as DataFrame"""
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM damage_log")
        columns = [description[0] for description in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

    def get_transport_delays(self):
        """Get transport delays as DataFrame"""
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM transport_delays")
        columns = [description[0] for description in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

    def get_sales_log(self):
        """Get sales log as DataFrame"""
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM sales_log")
        columns = [description[0] for description in cursor.description]
        return pd.DataFrame(cursor.fetchall(), columns=columns)

    def update_risk_factor(self, product_id, risk_factor):
        """Update the risk factor for a specific product"""
        cursor = self.get_cursor()
        cursor.execute(
            "UPDATE inventory SET risk_factor = ? WHERE product_id = ?",
            (risk_factor, product_id)
        )
        self.get_connection().commit() 