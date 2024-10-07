import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
import datetime as dt

# Load dataset (sesuaikan path dengan data yang benar)
all_data = pd.read_csv('all_data.csv')

# Header
st.title("E-Commerce Dashboard")

# Menambahkan informasi pribadi
st.write("**Tugas Proyek Akhir Analisis Data**")
st.write("**Nama**: Ariqah Maulia Listiani")
st.write("**Email**: m002b4kx0652@bangkit.academy")
st.write("**ID Dicoding**: armalist")

# Menampilkan daftar menu pada tampilan awal
st.markdown('<p style="color:red; font-size:20px;">(Select the analysis display menu first)</p>', unsafe_allow_html=True)

# Sidebar untuk pilihan analisis
st.sidebar.header("Analysis Options Menu")
analysis_type = st.sidebar.selectbox("Select the analysis you want to display:", 
                                     ['Choose..', 'Monthly Order Trends', 'Delivery Time vs Satisfaction', 'Best Selling Product Categories', 'RFM Analysis', 'Customer Review'])

# Fungsi untuk menampilkan tren pesanan bulanan
def plot_order_trend(all_data):
    # Convert the 'order_purchase_timestamp_x' to datetime
    all_data['order_purchase_timestamp_x'] = pd.to_datetime(all_data['order_purchase_timestamp_x'])

    # Extract year and month for grouping
    all_data['year_month'] = all_data['order_purchase_timestamp_x'].dt.to_period('M')

    # Group by 'year_month' and 'customer_state' to count the number of orders
    monthly_orders = all_data.groupby(['year_month', 'customer_state']).size().reset_index(name='order_count')

    # Pivot the data to create a matrix of 'year_month' (rows) and 'customer_state' (columns) with 'order_count' as values
    pivot_table = monthly_orders.pivot(index='year_month', columns='customer_state', values='order_count').fillna(0)

    plt.figure(figsize=(14,8))
    pivot_table.plot(kind='line', ax=plt.gca(), cmap='tab20')
    #Customize plot
    plt.title('Trends in the Number of Monthly Orders by Geographical Region', fontsize=16)
    plt.xlabel('Month-Year', fontsize=12)
    plt.ylabel('Number of Orders', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title="Region (State)", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
    plt.tight_layout()
    st.pyplot(plt)

# Fungsi untuk hubungan antara waktu pengiriman dan kepuasan pelanggan
def plot_delivery_time_vs_satisfaction(all_data):
    all_data['order_purchase_timestamp_x'] = pd.to_datetime(all_data['order_purchase_timestamp_x'])
    all_data['order_delivered_customer_date_x'] = pd.to_datetime(all_data['order_delivered_customer_date_x'])

    # Calculate delivery time in days
    all_data['delivery_time_days'] = (all_data['order_delivered_customer_date_x'] - all_data['order_purchase_timestamp_x']).dt.days

    # Filter the necessary columns for analysis and remove NaN values
    delivery_review_data = all_data[['delivery_time_days', 'review_score']].dropna()

    # Group by 'delivery_time_days' to calculate the average review score for each day
    average_review_data = delivery_review_data.groupby('delivery_time_days').agg({'review_score': 'mean'}).reset_index()

    # Create a regression plot to show the relationship between delivery time and average review score
    plt.figure(figsize=(10, 6))
    sns.regplot(x='delivery_time_days', y='review_score', data=average_review_data, scatter_kws={'alpha':0.5}, line_kws={"color": "red"})

    # Add title and labels
    plt.title('The Relationship between Delivery Time and Average Customer Satisfaction', fontsize=16)
    plt.xlabel('Delivery Time (Days)', fontsize=12)
    plt.ylabel('Average Review Score', fontsize=12)

    # Show plot
    plt.tight_layout()
    st.pyplot(plt)

# Fungsi untuk menampilkan kategori produk terlaris dalam 6 bulan terakhir
def plot_top_selling_category(all_data):
    # Convert 'order_purchase_timestamp_x' to datetime for filtering
    all_data['order_purchase_timestamp_x'] = pd.to_datetime(all_data['order_purchase_timestamp_x'])

    # Filter data for the last 6 months
    last_6_months = all_data[all_data['order_purchase_timestamp_x'] >= (all_data['order_purchase_timestamp_x'].max() - pd.DateOffset(months=6))]

    # Group by 'product_category_name' and calculate the total sales (sum of price)
    sales_by_category = last_6_months.groupby('product_category_name')['price'].sum().reset_index()

    # Sort categories by total sales in descending order
    top_sales_categories = sales_by_category.sort_values(by='price', ascending=False).head(10)  # Show top 10 categories

    # Create a bar plot for the top-selling product categories
    plt.figure(figsize=(10, 6))
    plt.barh(top_sales_categories['product_category_name'], top_sales_categories['price'], color='skyblue')
    plt.xlabel('Total Sales (in currency)', fontsize=12)
    plt.ylabel('Product Category', fontsize=12)
    plt.title('Top 10 Sales Product Categories in the Last 6 Months', fontsize=16)
    plt.gca().invert_yaxis()  # Invert the y-axis to show the highest value on top
    plt.tight_layout()

    plt.tight_layout()
    st.pyplot(plt)

# Fungsi untuk melakukan RFM Analysis
def rfm_analysis(all_data):
    # Convert 'order_purchase_timestamp_x' to datetime
    all_data['order_purchase_timestamp_x'] = pd.to_datetime(all_data['order_purchase_timestamp_x'])

    # Define today's date as the latest date in the dataset for recency calculation
    today_date = all_data['order_purchase_timestamp_x'].max() + pd.DateOffset(days=1)

    # Calculate RFM metrics
    rfm = all_data.groupby('customer_id_x').agg({
        'order_purchase_timestamp_x': lambda x: (today_date - x.max()).days,  # Recency
        'order_id': 'count',  # Frequency
        'price': 'sum'  # Monetary
    }).rename(columns={
        'order_purchase_timestamp_x': 'Recency',
        'order_id': 'Frequency',
        'price': 'Monetary'
    }).reset_index()

    # Assign RFM scores
    rfm['R_score'] = pd.qcut(rfm['Recency'], 5, labels=False) + 1  # Higher scores for lower recency
    rfm['F_score'] = pd.qcut(rfm['Frequency'], 5, labels=False, duplicates='drop') + 1
    rfm['M_score'] = pd.qcut(rfm['Monetary'], 5, labels=False, duplicates='drop') + 1

    # Create a total score for segmentation
    rfm['RFM_Score'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str) + rfm['M_score'].astype(str)

    # Analyze RFM segments
    rfm['Segment'] = 'Low Value'
    rfm.loc[(rfm['R_score'] >= 4) & (rfm['F_score'] >= 4) & (rfm['M_score'] >= 4), 'Segment'] = 'High Value'
    rfm.loc[(rfm['R_score'] <= 2) & (rfm['F_score'] <= 2) & (rfm['M_score'] <= 2), 'Segment'] = 'Churn'
    rfm.loc[(rfm['R_score'] >= 3) & (rfm['F_score'] >= 3), 'Segment'] = 'Mid Value'

    # Visualize the segments
    plt.figure(figsize=(10, 6))
    sns.countplot(data=rfm, x='Segment', palette='viridis')
    plt.title('Customer Segments Based on RFM Analysis', fontsize=16)
    plt.xlabel('Segment', fontsize=12)
    plt.ylabel('Number of Customers', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

def customer_review(all_data):
    # Check the relevant columns and clean the data
    reviews_data = all_data[['review_score', 'review_comment_message']].dropna()

    # Function to get sentiment
    def get_sentiment(review):
        analysis = TextBlob(review)
        # Classify as positive, negative, or neutral
        if analysis.sentiment.polarity > 0:
            return 'Positive'
        elif analysis.sentiment.polarity < 0:
            return 'Negative'
        else:
            return 'Neutral'

    # Apply sentiment analysis
    reviews_data['sentiment'] = reviews_data['review_comment_message'].apply(get_sentiment)

    # Count sentiment categories
    sentiment_counts = reviews_data['sentiment'].value_counts()

    # Create a bar plot for sentiment distribution
    plt.figure(figsize=(8, 5))
    sentiment_counts.plot(kind='bar', color=['green', 'red', 'blue'])
    plt.title('Customer Review Sentiment Analysis', fontsize=16)
    plt.xlabel('Sentiment', fontsize=12)
    plt.ylabel('Number of Reviews', fontsize=12)
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(plt)
 
# Kondisi untuk memilih visualisasi berdasarkan pilihan pengguna
if analysis_type == 'Monthly Order Trends':
    st.subheader("Trends in the Number of Monthly Orders in the Last Year in Various Geographical Regions")
    plot_order_trend(all_data)

elif analysis_type == 'Delivery Time vs Satisfaction':
    st.subheader("How is the relationship between delivery time and customer satisfaction in order reviews?")
    plot_delivery_time_vs_satisfaction(all_data)

elif analysis_type == 'Best Selling Product Categories':
    st.subheader("Most Sales Product Categories in the Last 6 Months")
    plot_top_selling_category(all_data)

elif analysis_type == 'RFM Analysis':
    st.subheader("RFM Analysis - Customer Segments")
    rfm_analysis(all_data)

elif analysis_type == 'Customer Review':
    st.subheader("Customer Review Sentiment Analysis")
    customer_review(all_data)