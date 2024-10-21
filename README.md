# Solar Products Price Monitoring Bot With VPN 🔆
<img src="https://blog.feniceenergy.com/wp-content/uploads/2024/05/how-is-solar-energy-useful-to-us.jpg" alt="A sample image" width="400" height="300">

🔸Overview
This project is a web scraping bot that tracks prices for solar energy products across 18 websites. It automatically updates daily by extracting prices, monitoring new products, and storing the data in Google Sheets and a database. The bot runs in a Docker container, making it easy to deploy and manage on different systems.

🔸Features
Price Extraction: Scrapes prices from 14 websites selling solar products.
Google Sheets Integration: Updates a Google Sheet with the latest prices for easy access.
Database Storage: Stores product and pricing data for historical tracking.
New Product Monitoring: Detects and logs newly listed products.
VPN Integration: Uses Surfshark VPN to rotate IP addresses and avoid blocking.
Docker Containerization: Ensures the bot runs consistently across platforms.

🔸Technology Stack
Python for web scraping and automation.
Scrapy for handling multiple website scrapes.
Google Sheets API for updating the sheet.
PostgreSQL/MySQL for storing scraped data.
Surfshark VPN for IP rotation.
Docker for packaging and deployment.

🔸How It Works
The bot scrapes prices from 14 websites at regular intervals.
It detects new products and updates their details.
Prices are updated in a Google Sheet and stored in a database for tracking.
The bot runs in a Docker container for consistent performance.
To avoid blocks, it uses Surfshark VPN for IP rotation.
Future Improvements
Add more websites for price monitoring.
Include data visualization for price trends.
Optimize VPN for smoother scraping.
