# filename: plot_seattle_weather.py
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

# Load the data from the URL
data = pd.read_csv('https://raw.githubusercontent.com/vega/vega/main/docs/data/seattle-weather.csv')

# Convert the 'date' column to DateTime type
data['date'] = pd.to_datetime(data['date'])

# Calculate the rolling average for smoother lines
data['temp_max_smoothed'] = data['temp_max'].rolling(30).mean()
data['temp_min_smoothed'] = data['temp_min'].rolling(30).mean()

# Create the figure and subplots
fig, ax = plt.subplots(figsize=(12, 8))

# Plot temperature high and low with smoothed data against the date
ax.plot(data['date'], data['temp_max_smoothed'], color='orange', label='Temperature High')
ax.plot(data['date'], data['temp_min_smoothed'], color='blue', label='Temperature Low')

# Format the x-axis to display the dates more clearly
date_format = mdates.DateFormatter('%b %Y')
ax.xaxis.set_major_formatter(date_format)

ax.xaxis.set_tick_params(rotation=45)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # set ticks to be every 3 months

# Add grid lines
ax.grid(True)

# Adding labels and title with increased size
ax.set_xlabel('Date', fontsize=14)
ax.set_ylabel('Temperature (°C)', fontsize=14)
ax.set_title('Temperature trends in Seattle', fontsize=16)

# Add the legend at the best location
plt.legend(loc='upper right', fontsize=10)

# Save the figure to 'result.jpg'
plt.savefig('result.jpg')

print("Figure has been saved successfully as 'result.jpg'")