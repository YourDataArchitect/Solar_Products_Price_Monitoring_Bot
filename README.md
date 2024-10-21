# Solar Products Price Monitoring Bot With VPN 🔆
<img src="https://blog.feniceenergy.com/wp-content/uploads/2024/05/how-is-solar-energy-useful-to-us.jpg" alt="A sample image" width="400" height="300">
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solar Products Price Monitoring Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }
        h2 {
            color: #0073e6;
        }
        .section-title {
            font-size: 1.5em;
            color: #ff6f61;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        ul li {
            padding: 5px 0;
        }
        ul li::before {
            content: "🔹";
            margin-right: 10px;
            color: #0073e6;
        }
        .feature-section, .stack-section {
            background-color: #fff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>

    <h2 class="section-title">#Overview</h2>
    <p>This project is a web scraping bot that tracks solar energy product prices across 18 e-commerce websites. It performs daily updates by extracting prices, monitoring new products, and storing data in Google Sheets and a MySQL database. The bot operates in a Docker container with Surfshark VPN for secure scraping, ensuring easy deployment and management across different systems.</p>

    <h2 class="section-title">#Features</h2>
    <div class="feature-section">
        <ul>
            <li>Price Extraction: Scrapes prices from 18 websites selling solar products.</li>
            <li>Google Sheets Integration: Updates a Google Sheet with the latest prices for easy access.</li>
            <li>Database Storage: Stores product and pricing data for historical tracking.</li>
            <li>New Product Monitoring: Detects and logs newly listed products.</li>
            <li>VPN Integration: Uses Surfshark VPN to rotate IP addresses and avoid blocking.</li>
            <li>Docker Containerization: Ensures the bot runs consistently across platforms.</li>
            <li>Email Notifications: Sends alerts to the user if any errors occur during the scraping process.</li>
        </ul>
    </div>

    <h2 class="section-title">#Technology Stack</h2>
    <div class="stack-section">
        <ul>
            <li>Python: Used for web scraping and automation.</li>
            <li>SQL: For creating data queries.</li>
            <li>Scrapy: Handles scraping across multiple websites.</li>
            <li>Selenium: Automates browsing of target pages.</li>
            <li>Pandas: Reformats and cleans the data.</li>
            <li>Google Sheets API: Updates Google Sheets with the latest data.</li>
            <li>MySQL: Stores the scraped data.</li>
            <li>Surfshark VPN: Provides IP rotation for secure and anonymous scraping.</li>
            <li>Docker: Packages and deploys the bot in a consistent environment.</li>
        </ul>
    </div>

    <h2 class="section-title">#How It Works</h2>
    <div class="feature-section">
        <ul>
            <li>The bot scrapes prices from 18 websites at regular intervals.</li>
            <li>It detects new products and updates their details.</li>
            <li>Prices are updated in a Google Sheet and stored in a database for tracking.</li>
            <li>The bot runs in a Docker container for consistent performance.</li>
            <li>To avoid blocks, it uses Surfshark VPN for IP rotation.</li>
        </ul>
    </div>

    <h2 class="section-title">#Future Improvements</h2>
    <div class="stack-section">
        <ul>
            <li>Add more websites for price monitoring.</li>
            <li>Include data visualization for price trends.</li>
            <li>Optimize VPN for smoother scraping.</li>
        </ul>
    </div>

</body>
</html>
