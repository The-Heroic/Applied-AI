import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_report_graph():
    try:
        # 1. Load the data
        df = pd.read_csv('mood_log.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 2. Set up the visual style
        plt.style.use('seaborn-v0_8-muted')
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 3. Plot the data
        ax.plot(df['Date'], df['Score'], marker='o', linestyle='-', color='#2e7d32', linewidth=2, label='Mood Score')
        ax.fill_between(df['Date'], df['Score'], alpha=0.2, color='#81c784')

        # 4. Formatting
        ax.set_title('Aria User Well-being Trend', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Mood Score (1-10)', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylim(0, 11)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Format dates on X-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        plt.xticks(rotation=45)
        
        # 5. Save and Show
        plt.tight_layout()
        plt.savefig('mood_report_chart.png', dpi=300)
        print("Success! 'mood_report_chart.png' has been saved to your folder.")
        plt.show()

    except FileNotFoundError:
        print("Error: 'mood_log.csv' not found. Please log some moods in the Aria app first!")

if __name__ == "__main__":
    generate_report_graph()