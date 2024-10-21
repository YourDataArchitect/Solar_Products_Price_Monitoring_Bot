# Solar Products Price Monitoring Bot With VPN 🔆
<div style="text-align: center;">
    <img src="https://blog.feniceenergy.com/wp-content/uploads/2024/05/how-is-solar-energy-useful-to-us.jpg" alt="A sample image" width="400" height="300">
</div>

🔸 Overview : 
-  This project is a web scraping bot that tracks solar energy product prices across 18 e-commerce websites. It performs daily updates by extracting prices, monitoring new products, and storing data in Google Sheets and a MySQL database. The bot operates in a Docker container with Surfshark VPN for secure scraping, ensuring easy deployment and management across different systems.

## 🔸 Features
-  **Price Extraction**: Scrapes prices from 18 websites selling solar products.
-  **Google Sheets Integration**: Updates a Google Sheet with the latest prices for easy access.
-  **Database Storage**: Stores product and pricing data for historical tracking.
-  **New Product Monitoring**: Detects and logs newly listed products.
-  **VPN Integration**: Uses Surfshark VPN to rotate IP addresses and avoid blocking.
-  **Docker Containerization**: Ensures the bot runs consistently across platforms.
-  **Email Notifications**: Sends alerts to the user if any errors occur during the scraping process.

## 🔸 Technology Stack
-  **Python**: Used for web scraping and automation.
-  **SQL**: For creating data queries.
-  **Scrapy**: Handles scraping across multiple websites.
-  **Selenium**: Automates browsing of target pages.
-  **Pandas**: Reformats and cleans the data.
-  **Google Sheets API**: Updates Google Sheets with the latest data.
-  **MySQL**: Stores the scraped data.
-  **Surfshark VPN**: Provides IP rotation for secure and anonymous scraping.
-  **Docker**: Packages and deploys the bot in a consistent environment.

## 🔸 How It Works
-  The bot scrapes prices from 18 websites at regular intervals.
-  It detects new products and updates their details.
-  Prices are updated in a Google Sheet and stored in a database for tracking.
-  The bot runs in a Docker container for consistent performance.
-  To avoid blocks, it uses Surfshark VPN for IP rotation.

## 🔸 Future Improvements
-  Add more websites for price monitoring.
-  Include data visualization for price trends.
-  Optimize VPN for smoother scraping.
