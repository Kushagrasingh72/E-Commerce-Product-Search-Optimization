import streamlit as st
import pandas as pd
import time
import random
import re

st.set_page_config(page_title='E-Commerce Search Lab', page_icon='🛒', layout='wide')

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('products.csv')
    except FileNotFoundError:
        random.seed(10)
        names = ['Wireless Headphones','Smart Watch','Gaming Mouse','Mechanical Keyboard','Bluetooth Speaker','Laptop Stand','USB Hub','Power Bank','Running Shoes','Backpack','Smartphone','Monitor','Webcam','SSD Drive','Tablet']
        categories = ['Electronics','Accessories','Gaming','Fashion']
        rows=[]
        for i in range(1,301):
            name=random.choice(names)
            rows.append({'Product_ID':i,'Product_Name':name,'Category':random.choice(categories),'Price':random.randint(499,69999),'Rating':round(random.uniform(2.8,5.0),1),'Reviews':random.randint(10,12000),'Brand':random.choice(['NovaTech','SoundMax','ProGear','TechNova','UrbanX','PixelPro'])})
        df=pd.DataFrame(rows)
        df.to_csv('products.csv', index=False)
    return df

df=load_data()


def linear_search(data, query):
    q=query.lower()
    return data[data['Product_Name'].str.lower().str.contains(q, na=False) | data['Category'].str.lower().str.contains(q, na=False) | data['Brand'].str.lower().str.contains(q, na=False)]

def binary_price_search(data, target):
    arr=sorted(data['Price'].tolist())
    low, high=0, len(arr)-1
    while low<=high:
        mid=(low+high)//2
        if arr[mid]==target: return True
        if arr[mid]<target: low=mid+1
        else: high=mid-1
    return False


st.markdown('''<style>
.block-container{padding-top:1.5rem}
[data-testid="stMetric"]{background:#111827;padding:16px;border-radius:14px;border:1px solid #273449}
.product{padding:16px;border:1px solid #334155;border-radius:14px;background:#101827;margin-bottom:8px}
.small{color:#94a3b8;font-size:13px}
</style>''',unsafe_allow_html=True)

st.title('E-Commerce Product Search Optimization')
st.caption('DAA Project • Search Algorithms • Sorting • Performance Analysis')

with st.sidebar:
    st.header('Search & Filters')
    query=st.text_input('Search products', placeholder='e.g. headphones, gaming, NovaTech')
    categories=['All']+sorted(df['Category'].unique().tolist())
    category=st.selectbox('Category',categories)
    price_min,price_max=int(df.Price.min()),int(df.Price.max())
    price_range=st.slider('Price range (₹)',price_min,price_max,(price_min,price_max))
    min_rating=st.slider('Minimum rating',0.0,5.0,0.0,0.5)
    sort_by=st.selectbox('Sort results by',['Relevance','Price: Low to High','Price: High to Low','Rating: High to Low','Most Reviews'])
    st.divider()
    st.caption('Dataset: 300 demo products')

start=time.perf_counter()
searched=linear_search(df,query) if query.strip() else df.copy()
search_time=(time.perf_counter()-start)*1000
filtered=searched[(searched.Price>=price_range[0])&(searched.Price<=price_range[1])&(searched.Rating>=min_rating)]
if category!='All': filtered=filtered[filtered.Category==category]
if sort_by=='Price: Low to High': filtered=filtered.sort_values('Price')
elif sort_by=='Price: High to Low': filtered=filtered.sort_values('Price',ascending=False)
elif sort_by=='Rating: High to Low': filtered=filtered.sort_values('Rating',ascending=False)
elif sort_by=='Most Reviews': filtered=filtered.sort_values('Reviews',ascending=False)

c1,c2,c3,c4=st.columns(4)
c1.metric('Products in Dataset',f'{len(df):,}')
c2.metric('Matching Results',f'{len(filtered):,}')
c3.metric('Search Time',f'{search_time:.3f} ms')
c4.metric('Algorithm','Linear Search')
st.divider()

st.subheader('📦 Search Results')
if filtered.empty:
    st.warning('No products match these filters. Try changing your search or filters.')
else:
    st.write(f'Found **{len(filtered)}** matching products')
    cols=st.columns(3)
    for idx,(_,p) in enumerate(filtered.head(60).iterrows()):
        with cols[idx%3]:
            st.markdown(f'''<div class="product"><b>{p.Product_Name}</b><br><span class="small">{p.Brand} • {p.Category}</span><h3>₹{p.Price:,}</h3>⭐ {p.Rating}/5 &nbsp; | &nbsp; {p.Reviews:,} reviews</div>''',unsafe_allow_html=True)
    if len(filtered)>60: st.info('Showing first 60 results to keep the page fast.')

st.divider()
st.subheader('⚙️ Algorithm Analysis')
left,right=st.columns(2)
with left:
    st.markdown('### Linear Search')
    st.write('Checks products one by one against the search keyword.')
    st.code('Time Complexity: O(n)\nSpace Complexity: O(1) extra')
    st.success(f'Found {len(searched)} matches in {search_time:.4f} ms')
with right:
    st.markdown('### Binary Search (Price)')
    target=st.number_input('Exact price to search for (₹)',min_value=0,value=999,step=100)
    t0=time.perf_counter(); exists=binary_price_search(df,int(target)); binary_time=(time.perf_counter()-t0)*1000
    st.write('Searches an array of prices after sorting it.')
    st.code('Time Complexity: O(log n)\nSorting prerequisite: O(n log n)')
    st.info(('Price exists in dataset' if exists else 'Exact price not found')+f' • {binary_time:.4f} ms')

st.subheader('Sorting Algorithm')
sort_df=df[['Product_Name','Price','Rating']].copy()
if st.button('Run Merge Sort Benchmark'):
    values=sort_df['Price'].tolist()
    def merge_sort(a):
        if len(a)<=1: return a
        mid=len(a)//2
        l=merge_sort(a[:mid]); r=merge_sort(a[mid:]); out=[]; i=j=0
        while i<len(l) and j<len(r):
            if l[i]<=r[j]: out.append(l[i]); i+=1
            else: out.append(r[j]); j+=1
        return out+l[i:]+r[j:]
    t0=time.perf_counter(); sorted_values=merge_sort(values); elapsed=(time.perf_counter()-t0)*1000
    st.success(f'Merge Sort completed: {len(sorted_values)} values sorted in {elapsed:.4f} ms')
    st.code('Merge Sort\nBest/Average/Worst: O(n log n)\nSpace Complexity: O(n)')

with st.expander('📚 Complexity Summary Table'):
    st.dataframe(pd.DataFrame({'Algorithm':['Linear Search','Binary Search','Merge Sort','Hash Table Lookup'],'Best Case':['O(1)','O(1)','O(n log n)','O(1)'],'Average Case':['O(n)','O(log n)','O(n log n)','O(1)'],'Worst Case':['O(n)','O(log n)','O(n log n)','O(n)']}),hide_index=True,use_container_width=True)

st.caption('Academic demonstration using generated sample product data. Search results and performance timings depend on the machine.')
