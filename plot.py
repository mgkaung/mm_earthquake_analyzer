import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime

# API parameters [[0]]
url = "https://mmeq.akze.me/api/myanmar-quakes"
params = {
    "from": "2025-03-27",
    "to": "2025-04-10"
}

try:
    # Fetch and validate data [[6]]
    response = requests.get(url, params=params)
    response.raise_for_status()
    api_response = response.json()
    api_data = api_response.get('earthquakes', [])
    
    if not api_data:
        print("No earthquake data found for this period [[9]]")
        
except requests.exceptions.RequestException as e:
    print(f"Network error: {str(e)} [[6]]")
    api_data = []

if api_data:
    try:
        # Process data [[4]]
        df = pd.DataFrame(api_data)
        required_fields = ['time', 'mag']
        
        if not all(field in df.columns for field in required_fields):
            raise ValueError("Missing required fields in API response [[4]]")
            
        # Convert timestamps and create full date range [[3]]
        df['datetime'] = pd.to_datetime(df['time'])
        df['date'] = df['datetime'].dt.date
        
        date_range = pd.date_range(
            start=params['from'],
            end=params['to'],
            freq='D'
        ).date
        
        # Aggregate and reindex [[3]]
        frequency = df.groupby('date').size().reindex(date_range, fill_value=0)
        frequency = frequency.reset_index(name='count')
        frequency.columns = ['date', 'count']

        # Calculate trend line [[5]][[8]]
        x_num = mdates.date2num(frequency['date'])
        z = np.polyfit(x_num, frequency['count'], 1)
        p = np.poly1d(z)
        trend_equation = f'y = {z[0]:.2f}x + {z[1]:.2f}'
        
        # Create visualization [[1]]
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(frequency['date'], frequency['count'], 
                marker='o', linestyle='-', color='blue',
                linewidth=2, markersize=8, markerfacecolor='red',
                label='Daily Count')
        
        # Add trend line [[5]]
        x_trend = np.linspace(x_num.min(), x_num.max(), 100)
        ax.plot(mdates.num2date(x_trend), p(x_trend), 
                linestyle='--', color='green', 
                linewidth=2, label='Trend Line')
        
        # Formatting [[1]][[6]]
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.xticks(rotation=45, ha='right')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add labels and legend [[1]]
        for x, y in zip(frequency['date'], frequency['count']):
            if y > 0:
                ax.text(x, y+0.2, str(y), ha='center')
        
        ax.set_title('Myanmar Earthquake Frequency (Mar 27 - April 10, 2025)\n'
                     f'Total Events: {len(df)}', 
                     fontsize=14, pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Earthquake Count', fontsize=12)
        ax.legend(loc='upper left')
        
        plt.tight_layout()
        plt.show()

        # Generate analysis report [[8]][[9]]
        print("\n--- Earthquake Trend Analysis Report ---")
        print(f"Date Range: March 28, 2025 to April 7, 2025")
        print(f"Total Events: {len(df)}")
        print(f"Trend Line Equation: {trend_equation}")
        
        if z[0] > 0.1:
            print("Trend: Significant increasing frequency")
        elif z[0] > 0:
            print("Trend: Slight increasing frequency")
        elif z[0] < -0.1:
            print("Trend: Significant decreasing frequency")
        elif z[0] < 0:
            print("Trend: Slight decreasing frequency")
        else:
            print("Trend: Stable activity")
            
        print(f"\nData source: Myanmar Earthquake API [[7]]")

    except Exception as e:
        print(f"Data processing error: {str(e)} [[4]]")
else:
    print("No earthquake data available for this period [[9]]")