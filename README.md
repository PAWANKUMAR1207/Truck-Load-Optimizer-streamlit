Truck Logistics Optimizer
A Streamlit-based app for optimizing multi-SKU truck planning with MongoDB integration and AI-driven efficiency suggestions.

🔑 Key Features
Multi-SKU Entry: Add/manage SKUs with quantity, volume, and weight

Truck Types: Select from customizable Small, Medium, or Large trucks

Smart Calculations: Auto-calculate trucks needed by volume/weight

Utilization Alerts: Warnings for utilization below 70%

Interactive Charts: Real-time visualizations of capacity usage

MongoDB Integration: Persistent cloud storage with MongoDB Atlas

Templates: Save/load SKU configurations for quick reuse

Analytics Dashboard: Historical trends and performance metrics

AI Suggestions: Optimize load efficiency with built-in logic

⚙️ Requirements
Python 3.11+

Recommended tools: Git, MongoDB Atlas (optional for local testing)


TO RUN THIS 

1.INSTALL DEPENDENCIES 
pip install streamlit pandas numpy plotly pymongo motor

2.MONGODB(SETUP OPTIONAL)
export MONGODB_URI="your-mongodb-connection-string"

3.Running the app
Navigate To Project Directory
cd truck-calculator

Start the app
python -m streamlit run app.py


