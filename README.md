<div align='center'>
    
![Zillow_Scraper](https://github.com/user-attachments/assets/9ff0fcf8-7b94-4cda-906d-a94eb0e5e5de)

</div>



# Overview

**The Problem**: Manually researching dozens or hundreds of properties on Zillow is time-consuming and inefficient. What takes hours of copying and pasting data can now be done in minutes.

**The Solution**: This application automates property data extraction from Zillow using a simple list of US addresses. It returns comprehensive property information including prices, status, seller details, price history, and features - all processed efficiently with multi-threading and real-time progress tracking.


<div align='center'>

<img src="https://github.com/user-attachments/assets/e351124e-4207-417d-b90a-e73ae8b48171" width="50%" alt="Overview Image">



</div>


# Who Would Benefit from This Tool:

<ul>
    <li><strong>Real Estate Investors:</strong> Quickly analyze multiple properties for investment opportunities</li>
    <li><strong>Real Estate Agents:</strong> Gather comprehensive market data for client presentations</li>
    <li><strong>Property Analysts:</strong>Conduct bulk property research and market analysis</li>
    <li><strong>Auction Companies:</strong>Extract property details for auction listings</li>
    <li><strong>Market Researchers:</strong>Analyze property trends and pricing patterns</li>
  <li><strong>Property Management Companies:</strong>Assess portfolio values and market positions</li>
</ul>

# Features

## Core Functionality
- **Batch Processing**: Process multiple addresses simultaneously from Excel files
- **Multi-threading**: Concurrent processing with configurable thread pools
- **Real-time Progress**: Live progress tracking with request counter
- **Selective Data Extraction**: Choose which data fields to extract via checkboxes

## Data Fields Available
-  **Lead Address**: Original input address
-  **Property Status**: Current listing status (For Sale, Sold, etc.)
-  **Zillow Link**: Direct link to the property listing
-  **Zestimate**: Zillow's estimated property value
-  **Seller Information**: Listed by details
-  **Price History**: Complete pricing timeline
-  **Auction Links**: Links to auction platforms if available
-  **House Features**: Detailed property specifications

## User Interface Features
- **Dark Mode Interface**: Modern, easy-on-the-eyes design
- **File Browser Integration**: Easy input/output file selection
- **Real-time Logging**: Detailed processing logs with timestamps
- **Progress Visualization**: Progress bar and completion statistics
- **Error Handling**: Robust error management with retry logic

## Technical Features
- **Batch Processing**: Groups of 5 leads processed in parallel
- **Automatic Retries**: Handles connection issues and timeouts
- **Intermediate Saves**: Prevents data loss during long processing sessions
- **Duplicate Removal**: Automatic deduplication of input addresses

# Project Background

This project was originally developed for **MSV Properties** to streamline their property research and analysis workflow. The tool was designed to handle large-scale property data extraction efficiently while maintaining data accuracy and reliability.

**Created by Karim Merchaoui**

# Installation

## Prerequisites
- Python 3.7 or higher
- ScraperAPI account and API key

## Step 1: Clone or Download
Download the project files to your local machine.

## Step 2: Install Dependencies
```bash
pip install requests beautifulsoup4 pandas customtkinter openpyxl urllib3
```

## Step 3: Configure API Key
1. Sign up for a ScraperAPI account at [scraperapi.com](https://scraperapi.com)
2. Replace `'API_KEY'` in the code with your actual ScraperAPI key:
```python
payload = {'api_key': 'YOUR_ACTUAL_API_KEY_HERE', 'url': zillow_link, 'ultra_premium': "true"}
```

## Step 4: Setup Dependencies
Ensure you have the `foratting.py` file in the same directory with the following functions:
- `format_hist()`
- `format_house_details()`
- `chunk_leads()`
- `generate_zillow_link()`

# Usage

## Step 1: Prepare Input Data
Create an Excel file (.xlsx) with US addresses in the first column. Example:
```
123 Main Street, New York, NY 10001
456 Oak Avenue, Los Angeles, CA 90210
789 Pine Road, Chicago, IL 60601
```

## Step 2: Launch Application
Run the main Python script:
```bash
python zillow_scraper.py
```

## Step 3: Configure Settings
1. **Select Input File**: Click "Browse Input" and choose your Excel file
2. **Select Output Directory**: Click "Browse Output" and choose where to save results
3. **Choose Data Fields**: Check/uncheck the data fields you want to extract:
   - Lead (always included)
   - Status
   - Zillow Link
   - Zestimate
   - Seller
   - Price History
   - Auction Link
   - House Features

## Step 4: Process Data
1. Click "Process Files" to start extraction
2. Monitor progress in real-time through:
   - Progress bar
   - Completion counter (e.g., "45/100")
   - API request counter
   - Detailed logs

### Step 5: Access Results
- Results are automatically saved to Excel files with timestamps
- Files are saved in your selected output directory
- Format: `YYYY-MM-DD_HH-MM-SS-output.xlsx`




## Output Format

The generated Excel file contains columns based on your selections:

| Lead | Status | Zillow Link | Zestimate | Seller | Price History | Auction Link | House Features |
|------|--------|-------------|-----------|---------|---------------|--------------|----------------|
| 123 Main St... | For Sale | zillow.com/... | $450,000 | John Doe Realty | 2023-01: $440K... | auction.com/... | 3 bed, 2 bath... |


![image](https://github.com/user-attachments/assets/c9fbba81-245d-420a-b199-75dab4371273)


## Performance Notes

- **Concurrent Processing**: Processes 5 leads simultaneously per batch
- **Batch Management**: Handles 9 batches concurrently for optimal performance
- **Rate Limiting**: Built-in delays to respect API limits
- **Error Recovery**: Automatic retry mechanism for failed requests
- **Memory Efficient**: Processes data in chunks to handle large datasets

## Troubleshooting

### Common Issues
- **"Property Not Found"**: Address format may be incorrect or property not listed on Zillow
- **Connection Errors**: Check internet connection and ScraperAPI service status
- **API Limit Exceeded**: Monitor API usage and upgrade plan if needed

### Tips for Best Results
- Use complete, properly formatted US addresses
- Include state abbreviations (NY, CA, TX, etc.)
- Avoid special characters in addresses
- Process smaller batches first to test configuration



