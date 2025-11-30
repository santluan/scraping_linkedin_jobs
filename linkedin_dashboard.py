import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
from functions_scrape_linkedin import scrape_linkedin_jobs
nltk.download('stopwords')
from nltk.corpus import stopwords

st.set_page_config(layout="wide")

st.title('📊 Dashboard para Análise de Vagas do Linkedin')
st.header('Análise de Dados')

# Limpar dados
def clear_text():
    st.session_state['my_key'] = ""
    st.session_state['my_location'] = ""

# Guardando dados em cache
@st.cache_data
def scrape_linkedin_cached(k, l):
    # Deixei 5 páginas por padrão
    return scrape_linkedin_jobs(k, l, start_page=1, end_page=5)
    
#### ---- SIDEBAR ----

with st.sidebar:
    st.write('Indique abaixo o nome da vaga e localização para iniciar a raspagem')

    keyword = st.text_input("Palavra-chave:", key='my_key')
    location = st.text_input("Localização:", key='my_location')

    if keyword and location:
        st.write(f'Começando raspagem de vagas do Linkedin para {keyword} em {location}')
        st.write('Pode levar um tempo...')
    
    st.button('Limpar texto', on_click=clear_text)

#### ---- LÓGICA PRINCIPAL ----

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

if keyword and location:

    df = scrape_linkedin_cached(keyword, location)
    df['Date_Posted'] = pd.to_datetime(df['Date_Posted'], format="%Y-%m-%d")
    df = df.sort_values(by='Date_Posted')

    with col1:
        st.write('### Distribuição de vagas por Nível')

        vagas_nivel = df.groupby('Level').size().reset_index()
        vagas_nivel.columns = ['Nivel', 'Quantidade']

        fig_bar = px.bar(vagas_nivel, x='Nivel', y='Quantidade')
        st.plotly_chart(fig_bar)

    with col2:
        st.write('### Nuvem de Palavras das descrições das vagas')
        
        col2_1, col2_2 = st.columns(2)
        with st.container():

            nivel_1 = col2_1.selectbox(
                "Selecionar nível:",
                ['Estágio', 'Junior', 'Pleno', 'Senior', 'Especialista', 'Outros'],
                key='nivel_1'
                )

            qt_words = col2_2.slider(
                'Selecione a quantidade de palavras', 
                10, 
                500, 
                100
                )

        def black_color_func(word, font_size, position,orientation,random_state=None, **kwargs):
            return("hsl(0,100%, 1%)")

        text = " ".join(description for description in df[df['Level']==nivel_1].Description)
        stopwords_pt = stopwords.words('portuguese')
        wordcloud = WordCloud(stopwords=stopwords_pt, background_color="white",max_words=qt_words).generate(text)
        wordcloud.recolor(color_func=black_color_func)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

    st.write('### Tabela de Dados Brutos')

    nivel_2 = st.selectbox(
        "Selecionar nível:",
        ['Estágio', 'Junior', 'Pleno', 'Senior', 'Especialista', 'Outros'],
        key='nivel_2'
        )

    df = scrape_linkedin_cached(keyword, location)
    df['Date_Posted'] = pd.to_datetime(df['Date_Posted'], format="%Y-%m-%d")
    df = df.sort_values(by='Date_Posted')
    st.dataframe(df[df['Level']==nivel_2], key='my_df')

    

    



