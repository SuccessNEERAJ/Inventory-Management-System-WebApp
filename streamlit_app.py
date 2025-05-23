import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from milestone2 import NewsAnalyzer
from milestone3 import InventorySystem
import json
import plotly.express as px
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "neerajjaiswal938@gmail.com",
    "sender_password": "fxqz conh gqyq dugb",   # Make sure this is your 16-character App Password
    "recipient_email": "cuneerajjaiswal@gmail.com"
}

# Initialize session state
if 'news_analyzer' not in st.session_state:
    st.session_state.news_analyzer = NewsAnalyzer(
        groq_api_key="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",
        event_registry_api_key="c3892498-706c-443a-a9a7-b194c52887b7"
    )
if 'inventory_system' not in st.session_state:
    st.session_state.inventory_system = InventorySystem()
if 'scenarios_run' not in st.session_state:
    st.session_state.scenarios_run = False
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'last_check_time' not in st.session_state:
    st.session_state.last_check_time = datetime.now()

def send_email_alert(subject, body):
    """Send email alert"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender_email"]
        msg['To'] = EMAIL_CONFIG["recipient_email"]
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def check_alerts():
    """Check for alerts and update session state"""
    try:
        inventory = st.session_state.inventory_system.get_current_inventory()
        current_time = datetime.now()
        
        for _, row in inventory.iterrows():
            # Check for low stock
            if row['total_stock'] <= row['min_threshold']:
                alert = {
                    'timestamp': current_time,
                    'type': 'Low Stock',
                    'product_id': row['product_id'],
                    'message': f"Low stock alert: {row['product_id']} is below minimum threshold ({row['total_stock']}/{row['min_threshold']})",
                    'severity': 'High'
                }
                if not any(a['type'] == alert['type'] and a['product_id'] == alert['product_id'] for a in st.session_state.alerts):
                    st.session_state.alerts.append(alert)
                    send_email_alert(
                        "Low Stock Alert",
                        f"Product {row['product_id']} is below minimum threshold.\nCurrent stock: {row['total_stock']}\nMinimum threshold: {row['min_threshold']}"
                    )
            
            # Check for high risk
            if row['risk_factor'] >= 7:
                alert = {
                    'timestamp': current_time,
                    'type': 'High Risk',
                    'product_id': row['product_id'],
                    'message': f"High risk alert: {row['product_id']} has risk factor of {row['risk_factor']}",
                    'severity': 'High'
                }
                if not any(a['type'] == alert['type'] and a['product_id'] == alert['product_id'] for a in st.session_state.alerts):
                    st.session_state.alerts.append(alert)
                    send_email_alert(
                        "High Risk Alert",
                        f"Product {row['product_id']} has high risk factor.\nRisk Factor: {row['risk_factor']}"
                    )
        
        st.session_state.last_check_time = current_time
    except Exception as e:
        st.error(f"Error checking alerts: {str(e)}")

# Function to update alerts tab
def update_alerts_tab():
    if st.session_state.alerts:
        alert_df = pd.DataFrame(st.session_state.alerts)
        st.subheader("Active Alerts")
        
        def color_severity(val):
            color = 'red' if val == 'High' else 'orange'
            return f'color: {color}'
        
        styled_alert_df = alert_df.style.applymap(color_severity, subset=['severity'])
        st.dataframe(styled_alert_df)

# Page title
st.title("Supply Chain Risk and Inventory Management Dashboard")

# Create horizontal tabs
tab_alerts, tab_scenarios, tab_inventory, tab_damage, tab_transport, tab_sales, tab_news, tab_chat = st.tabs([
    "Alerts & Analytics", "Run Scenarios", "Inventory Management", "Damage Log", "Transport Delays", 
    "Sales Log", "News Analysis", "LLaMA Chat"
])

# Alerts & Analytics Tab
with tab_alerts:
    st.header("Real-Time Alerts & Analytics Dashboard")
    
    # Add auto-refresh
    auto_refresh = st.empty()
    with auto_refresh.container():
        # Check for new alerts
        check_alerts()
        update_alerts_tab()
    
    # Add manual refresh button
    if st.button("Refresh Alerts"):
        check_alerts()
        st.rerun()
    
    # Visualizations
    st.subheader("Supply Chain Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Inventory Levels Chart
        inventory = st.session_state.inventory_system.get_current_inventory()
        fig_inventory = go.Figure()
        fig_inventory.add_trace(go.Bar(
            name='Current Stock',
            x=inventory['product_id'],
            y=inventory['total_stock'],
            marker_color='blue'
        ))
        fig_inventory.add_trace(go.Bar(
            name='Min Threshold',
            x=inventory['product_id'],
            y=inventory['min_threshold'],
            marker_color='red'
        ))
        fig_inventory.update_layout(
            title='Inventory Levels vs. Minimum Threshold',
            barmode='group'
        )
        st.plotly_chart(fig_inventory)
    
    with col2:
        # Risk Factor Gauge Charts
        for _, row in inventory.iterrows():
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = row['risk_factor'],
                title = {'text': f"Risk Factor - {row['product_id']}"},
                gauge = {
                    'axis': {'range': [0, 10]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 3], 'color': "green"},
                        {'range': [3, 7], 'color': "yellow"},
                        {'range': [7, 10], 'color': "red"}
                    ]
                }
            ))
            fig_gauge.update_layout(height=200)
            st.plotly_chart(fig_gauge)
    
    # Historical Analysis
    st.subheader("Historical Analysis")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Damage Trends
        damage_log = st.session_state.inventory_system.get_damage_log()
        if not damage_log.empty:
            damage_by_product = damage_log.groupby('product_id')['quantity_damaged'].sum()
            fig_damage = px.pie(
                values=damage_by_product.values,
                names=damage_by_product.index,
                title='Damage Distribution by Product'
            )
            st.plotly_chart(fig_damage)
    
    with col4:
        # Transport Delay Analysis
        delays = st.session_state.inventory_system.get_transport_delays()
        if not delays.empty:
            delays['delay_days'] = (pd.to_datetime(delays['actual_delivery'], format='%Y-%m-%d', errors='coerce') - 
                                  pd.to_datetime(delays['expected_delivery'], format='%Y-%m-%d', errors='coerce')).dt.days
            avg_delay = delays.groupby('product_id')['delay_days'].mean()
            fig_delays = px.bar(
                x=avg_delay.index,
                y=avg_delay.values,
                title='Average Transport Delays by Product (Days)',
                labels={'x': 'Product ID', 'y': 'Average Delay (Days)'}
            )
            st.plotly_chart(fig_delays)

# Scenarios Tab
with tab_scenarios:
    st.header("Run Risk Management Scenarios")
    
    if not st.session_state.scenarios_run and st.button("Run Scenarios"):
        scenarios = [
            {
                'product_id': 'LIB001',
                'inventory_level': 3500,
                'lead_time': 10,
                'news_text': "Market shows strong potential for standard lithium batteries with increasing electric vehicle adoption",
                'textual_risk': 3,
                'damage_scenario': {
                    'quantity': 75,
                    'reason': "Transportation packaging failure"
                },
                'transport_delay': {
                    'expected_delivery': datetime.now(),
                    'actual_delivery': datetime.now() + timedelta(days=3),
                    'delay_reason': "Port congestion"
                },
                'sales_volume': 350
            },
            {
                'product_id': 'LIB002',
                'inventory_level': 500,
                'lead_time': 25,
                'news_text': "High-capacity battery market facing supply chain disruptions",
                'textual_risk': 7,
                'damage_scenario': {
                    'quantity': 50,
                    'reason': "Warehouse climate control failure"
                },
                'transport_delay': {
                    'expected_delivery': datetime.now(),
                    'actual_delivery': datetime.now() + timedelta(days=5),
                    'delay_reason': "Severe weather conditions"
                },
                'sales_volume': 100
            },
            {
                'product_id': 'LIB003',
                'inventory_level': 8000,
                'lead_time': 15,
                'news_text': "EV battery module market shows moderate stability",
                'textual_risk': 2,
                'damage_scenario': {
                    'quantity': 25,
                    'reason': "Minor handling damage"
                },
                'transport_delay': {
                    'expected_delivery': datetime.now(),
                    'actual_delivery': datetime.now() + timedelta(days=1),
                    'delay_reason': "Minor routing adjustment"
                },
                'sales_volume': 250
            }
        ]

        for scenario in scenarios:
            st.write(f"\n--- Scenario for {scenario['product_id']} ---")
            
            risk_label, risk_score = st.session_state.inventory_system.predict_risk(
                inventory_level=scenario['inventory_level'],
                lead_time=scenario['lead_time'],
                news_text=scenario['news_text'],
                textual_risk=scenario['textual_risk']
            )
            st.write(f"Risk Assessment: {risk_label} (Score: {risk_score:.2f})")

            alerts = st.session_state.inventory_system.update_inventory(
                scenario['product_id'], 
                scenario['inventory_level'] if scenario['inventory_level'] > 0 else 0,
                "add"
            )
            st.write("Inventory Alerts:")
            st.write(alerts)

            st.session_state.inventory_system.log_damage(
                scenario['product_id'],
                scenario['damage_scenario']['quantity'],
                scenario['damage_scenario']['reason']
            )
            st.write(f"Logged damage: {scenario['damage_scenario']['quantity']} units due to {scenario['damage_scenario']['reason']}")

            st.session_state.inventory_system.log_transport_delay(
                scenario['product_id'],
                scenario['transport_delay']['expected_delivery'],
                scenario['transport_delay']['actual_delivery'],
                scenario['transport_delay']['delay_reason']
            )
            st.write(f"Transport Delay: {scenario['transport_delay']['delay_reason']}")

            st.session_state.inventory_system.log_sales(
                scenario['product_id'],
                scenario['sales_volume']
            )
            st.write(f"Sales Volume: {scenario['sales_volume']} units")

        st.session_state.scenarios_run = True
        st.success("All scenarios have been processed!")

# Inventory Management Tab
with tab_inventory:
    st.header("Inventory Management")
    
    col1, col2 = st.columns(2)
    with col1:
        product_id = st.selectbox("Product ID", ["LIB001", "LIB002", "LIB003"])
        quantity = st.number_input("Quantity", min_value=1)
        action = st.radio("Action", ["Add Stock", "Remove Stock"])
        
        if st.button("Update Inventory"):
            success, message = st.session_state.inventory_system.update_inventory(
                product_id, int(quantity),
                "add" if action == "Add Stock" else "remove"
            )
            st.write(message)
    
    with col2:
        st.write("Current Inventory")
        st.dataframe(st.session_state.inventory_system.get_current_inventory())

# Damage Log Tab
with tab_damage:
    st.header("Damage Log")
    
    col1, col2 = st.columns(2)
    with col1:
        product_id = st.selectbox("Product ID ", ["LIB001", "LIB002", "LIB003"])
        quantity = st.number_input("Damaged Quantity", min_value=1)
        reason = st.text_input("Damage Reason")
        
        if st.button("Log Damage"):
            st.session_state.inventory_system.log_damage(product_id, quantity, reason)
            st.success(f"Logged damage for {product_id}")
    
    with col2:
        st.write("Damage History")
        st.dataframe(st.session_state.inventory_system.get_damage_log())

# Transport Delays Tab
with tab_transport:
    st.header("Transport Delays")
    
    col1, col2 = st.columns(2)
    with col1:
        product_id = st.selectbox("Product ID  ", ["LIB001", "LIB002", "LIB003"])
        expected_date = st.date_input("Expected Delivery Date")
        actual_date = st.date_input("Actual Delivery Date")
        delay_reason = st.text_input("Delay Reason")
        
        if st.button("Log Delay"):
            st.session_state.inventory_system.log_transport_delay(
                product_id,
                expected_date,
                actual_date,
                delay_reason
            )
            st.success(f"Logged transport delay for {product_id}")
    
    with col2:
        st.write("Transport Delay History")
        st.dataframe(st.session_state.inventory_system.get_transport_delays())

# Sales Log Tab
with tab_sales:
    st.header("Sales Log")
    
    col1, col2 = st.columns(2)
    with col1:
        product_id = st.selectbox("Product ID   ", ["LIB001", "LIB002", "LIB003"])
        quantity = st.number_input("Sales Quantity", min_value=1)
        
        if st.button("Log Sale"):
            st.session_state.inventory_system.log_sales(product_id, quantity)
            st.success(f"Logged sale for {product_id}")
    
    with col2:
        st.write("Sales History")
        st.dataframe(st.session_state.inventory_system.get_sales_log())

# News Analysis Tab
with tab_news:
    st.header("News Analysis")
    
    if st.button("Fetch Latest News"):
        with st.spinner("Fetching and analyzing news..."):
            try:
                results = st.session_state.news_analyzer.run_analysis()
                if results:
                    # Display results in a dataframe
                    df = pd.DataFrame(results)
                    st.dataframe(df[["title", "source", "dateTime", "sentiment_analysis", "risk_analysis"]])
                    
                    # Add JSON download button
                    st.download_button(
                        label="Download Results as JSON",
                        data=json.dumps(results, indent=4),
                        file_name="analysis_results.json",
                        mime="application/json"
                    )
                    
                    # Calculate average sentiment score and update risk factors
                    sentiment_scores = [article['sentiment_analysis']['score'] for article in results]
                    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                    
                    # Update risk factors for each product
                    inventory = st.session_state.inventory_system.get_current_inventory()
                    for product_id in ["LIB001", "LIB002", "LIB003"]:
                        # Get current stock level
                        total_stock = inventory.loc[inventory['product_id'] == product_id, 'total_stock'].iloc[0]
                        max_capacity = inventory.loc[inventory['product_id'] == product_id, 'max_capacity'].iloc[0]
                        min_threshold = inventory.loc[inventory['product_id'] == product_id, 'min_threshold'].iloc[0]
                        
                        # Calculate stock level risk (0-1 scale)
                        stock_ratio = total_stock / max_capacity
                        if total_stock <= min_threshold:
                            stock_risk = 1.0  # Highest risk
                        elif stock_ratio < 0.3:
                            stock_risk = 0.8
                        elif stock_ratio < 0.5:
                            stock_risk = 0.5
                        else:
                            stock_risk = 0.2  # Low risk for good stock levels
                        
                        # Calculate sentiment risk (inverse of sentiment score)
                        sentiment_risk = 1 - avg_sentiment
                        
                        # Combine risks (70% stock risk, 30% sentiment risk)
                        final_risk = (stock_risk * 0.7 + sentiment_risk * 0.3) * 10
                        
                        # Ensure risk is between 1 and 10
                        final_risk = max(1, min(10, final_risk))
                        
                        # Update the risk factor in the database
                        st.session_state.inventory_system.update_risk_factor(product_id, final_risk)
                    
                    # Display updated inventory
                    st.write("Updated Inventory with Risk Factors:")
                    st.dataframe(st.session_state.inventory_system.get_current_inventory())
                    
                    st.success("News analysis completed and risk factors updated!")
                else:
                    st.error("No results returned from news analysis")
            except Exception as e:
                st.error(f"Error fetching news: {str(e)}")

# LLaMA Chat Tab
with tab_chat:
    st.header("LLaMA Chat")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get current inventory and news context
    inventory_df = st.session_state.inventory_system.get_current_inventory()
    try:
        with open("data/analysis_results.json", "r") as f:
            news_data = json.load(f)
            news_context = "\n".join([f"Article: {article['title']}\nSentiment: {article['sentiment_analysis']['label']}\n" 
                                    for article in news_data[:3]])
    except:
        news_context = "No recent news analysis available."

    # Chat input
    if prompt := st.chat_input("Ask about inventory..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get AI response with context
        try:
            context = f"""Current inventory status:\n{inventory_df.to_string()}\n\n
                         Recent news context:\n{news_context}\n\n
                         User question: {prompt}"""
            
            response = st.session_state.news_analyzer.analyze_risk_with_llama(context)
            
            # Display AI response
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {str(e)}")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun() #streamlit run "Milestone 4 (AI powered Inventory Management DashBoard)/python_scripts/streamlit_app.py"