# 📊 Dashboard de Vendas - Superstore 🛒

## Descrição

Este projeto visa construir um dashboard de business intelligence de vendas baseado na base de dados *Sample - Superstore* disponibilizada pelo Tableau. O projeto envolve um processo de ETL (Extração, Transformação e Carga) utilizando Python no Google Colab, armazenando os dados em um banco de dados PostgreSQL na plataforma Aiven e implementando um data warehouse por meio da modelagem dimensional. O resultado final é um dashboard interativo desenvolvido com Streamlit e gráficos do Pyplot.

## Estrutura do Projeto

1. **ETL e Preparação de Dados**
   - **Ferramentas Utilizadas**: Python, Google Colab
   - **Processos**: Extração, transformação e carga dos dados da base Sample - Superstore. Inclui a construção de atributos e outras preparações necessárias.

2. **Armazenamento de Dados**
   - **Banco de Dados**: PostgreSQL
   - **Plataforma**: Aiven Cloud
   - **Modelagem**: Modelagem dimensional para suportar a construção de um data warehouse.

3. **Visualização de Dados**
   - **Ferramenta**: Streamlit
   - **Biblioteca dos gráficos**: Pyplot
   - **Descrição**: Desenvolvimento de um dashboard interativo para visualização dos dados de vendas com gráficos e tabelas. Inclui uma visualização geoespacial utilizando um arquivo GeoJSON.

## Arquivo GeoJSON

O projeto utiliza um arquivo GeoJSON para visualização geoespacial. O arquivo está disponível no repositório do GitHub da Folium:

- **URL do Repositório**: [Folium GeoJSON Repository]([https://github.com/python-visualization/folium](https://github.com/python-visualization/folium-example-data/))

## Observação

A senha da conexão do banco de dados foi definida como variável de ambiente. Desse modo, em caso de execução local, é necessário definir a variável ou alterá-la no código antes da execução.