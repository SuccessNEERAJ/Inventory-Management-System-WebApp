# Supply Chain Risk and Inventory Management Dashboard

## Project Overview
This milestone integrates all previous milestones into a comprehensive supply chain risk management system with a modern web interface built using Streamlit. The system provides real-time monitoring, risk assessment, and intelligent decision support for managing lithium-ion battery supply chains.

## Features

### 1. Real-Time Alerts & Analytics Dashboard
- **Live Monitoring**: Real-time tracking of inventory levels, risk factors, and supply chain events
- **Email Notifications**: Automated alerts for:
  - Low stock conditions (when inventory falls below minimum threshold)
  - High risk situations (when risk factor exceeds 7)
- **Visual Analytics**:
  - Interactive bar charts comparing current stock vs. minimum thresholds
  - Risk factor gauge charts with color-coded risk levels
  - Historical damage distribution pie charts
  - Transport delay analysis graphs

### 2. Inventory Management
- Track multiple battery products (LIB001, LIB002, LIB003)
- Real-time stock updates
- Minimum threshold monitoring
- Maximum capacity management
- Automated risk factor calculations

### 3. Risk Assessment System
- **Multi-factor Risk Analysis**:
  - Stock level risk (70% weight)
  - News sentiment risk (30% weight)
- **Risk Calculation Factors**:
  - Current stock levels relative to capacity
  - Minimum threshold violations
  - Market sentiment from news analysis
- **Risk Visualization**: Color-coded gauge charts (Green: 0-3, Yellow: 3-7, Red: 7-10)

### 4. News Analysis and Sentiment Tracking
- Real-time news fetching and analysis
- Sentiment analysis of news articles
- Risk analysis using LLaMA model
- Downloadable JSON reports
- Automatic risk factor updates based on news sentiment

### 5. Comprehensive Logging System
- **Damage Log**: Track product damages with reasons
- **Transport Delays**: Monitor shipping delays and reasons
- **Sales Log**: Record and track sales transactions
- Historical data visualization for all logs

### 6. AI-Powered Chat Interface
- Interactive chat with LLaMA model
- Context-aware responses incorporating:
  - Current inventory status
  - Recent news analysis
  - Historical data
- Natural language queries about inventory and risks

## Technical Architecture

### Components
1. **Frontend**: Streamlit web interface
2. **Backend Services**:
   - InventorySystem: SQLite database management
   - NewsAnalyzer: News fetching and analysis
   - LLaMA Integration: AI-powered analysis and chat

### Database Schema
- **Inventory Table**: Product details and current stock
- **Damage Log**: Damage incidents and quantities
- **Transport Delays**: Shipping delay tracking
- **Sales Log**: Sales transactions and status

### External APIs and Models
- Event Registry API: News fetching
- Groq API: LLaMA model integration
- SMTP: Email notifications
- Plotly: Interactive visualizations

## Installation and Setup

### Prerequisites
```bash
pip install streamlit pandas plotly groq eventregistry transformers textblob
```

### Configuration
1. Email Setup:
   ```python
   EMAIL_CONFIG = {
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "sender_email": "your-email@gmail.com",
       "sender_password": "your-app-password",
       "recipient_email": "recipient@email.com"
   }
   ```
2. API Keys:
   - Set up Groq API key
   - Configure Event Registry API key

### Running the Application
```bash
streamlit run Milestone_4/python_scripts/streamlit_app.py
```

## Usage Guide

### 1. Initial Setup
1. Run the application
2. Navigate to "Run Scenarios" tab
3. Click "Run Scenarios" to initialize test data

### 2. Monitoring Inventory
1. Use "Inventory Management" tab
2. Add or remove stock
3. Monitor real-time updates

### 3. Risk Assessment
1. Go to "News Analysis" tab
2. Click "Fetch Latest News"
3. Review risk updates in "Alerts & Analytics"

### 4. Managing Alerts
1. Monitor "Alerts & Analytics" dashboard
2. Check email notifications
3. Review risk gauges and charts

### 5. Using AI Chat
1. Navigate to "LLaMA Chat" tab
2. Ask questions about inventory or risks
3. Review AI-generated insights

## Best Practices and Recommendations

### Inventory Management
- Regularly monitor stock levels
- Keep stock above minimum thresholds
- Review risk factors daily

### Risk Monitoring
- Check news analysis regularly
- Review alerts promptly
- Monitor email notifications

### System Maintenance
- Regular database backups
- API key rotation
- Log review and cleanup

## Troubleshooting

### Common Issues
1. Email Notifications:
   - Verify App Password setup
   - Check SMTP configuration
   - Confirm email addresses

2. News Analysis:
   - API key validation
   - Internet connectivity
   - Rate limiting considerations

3. Database:
   - File permissions
   - Disk space
   - Connection handling

## Future Enhancements
1. Machine Learning Integration:
   - Predictive analytics
   - Automated risk mitigation
   - Pattern recognition

2. Extended Features:
   - Supplier management
   - Cost analysis
   - Automated ordering

3. UI/UX Improvements:
   - Mobile responsiveness
   - Custom dashboards
   - Advanced visualizations

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License
Neeraj Jaiswal

## Acknowledgments
- Streamlit for the web framework
- LLaMA for AI capabilities
- Event Registry for news data 