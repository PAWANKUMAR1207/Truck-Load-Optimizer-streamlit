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

Use the screenshots to see how to strucuture the file in the computer 
Any queries i can guide just send me a mail cheerfulpawan@gmail.com 
























 Role of AI in This Project
This project integrates AI-powered logic to enhance decision-making and provide actionable insights beyond basic calculations:

1. Smart Utilization Feedback
The system automatically analyzes volume and weight utilization and identifies the limiting factor (volume or weight).

If truck utilization is low (e.g. <70%), the app provides AI-generated suggestions to improve efficiency, such as:

Reducing or batching low-volume SKUs

Reorganizing shipments by destination

Upgrading/downgrading truck size

These suggestions are generated using a custom logic engine simulating basic AI heuristics for logistics optimization.

2. Efficiency Rating System (AI Enhancement)
The app gives a qualitative rating (Excellent, Good, Moderate, Poor) based on the calculated utilization percentages.

These labels help users quickly interpret performance without diving into raw numbers — an intuitive, user-friendly AI enhancement.

3. Template Intelligence
Users can save SKU templates and reuse them. In future iterations, AI can analyze past templates to auto-suggest best combinations for similar destinations or volume patterns.

4. Scalable AI Vision
The architecture is designed to support more advanced AI/ML features in future, such as:

Predictive truck allocation based on SKU patterns

Route optimization using real-time data

Reinforcement learning for optimal packing strategies




Use the screenshots to see how to strucuture the file in the computer 
Any queries i can guide just send me a mail cheerfulpawan@gmail.com 

truck-calculator/
├── app.py                  # Main Streamlit app
├── utils/                  # Core modules
│   ├── calculations.py     # SKU & truck logic
│   ├── database.py         # MongoDB interface
│   ├── optimization.py     # Efficiency suggestions
│   └── visualizations.py   # Graph generation
└── .streamlit/config.toml  # Streamlit config
