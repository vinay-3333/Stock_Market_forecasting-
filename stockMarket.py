import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import datetime
from datetime import date,timedelta
import requests
from bs4 import BeautifulSoup


#Title
container = st.container(border=True)
container.title(':blue[Stock Market Forecasting App]')
container.subheader('interactive tools to valuate and analyze stocks through Reverse DCF model')


#add an image 
st.image('https://media.istockphoto.com/id/1492226950/photo/stock-market-online-business-graph-forex-trading-graph.jpg?s=612x612&w=0&k=20&c=Ft8YFU-iMJuk1gfs_3oEJ_FLDffitrJMVzMv0cIuIVs=',width=900)

#take input from the user of app about the start and end date 

#sidebar
st.sidebar.header('Select the parameters from below')

start_date = st.sidebar.date_input('Start Date',date(2021,3,15))
end_date=st.sidebar.date_input('End Date',date(2024,3,31))

#add ticker
ticker=st.sidebar.text_input('Stock Name','NESTLEIND')


global url
url = f'https://www.screener.in/company/{ticker}/'
global response
response = requests.get(url)
global soup
soup = BeautifulSoup(response.text,'html.parser')



#company current Stock price,date information
def company_info():
    company_class ='margin-0 show-from-tablet-landscape'
    company = soup.find(class_=company_class).text

    price_class ='flex flex-align-center'
    row_price= soup.find(class_=price_class).text.strip().replace('\n','').split()
    price = row_price[0]+row_price[1]
    date_class ='ink-600 font-size-11 font-weight-500'
    date = soup.find('div',class_=date_class).text.strip().replace('\n','').replace(' ','')


    about_class = 'title'
    about = soup.find(class_=about_class).text.strip()
    meta_data_class ='sub show-more-box about'
    meta_data_company = soup.find(class_=meta_data_class).text.strip()[:-3]

    return company,price,date,meta_data_company

company_name,company_price,current_date,about=company_info()
container = st.container(border=True)
container.subheader(f'{company_name}   :      {company_price} ',divider='rainbow')
container.write(current_date)
container.write(about)




#company current 
def ratios():
    market_cap =0
    current_price=0
    high_low=0
    stock_pe =0
    face_value=0
    dividend_yield=0
    roce=0
    company_ratio_class1 ='company-ratios'
    company_ratio_class2 ='flex flex-space-between'
    values = soup.find_all('div',class_=company_ratio_class1)
    for i in values:

        #market_cap    
        market_cap =i.find_all('li',class_=company_ratio_class2)[0].text.strip().split()
        market_cap=market_cap[0]+market_cap[1]+' : '+market_cap[2]+market_cap[3]+market_cap[4]

        #current_price
        current_price =i.find_all('li',class_=company_ratio_class2)[1].text.strip().split()
        current_price=current_price[0]+current_price[1]+' : '+current_price[2]+current_price[3]

        #High_low
        high_low=i.find_all('li',class_='flex flex-space-between')[2].text.strip().split()
        high_low=high_low[0]+high_low[1]+high_low[2]+' : '+high_low[3]+high_low[4]+high_low[5]+high_low[6]

        #stock_pe
        stock_pe =i.find_all('li',class_='flex flex-space-between')[3].text.strip().split()
        stock_pe=stock_pe[0]+' '+stock_pe[1]+' : '+stock_pe[2]

        #dividend_yield
        dividend_yield =i.find_all('li',class_='flex flex-space-between')[5].text.strip().split()
        dividend_yield=dividend_yield[0]+dividend_yield[1]+' : '+dividend_yield[2]+dividend_yield[3]

        #ROCE
        roce =i.find_all('li',class_='flex flex-space-between')[6].text.strip().split()
        roce=roce[0]+' : '+roce[1]+roce[2]
    return market_cap,current_price,high_low,stock_pe,dividend_yield,roce


Market_cap,Current_price,High_Low,Stock_PE,Dividend_Yield,RoCE=ratios()
container = st.container(border=True)
container.subheader('Company Ratios',divider='rainbow')
container.write(f'{Market_cap}  | {Current_price}    |  {High_Low}  ')
container.write(f'{Stock_PE}    |   {Dividend_Yield}  |  {RoCE}  ')




def financial_year23_PE_RoCE():
        #current Price
        price_class ='flex flex-align-center'
        row_price= soup.find(class_=price_class).text.strip().replace('\n','').split()
        price= int(row_price[1].replace(',',''))

        #EPS
        company_ratio_id ='profit-loss'
        values = soup.find_all(id=company_ratio_id)
        for i in values:
            l=i.find_all('tr')[11].text.strip().replace(',','').replace('EPS in Rs\n            \n          \n','').replace('\n',',').split(',')
        eps=float(l[-1])

        # current_price=self.stock_current_price()
        # eps_23_cons= self.eps_2023()

        #inancial year 2023 pe
        pe_23=price/eps
        pe_23=str(float(f"{pe_23:.2f}"))

        #median Roce
        values = soup.find_all(id='ratios')
        for i  in values:
            l=i.find_all('tr')[6].text.strip().replace('ROCE %\n            \n          \n','').replace('%\n',',').replace('%','').split(',')
            for i in range(len(l[:])):
                l[i]=int(l[i])
            median_roce=np.median(l[-6:-1])
            median_roce=str(float(f"{median_roce:.2f}"))
        return price,eps,pe_23,median_roce

stock_price,eps_2023,fy_pe_23,median_RoCE=financial_year23_PE_RoCE()

container = st.container(border=True)
container.subheader('Financial Year 2023 PE & RoCE',divider='rainbow')
container.write(f'Stock Symbol: {ticker}')
container.write(f'Current {Stock_PE}')
container.write(f'FY23PE: {fy_pe_23}')
container.write(f'5-yr median pre-tax RoCE: {median_RoCE}')


#Graph and Table

#get index column values
def get_index_column_values():
    graph_class='ranges-table'
    values = soup.find_all('table',class_=graph_class)

#index
    index = list()
    a = list()
    for i in values[0:2]:
        a =i.find_all('tr')[0].text.split()
        a = (a[1]+' ' +a[2])
        index.append(a)

#column
    column=list()
    b= list()
    for i in values[0:1]:
        b=i.find_all('tr')[1].text.strip().replace(':','').split()
        column.append(b[0]+b[1])
        b=i.find_all('tr')[2].text.strip().replace(':','').split()
        column.append(b[0]+b[1])
        b=i.find_all('tr')[3].text.strip().replace(':','').split()
        column.append(b[0]+b[1])
        b=i.find_all('tr')[4].text.strip().replace(':','').split()
        column.append(b[0])

#values
    val = list()
    c=list()
    for i in values[0:2]:
        c=i.find_all('tr')[1].text.strip().replace(':','').split()
        val.append(int(c[-1].replace('%','')))
        c=i.find_all('tr')[2].text.strip().replace(':','').split()
        val.append(int(c[-1].replace('%','')))
        c=i.find_all('tr')[3].text.strip().replace(':','').split()
        val.append(int(c[-1].replace('%','')))
        c=i.find_all('tr')[4].text.strip().replace(':','').split()
        val.append(int(c[-1].replace('%','')))
    return index,column,val
    

#Table
def table():
    index,column,val=get_index_column_values()
    d={
    column[0]:val[0:5:4],
    column[1]:val[1:6:4],
    column[2]:val[2:7:4],
    column[3]:val[3::4]

    }
    graph=pd.DataFrame(d,index=index)
    return graph
container = st.container(border=True)
container.subheader("Sales and Profit Growth Table",divider='rainbow')
container.write(table())



#profit graph
def sales_profit_graph():
    # index,column,val=get_index_column_values()
    graph=table()
    graph.insert(0,'Growth',graph.index,True)
    graph.reset_index(drop=True,inplace=True)
    # fig = px.bar(graph.index[0],graph.columns[0:])
    return graph  
    # fig = px.histogram(graph,graph.loc[1:])

# st.bar_chart(sales_profit_graph(),width=500,height=500)

profit=sales_profit_graph()
container = st.container(border=True)
container.subheader("Sales and Profit Growth Graph",divider='rainbow')
container.bar_chart(profit,x='Growth',y=profit.columns[1:],width=700,height=500)


#fetch data from user input using yfinance 

data = yf.download(ticker+'.NS',start=start_date,end=end_date)
data.insert(0,'Date',data.index,True)
data.reset_index(drop=True,inplace=True)
container = st.container(border=True)
container.subheader(f'Historical Prices From {start_date} to {end_date}',divider='rainbow')
container.write(data)

#plot the data
container = st.container(border=True)
container.subheader('Data Visualization ',divider='rainbow')
fig = px.line(data,x='Date',y=data.columns,width=1000,height=800)
container.plotly_chart(fig)


a=yf.Ticker(ticker+'.NS')
#major Share holder
container = st.container(border=True)
container.subheader('Major Share Holder',divider='rainbow')
container.write(a.major_holders)







