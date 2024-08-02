import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import plotly
import plotly.express as px
import plotly.graph_objects as go
import os

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Dashboard de Vendas',
    page_icon=':bar_chart:'
)

# Conexão com o banco de dados Postgres
def get_db_connection():
    return psycopg2.connect(
        dbname="tebd",
        user="avnadmin",
        password= os.getenv("USER_PASSWORD"),
        host="pg-tebd-tebd.g.aivencloud.com",
        port="11321"
    )

# Função para executar uma query SQL e retornar um DataFrame
def execute_query(query, params=None):
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Consultas SQL para cada indicador e relatório
queries = {
    "sales_by_date": """
        SELECT dp.date as order_date, SUM(fs.sales) as total_sales
        FROM fct_sale fs
        JOIN dim_period dp ON fs.orderdatekey = dp.datekey
        WHERE dp.date BETWEEN %s AND %s
        GROUP BY dp.date
        ORDER BY dp.date
    """,
    "sales_by_state": """
        SELECT dr.state, dr.stateabbreviation, SUM(fs.sales) as total_sales
        FROM fct_sale fs
        JOIN dim_region dr ON fs.regionkey = dr.regionkey
        JOIN dim_period dp ON fs.orderdatekey = dp.datekey
        WHERE dp.date BETWEEN %s AND %s
        GROUP BY dr.state, dr.stateabbreviation
        ORDER BY dr.state, dr.stateabbreviation
    """,
    "sales_by_category": """
        SELECT dp3.category, COUNT(fs.orderid) as num_sales
        FROM fct_sale fs
        JOIN dim_product dp3 ON fs.productkey = dp3.productkey
        JOIN dim_period dp ON fs.orderdatekey = dp.datekey
        WHERE dp.date BETWEEN %s AND %s
        GROUP BY dp3.category
        ORDER BY dp3.category
    """,
    "cost_by_category": """
        SELECT dp3.category, SUM(fs.sales - fs.profit) as total_cost
        FROM fct_sale fs
        JOIN dim_product dp3 ON fs.productkey = dp3.productkey
        JOIN dim_period dp ON fs.orderdatekey = dp.datekey
        WHERE dp.date BETWEEN %s AND %s
        GROUP BY dp3.category
        ORDER BY dp3.category
    """,
    "totals": """
        SELECT 
            SUM(fs.sales) as total_sales, 
            SUM(fs.sales - fs.profit) as total_cost, 
            SUM(fs.profit) as total_profit
        FROM fct_sale fs
        JOIN dim_period dp ON fs.orderdatekey = dp.datekey
        WHERE dp.date BETWEEN %s AND %s
    """,
    "report_by_subcategory": """
        SELECT dp3.subcategory, 
               SUM(fs.sales) as total_sales, 
               COUNT(fs.orderid) as num_sales, 
               SUM(fs.discount) as total_discount, 
               SUM(fs.profit) as total_profit, 
               SUM(fs.sales - fs.profit) as total_cost
        FROM fct_sale fs
        JOIN dim_product dp3 ON fs.productkey = dp3.productkey
        JOIN dim_period dp ON fs.orderdatekey = dp.datekey
        WHERE dp.date BETWEEN %s AND %s
        GROUP BY dp3.subcategory
        ORDER BY dp3.subcategory
    """,
    "detailed_sales": """
        SELECT fs.orderid, fs.sales, fs.quantity, fs.discount, fs.profit, fs.cost,
               dp.date as order_date, dr.city, dr.state, dr.region, ds.shipmode, dp2.date as ship_date,
               dc.customername, dc.segment, dp3.productname, dp3.category, dp3.subcategory
        FROM fct_sale fs
        JOIN dim_period dp ON fs.orderdatekey = dp.datekey
        JOIN dim_period dp2 ON fs.shipdatekey = dp2.datekey
        JOIN dim_customer dc ON fs.customerkey = dc.customerkey
        JOIN dim_product dp3 ON fs.productkey = dp3.productkey
        JOIN dim_region dr ON fs.regionkey = dr.regionkey
        JOIN dim_shipmode ds ON fs.shipmodekey = ds.shipmodekey
        WHERE dp.date BETWEEN %s AND %s
    """,
    "report_by_product": """
        SELECT dp3.productname, 
               SUM(fs.sales) as total_sales, 
               COUNT(fs.orderid) as num_sales, 
               SUM(fs.discount) as total_discount, 
               SUM(fs.profit) as total_profit, 
               SUM(fs.cost) as total_cost
        FROM fct_sale fs
        JOIN dim_product dp3 ON fs.productkey = dp3.productkey
        JOIN dim_period dp ON fs.orderdatekey = dp.datekey
        WHERE dp.date BETWEEN %s AND %s
        GROUP BY dp3.productname
        ORDER BY dp3.productname
    """,
    "report_by_product_region": """
        SELECT dp3.productname, dr.city, dr.state, dr.region, 
               SUM(fs.sales) as total_sales, 
               COUNT(fs.orderid) as num_sales, 
               SUM(fs.discount) as total_discount, 
               SUM(fs.profit) as total_profit, 
               SUM(fs.sales - fs.profit) as total_cost
        FROM fct_sale fs
        JOIN dim_product dp3 ON fs.productkey = dp3.productkey
        JOIN dim_region dr ON fs.regionkey = dr.regionkey
        JOIN dim_period dp ON fs.orderdatekey = dp.datekey
        WHERE dp.date BETWEEN %s AND %s
        GROUP BY dp3.productname, dr.city, dr.state, dr.region
        ORDER BY dp3.productname, dr.city, dr.state, dr.region
    """,
    "max_min_date": """
    SELECT 
        MIN(date) AS min_date,
        MAX(date) AS max_date
    FROM 
        dim_period;
    """
}

# Função para gerar os gráficos e relatórios
def generate_reports(start_date, end_date):
     # Totais
     totals = execute_query(queries["totals"], (start_date, end_date)).iloc[0]
     total_sales = totals['total_sales']

     if (total_sales is None or total_sales == 0):
         #Resultado caso não hajam dados disponíveis para o período
         isnull = st.write("Não foram encontrados dados para o período informado")
     else:
         #Limpa conteúdo de isnull
         isnull = None

         #Continuação dos totais em caso de sucesso
         total_cost = totals['total_cost']
         total_profit = totals['total_profit']
    
         st.subheader("Totais")
         st.metric(label="Total de Vendas", value=f"{total_sales:,.2f}")
         st.metric(label="Total de Custo", value=f"{total_cost:,.2f}")
         st.metric(label="Total de Lucro", value=f"{total_profit:,.2f}")
         st.subheader("Indicadores Gráficos")
    
         # Valor total de vendas por data
         sales_by_date = execute_query(queries["sales_by_date"], (start_date, end_date))
         fig = px.line(sales_by_date, x='order_date', y='total_sales', title="Valor total de vendas por data do pedido")
         st.plotly_chart(fig)
    
         # Valor total de vendas por estado
         sales_by_state = execute_query(queries["sales_by_state"], (start_date, end_date))
         fig = px.bar(sales_by_state, x='total_sales', y='state', orientation='h', title="Valor total de vendas por estado")
         st.plotly_chart(fig)
    
         # Mapa de vendas por estado
         state_sales = execute_query(queries["sales_by_state"], (start_date, end_date))
         map_data = pd.DataFrame({
             'state': state_sales['state'],
             'total_sales': state_sales['total_sales'],
             'stateabbreviation': state_sales['stateabbreviation']
         })
         geojson_url = "https://raw.githubusercontent.com/pauloandreoliv/tebd/master/data_folium.json"
         fig = px.choropleth(map_data,
                             geojson=geojson_url,
                             locations="stateabbreviation",
                             color="total_sales",
                             color_continuous_scale="Blues",
                             scope="usa",
                             hover_data=["state", "total_sales"],
                             labels={'sales': 'Vendas'}
                            )
         st.plotly_chart(fig)
    
         # Número de vendas por categoria
         sales_by_category = execute_query(queries["sales_by_category"], (start_date, end_date))
         fig = px.bar(sales_by_category, x='category', y='num_sales', title="Número de vendas por categoria de produto")
         st.plotly_chart(fig)
    
         # Valor do custo por categoria (custo = venda - lucro)
         cost_by_category = execute_query(queries["cost_by_category"], (start_date, end_date))
         fig = px.bar(cost_by_category, x='category', y='total_cost', title="Custo por categoria de produto")
         st.plotly_chart(fig)
    
         # Relatórios
         st.subheader("Relatórios")
    
         # Valor total de vendas, desconto, lucro e número de vendas por Subcategoria
         report_by_subcategory = execute_query(queries["report_by_subcategory"], (start_date, end_date))
         st.write("Valor total de vendas, desconto, lucro e número de vendas por Subcategoria")
         st.dataframe(report_by_subcategory)
    
         # Vendas detalhadas
         detailed_sales = execute_query(queries["detailed_sales"], (start_date, end_date))
         st.write("Vendas detalhadas")
         st.dataframe(detailed_sales)
    
         # Valor total de vendas, desconto, lucro e número de vendas por produto
         report_by_product = execute_query(queries["report_by_product"], (start_date, end_date))
         st.write("Valor total de vendas, desconto, lucro e número de vendas por produto")
         st.dataframe(report_by_product)
    
         # Total de vendas, número de vendas, desconto, lucro e custo por produto, cidade, estado e região
         report_by_product_region = execute_query(queries["report_by_product_region"], (start_date, end_date))
         st.write("Valor total de vendas, número de vendas, valor total de desconto, lucro e custo por produto, cidade, estado e região")
         st.dataframe(report_by_product_region)

# Configuração do painel Streamlit
st.title("🛒 Dashboard de Vendas")

# Seleção de data
dates = execute_query(queries['max_min_date'])
max_date = dates['max_date'].iloc[0]
min_date = dates['min_date'].iloc[0]

start_date = st.date_input("Data de Início", min_date)
end_date = st.date_input("Data de Fim", max_date)

# Botão para executar a consulta
if st.button("Consultar"):
    date_between = st.write(f"Consultando dados de {start_date} a {end_date}")
    generate_reports(start_date, end_date)
else:
    generate_reports(start_date, end_date)
