import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt

all_df = pd.read_csv('main_data.csv')

datetime_columns = ["order_approved_at"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

def number_order_per_month(df):
    monthly_df = df.resample(rule='M', on='order_approved_at').agg({"order_id": "size"})
    monthly_df.index = monthly_df.index.strftime('%B')
    monthly_df = monthly_df.reset_index()
    monthly_df.rename(columns={"order_id": "order_count"}, inplace=True)
    monthly_df = monthly_df.sort_values('order_count').drop_duplicates('order_approved_at', keep='last')
    month_mapping = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }

    monthly_df["month_numeric"] = monthly_df["order_approved_at"].map(month_mapping)
    monthly_df = monthly_df.sort_values("month_numeric")
    monthly_df = monthly_df.drop("month_numeric", axis=1)
    return monthly_df

def customer_spend_df(df):
    sum_spend_df = df.resample(rule='M', on='order_approved_at').agg({"price": "sum"})
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={"price": "total_spend"}, inplace=True)
    sum_spend_df['order_approved_at'] = sum_spend_df['order_approved_at'].dt.strftime('%B') 
    sum_spend_df = sum_spend_df.sort_values('total_spend').drop_duplicates('order_approved_at', keep='last')
    custom_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    sum_spend_df['month_cat'] = pd.Categorical(sum_spend_df['order_approved_at'], categories=custom_order, ordered=True)

    sorted_df = sum_spend_df.sort_values(by='month_cat')

    sorted_df = sorted_df.drop(columns=['month_cat'])
    return sorted_df


def create_by_product_df(df):
    product_id_counts = df.groupby('product_category_name_english')['product_id'].count().reset_index()
    sorted_df = product_id_counts.sort_values(by='product_id', ascending=False)
    return sorted_df

def create_rfm(df):
    now=dt.datetime(2018,10,20)

    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    recency = (now - df.groupby('customer_id')['order_purchase_timestamp'].max()).dt.days
    frequency = df.groupby('customer_id')['order_id'].count()
    monetary = df.groupby('customer_id')['price'].sum()

    rfm = pd.DataFrame({
        'customer_id': recency.index,
        'Recency': recency.values,
        'Frequency': frequency.values,
        'Monetary': monetary.values
    })

    col_list = ['customer_id','Recency','Frequency','Monetary']
    rfm.columns = col_list
    return rfm

daily_orders_df=number_order_per_month(all_df)
most_and_least_products_df=create_by_product_df(all_df)
customer_spend_df=customer_spend_df(all_df)
rfm=create_rfm(all_df)

st.header('Proyek Analisis Data')

st.subheader('Pembelian Bulanan')
col1, col2 = st.columns(2)

with col1:
    high_order_num = daily_orders_df['order_count'].max()
    high_order_month=daily_orders_df[daily_orders_df['order_count'] == daily_orders_df['order_count'].max()]['order_approved_at'].values[0]
    st.markdown(f"Pembelian tertinggi di bulan {high_order_month} : **{high_order_num}**")

with col2:
    low_order = daily_orders_df['order_count'].min()
    low_order_month=daily_orders_df[daily_orders_df['order_count'] == daily_orders_df['order_count'].min()]['order_approved_at'].values[0]
    st.markdown(f"Pembelian terendah di bulan {low_order_month} : **{low_order}**")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#FF9999",
)
plt.xticks(rotation=45)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)



st.subheader('Pembelian Pelanggan')
col1, col2 = st.columns(2)

with col1:
    total_spend=customer_spend_df['total_spend'].sum()
    formatted_total_spend = "%.2f" % total_spend
    st.markdown(f"Total Pembelian : **{formatted_total_spend}**")

with col2:
    avg_spend=customer_spend_df['total_spend'].mean()
    formatted_avg_spend = "%.2f" % avg_spend
    st.markdown(f"Rata-Rata Pembelian : **{formatted_avg_spend}**")

plt.figure(figsize=(16, 8))
min_total_spend = customer_spend_df['total_spend'].min()
max_total_spend = customer_spend_df['total_spend'].max()

plt.axhline(y=max_total_spend, color='orange', linestyle='-', linewidth=0.5, label=f'Max ({max_total_spend:.2f})')
plt.axhline(y=min_total_spend, color='blue', linestyle='-', linewidth=0.5, label=f'Min ({min_total_spend:.2f})')
sns.barplot(
    x='order_approved_at',
    y='total_spend',
    data=customer_spend_df,
    linestyle='-',
    color="#FF9999",
    
)
plt.xlabel('')
plt.ylabel('Total Pembelian')
plt.xticks(fontsize=10, rotation=25)
plt.yticks(fontsize=10)
plt.legend()
st.pyplot(plt)



st.subheader("Produk Dengan Pembelian Terbanyak dan Tersedikit")
col1, col2 = st.columns(2)

with col1:
    highest_product_sold=most_and_least_products_df['product_id'].max()
    st.markdown(f"Pembelian Terbanyak : **{highest_product_sold}**")

with col2:
    lowest_product_sold=most_and_least_products_df['product_id'].min()
    st.markdown(f"Pembelian Tersedikit : **{lowest_product_sold}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))

colors = ["#FF9999", "#B2B2B2", "#B2B2B2", "#B2B2B2", "#B2B2B2"]

sns.barplot(
    x="product_id", 
    y="product_category_name_english", 
    data=most_and_least_products_df.head(5), 
    palette=colors, 
    ax=ax[0],
    )
ax[0].set_ylabel('')
ax[0].set_xlabel('')
ax[0].set_title("Produk yang paling banyak dibeli", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=15)

sns.barplot(
    x="product_id", 
    y="product_category_name_english", 
    data=most_and_least_products_df.sort_values(by="product_id", ascending=True).head(5), 
    palette=colors, 
    ax=ax[1],)
ax[1].set_ylabel('')
ax[1].set_xlabel('')
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk yang paling sedikit dibeli", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

plt.suptitle("Penjualan terbanyak dan tersedikit", fontsize=20)
st.pyplot(fig)



st.subheader("Nilai RFM")


colors = ["#FF9999", "#B2B2B2", "#B2B2B2", "#B2B2B2", "#B2B2B2"]



rfm1, rfm2, rfm3 = st.tabs(["Recency", "Frequency", "Monetary"])

with rfm1:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Recency", 
        x="customer_id", 
        data=rfm.sort_values(by="Recency", ascending=True).head(5), 
        palette=colors,
        
        )
    plt.title("Recency (Hari)", loc="center", fontsize=18)
    plt.ylabel('')
    plt.xlabel("pelanggan")
    plt.tick_params(axis ='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)

with rfm2:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Frequency", 
        x="customer_id", 
        data=rfm.sort_values(by="Frequency", ascending=False).head(5), 
        palette=colors,
        
        )
    plt.ylabel('')
    plt.xlabel("pelanggan")
    plt.title("Frequency", loc="center", fontsize=18)
    plt.tick_params(axis ='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)

with rfm3:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Monetary", 
        x="customer_id", 
        data=rfm.sort_values(by="Monetary", ascending=False).head(5), 
        palette=colors,
        )
    plt.ylabel('')
    plt.xlabel("pelanggan")
    plt.title("Monetary", loc="center", fontsize=18)
    plt.tick_params(axis ='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)
