import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic


@st.cache_data
def carregar_dados_processados():
    """
    Carrega o arquivo CSV já pré-processado com as coordenadas.
    Esta função é extremamente rápida.
    """
    try:
        df = pd.read_csv('estabelecimentos_geocoded.csv', sep=';')
        return df
    except FileNotFoundError:
        st.error("Arquivo de dados 'estabelecimentos_geocoded.csv' não encontrado! Por favor, execute o script 'preprocessador.py' primeiro.")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_analise():
    """ Carrega os arquivos originais para as análises nos gráficos. """
    try:
        df_restaurantes = pd.read_csv("restaurante.csv", sep=";")
        df_bares = pd.read_csv("bar.csv", sep=";")
        return df_restaurantes, df_bares
    except FileNotFoundError:
        st.error("Arquivos originais ('restaurante.csv', 'bar.csv') não encontrados na pasta.")
        return pd.DataFrame(), pd.DataFrame()


df_total_geo = carregar_dados_processados()
df_restaurantes_analise, df_bar_analise = carregar_dados_analise()

# --- INTERFACE DO STREAMLIT ---

with st.sidebar:
    st.text('Alisson Nobre Nogueira: Frontend')
    st.text('Carlos Estellita Neto: Cientista de Dados')
    st.text('Eulidio Regadas de Souza: Cientista de Dados')

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", width=300)

tab1, tab2, tab3, tab4 = st.tabs(["Apresentação", "Análise dos restaurantes", "Análise dos bares", "Geolocalização"])

# --- Aba de Apresentação ---
with tab1:
    st.header("Apresentação", divider="red")
    st.markdown("Quando o rolê tá bom, ninguém quer parar, né?")
    st.markdown("Com o After, você decide onde sua noite vai terminar — ou começar de novo.")
    st.markdown("E aí? Bora de After?")

    st.header("Detalhes técnicos", divider="red")
    st.markdown("A aplicação se trata de um serviço de geolocalização, onde é possível o usuário filtrar e encontrar quais estabelecimentos estão disponíveis para continuar sua noite.")
    st.markdown("Foram escolhidos os datasets **restaurante** e **bar**.")
    st.markdown("Na seção de análise de dados, foram plotados gráficos a partir dos atributos julgados como mais relevantes - Pontuação e Tipo de estabelecimento.")
    st.markdown("Por fim, na seção de mapa, há a possibilidade de filtrar os estabelecimentos por pontuação, dataset (restaurante ou bar), especialidade do estabelecimento e por proximidade de distância ao pin selecionado.")

# --- Aba de Análise dos Restaurantes ---
with tab2:
    st.header("Análise dos restaurantes")
    if not df_restaurantes_analise.empty:
        df_limpo = df_restaurantes_analise.dropna(subset=['NOME', 'PONTUACAO', 'TIPO']).copy()

        # PRIMEIRO GRÁFICO RESTAURANTES
        st.markdown("$\;\;\;$ O gráfico abaixo mostra a *contagem de restaurantes por tipo*, destacando que a maioria é classificada genericamente como Restaurante, seguido por estabelecimentos com faixas de preço $$ e $$$.")
        contagem = df_limpo['TIPO'].value_counts()
        rotulos_escapados = [str(s).replace('$', r'\$') for s in contagem.index]
        
        fig1, ax1 = plt.subplots(figsize=(12, 7))
        sns.barplot(x=rotulos_escapados, y=contagem.values, palette='mako', edgecolor="black", ax=ax1)
        for i, v in enumerate(contagem.values):
            ax1.text(i, v + 0.5, str(v), ha='center')
        for label in ax1.get_xticklabels():
            label.set_text(label.get_text().replace('\\', ''))
        
        ax1.set_title('Contagem de Restaurantes por Tipo', fontsize=16)
        ax1.set_xlabel('Tipo de Restaurante', fontsize=12)
        ax1.set_ylabel('Quantidade (Frequência)', fontsize=12)
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        ax1.grid(alpha=0.2)
        fig1.tight_layout()
        st.pyplot(fig1)
        st.write("####")

        # SEGUNDO GRÁFICO RESTAURANTES
        st.markdown("$\;\;\;$ Este gráfico exibe os 50 locais com as melhores pontuações, variando de 4,0 a quase 5,0. A maioria pertence às faixas de preço $ e $$, mas há também estabelecimentos mais caros ($$$ e $$$$) com alta avaliação.")
        faixas_de_preco = ['$', '$$', '$$$', '$$$$']
        df_filtrado_por_preco = df_limpo[df_limpo['TIPO'].isin(faixas_de_preco)].copy()
        df_para_plotar = df_filtrado_por_preco.sort_values(by='PONTUACAO', ascending=False).head(50)
        df_para_plotar['TIPO'] = df_para_plotar['TIPO'].apply(lambda s: str(s).replace('$', r'\$'))
        ordem_da_legenda = [r'\$', r'\$\$', r'\$\$\$', r'\$\$\$\$']

        fig2, ax2 = plt.subplots(figsize=(15, 14), dpi=300)
        sns.barplot(x='PONTUACAO', y='NOME', hue='TIPO', data=df_para_plotar, palette='Blues', edgecolor="black", hue_order=ordem_da_legenda, ax=ax2)
        ax2.set_title('Locais por Pontuação e Faixa de Preço (Top 50)', fontsize=16)
        ax2.set_xlabel('Pontuação', fontsize=12)
        ax2.set_ylabel('Local', fontsize=12)
        ax2.set_xlim(4, 5)
        ax2.grid(axis='x', alpha=0.2)
        fig2.tight_layout()
        st.pyplot(fig2)
        st.write("####")

        # TERCEIRO GRÁFICO RESTAURANTES
        st.markdown("$\;\;\;$ Este gráfico apresenta os *50 restaurantes mais bem avaliados* por pontuação. As notas variam entre *4,5 e 5,0, com forte presença de restaurantes do tipo **genérico**, *comida brasileira* e *caseira*.")
        df_ordenado = df_limpo.sort_values(by='PONTUACAO', ascending=False)
        top_50_restaurantes = df_ordenado.head(50)
        top_50_restaurantes['TIPO'] = top_50_restaurantes['TIPO'].apply(lambda s: str(s).replace('$', r'\$'))
        
        fig3, ax3 = plt.subplots(figsize=(12, 14))
        sns.barplot(x='PONTUACAO', y='NOME', hue='TIPO', data=top_50_restaurantes, palette='tab10', edgecolor="black", ax=ax3)
        ax3.set_title('Restaurantes por Pontuação e Tipo (Top 50)', fontsize=16)
        ax3.set_xlabel('Pontuação', fontsize=12)
        ax3.set_ylabel('Local', fontsize=12)
        ax3.set_xlim(4.5, 5)
        ax3.grid(axis='x', alpha=0.2)
        fig3.tight_layout()
        st.pyplot(fig3)

# --- Aba de Análise dos Bares ---
with tab3:
    st.header("Análise dos bares")
    if not df_bar_analise.empty:
        df_limpo2 = df_bar_analise.dropna(subset=['NOME', 'PONTUACAO', 'TIPO']).copy()

        # PRIMEIRO GRÁFICO BARES
        st.markdown("$\;\;\;$ Este gráfico mostra a *quantidade de bares por tipo*. A maioria é classificada simplesmente como *Bar*, seguida por estabelecimentos de faixa de preço $$ e $.")
        contagem2 = df_limpo2['TIPO'].value_counts()
        rotulos_escapados2 = [str(s).replace('$', r'\$') for s in contagem2.index]
        
        fig4, ax4 = plt.subplots(figsize=(12, 7))
        sns.barplot(x=rotulos_escapados2, y=contagem2.values, palette='Reds_r', edgecolor="black", ax=ax4)
        for i, v in enumerate(contagem2.values):
            ax4.text(i, v + 0.5, str(v), ha='center')
        for label in ax4.get_xticklabels():
            label.set_text(label.get_text().replace('\\', ''))
            
        ax4.set_title('Contagem de Bares por Tipo', fontsize=16)
        ax4.set_xlabel('Tipo de Bar', fontsize=12)
        ax4.set_ylabel('Quantidade (Frequência)', fontsize=12)
        plt.setp(ax4.get_xticklabels(), rotation=45, ha='right')
        ax4.grid(alpha=0.2)
        fig4.tight_layout()
        st.pyplot(fig4)
        st.write("####")

        # SEGUNDO GRÁFICO BARES
        st.markdown("$\;\;\;$ Este gráfico mostra os *50 bares mais bem avaliados*. A maioria está nas faixas de preço $*$ e $**$, demonstrando boa qualidade independente do custo.")
        faixas_de_preco_bar = ['$', '$$', '$$$', '$$$$']
        df_filtrado_por_preco2 = df_limpo2[df_limpo2['TIPO'].isin(faixas_de_preco_bar)].copy()
        df_para_plotar2 = df_filtrado_por_preco2.sort_values(by='PONTUACAO', ascending=False).head(50)
        df_para_plotar2['TIPO'] = df_para_plotar2['TIPO'].apply(lambda s: str(s).replace('$', r'\$'))
        ordem_da_legenda_bar = [r'\$', r'\$\$', r'\$\$\$', r'\$\$\$\$']

        fig5, ax5 = plt.subplots(figsize=(15, 14), dpi=300)
        sns.barplot(x='PONTUACAO', y='NOME', hue='TIPO', data=df_para_plotar2, palette='Reds', edgecolor="black", hue_order=ordem_da_legenda_bar, ax=ax5)
        ax5.set_title('Bares por Pontuação e Faixa de Preço (Top 50)', fontsize=16)
        ax5.set_xlabel('Pontuação', fontsize=12)
        ax5.set_ylabel('Local', fontsize=12)
        ax5.set_xlim(4, 5)
        ax5.grid(axis='x', alpha=0.2)
        fig5.tight_layout()
        st.pyplot(fig5)

        # SEGUNDO GRÁFICO BARES
        st.markdown("$\;\;\;$ Este gráfico apresenta os 50 bares mais bem avaliados, com pontuações variando de 4,5 a 5,0. A maioria dos locais é classificada como Bar, mas também há presença de bares com música ao vivo, bares e grills, restaurantes, churrascarias e até bares de cerveja.")
        df_ordenado2 = df_limpo2.sort_values(by='PONTUACAO', ascending=False)
        df_ordenado2['TIPO'] = df_ordenado2['TIPO'].apply(lambda s: str(s).replace('$', r'\$'))
        top_50_bares = df_ordenado2.head(50)
        fig6, ax6 = plt.subplots(figsize=(15, 14), dpi=300)
        sns.barplot(x='PONTUACAO', y='NOME', hue='TIPO', data=top_50_bares, palette='tab10', edgecolor = "black")
        ax6.set_title('Bares por Pontuação e Tipo(Top 50)', fontsize=16)
        ax6.set_xlabel('Pontuação', fontsize=12)
        ax6.set_ylabel('Local', fontsize=12)
        ax6.set_xlim(4.5, 5)
        ax6.grid(axis='x', alpha = 0.2)
        fig6.tight_layout()
        st.pyplot(fig6)



# --- Aba de Geolocalização ---
with tab4:
    st.header("Procure seu After aqui!")

    if df_total_geo.empty:
        st.stop()
    
    values = st.slider("Selecione o range de pontuação", 0.0, 5.0, (0.0, 5.0), step=0.1)
    tipo_selecionado = st.radio("Escolha o tipo de estabelecimento:", ['Todos', 'Restaurantes', 'Bares'])
    
    if tipo_selecionado == 'Restaurantes':
        df_filtrado_tipo = df_total_geo[df_total_geo['dataset_type'] == 'restaurante'].copy()
    elif tipo_selecionado == 'Bares':
        df_filtrado_tipo = df_total_geo[df_total_geo['dataset_type'] == 'bar'].copy()
    else:
        df_filtrado_tipo = df_total_geo.copy()

    if not df_filtrado_tipo.empty:
        especialidades = sorted(df_filtrado_tipo['TIPO'].dropna().unique())
        especialidades.insert(0, "Todos")
        tipo_especialidade = st.selectbox("Escolha a especialidade do local:", especialidades)

        if tipo_especialidade != "Todos":
            df_filtrado_especialidade = df_filtrado_tipo[df_filtrado_tipo['TIPO'] == tipo_especialidade].copy()
        else:
            df_filtrado_especialidade = df_filtrado_tipo.copy()
    else:
        df_filtrado_especialidade = pd.DataFrame()

    if not df_filtrado_especialidade.empty:
        df_final_filtrado = df_filtrado_especialidade[
            (df_filtrado_especialidade['PONTUACAO'] >= values[0]) &
            (df_filtrado_especialidade['PONTUACAO'] <= values[1])
        ].copy()
    else:
        df_final_filtrado = df_filtrado_especialidade

    enderecos = df_final_filtrado['LOCAL'].unique().tolist()
    local_referencia = st.selectbox("Escolha um local como referência:", ['Nenhum'] + enderecos)

    if local_referencia != 'Nenhum':
        raio_km = st.slider("Selecione o raio de distância (km):", 0.5, 10.0, 2.0, step=0.1)
        
        ref_row = df_final_filtrado[df_final_filtrado['LOCAL'] == local_referencia].iloc[0]
        ref_coord = (ref_row['LAT'], ref_row['LON'])
        
        df_proximos = df_final_filtrado[
            df_final_filtrado.apply(lambda row: geodesic(ref_coord, (row['LAT'], row['LON'])).km <= raio_km, axis=1)
        ]
        
        if not df_proximos.empty:
            mapa = folium.Map(location=ref_coord, zoom_start=15)
            folium.Marker(
                location=ref_coord,
                popup=f"<b>{local_referencia} (Referência)</b>",
                tooltip="Ponto de Referência",
                icon=folium.Icon(color='green', icon='star')
            ).add_to(mapa)

            for _, row in df_proximos.iterrows():
                cor = 'red' if row['dataset_type'] == 'bar' else 'blue'
                popup_html = f"""
                <b>{row['NOME']}</b><br>
                Endereço: {row['LOCAL']}<br>
                Pontuação: {row['PONTUACAO']}
                """
                folium.Marker(
                    location=[row['LAT'], row['LON']],
                    popup=popup_html,
                    tooltip=row['NOME'],
                    icon=folium.Icon(color=cor)
                ).add_to(mapa)
            folium_static(mapa)
        else:
            st.warning("Nenhum estabelecimento encontrado dentro do raio selecionado.")
    else:
        if not df_final_filtrado.empty:
            mapa = folium.Map(location=[df_final_filtrado['LAT'].mean(), df_final_filtrado['LON'].mean()], zoom_start=12)
            for _, row in df_final_filtrado.iterrows():
                cor = 'red' if row['dataset_type'] == 'bar' else 'blue'
                popup_html = f"""
                <b>{row['NOME']}</b><br>
                Endereço: {row['LOCAL']}<br>
                Pontuação: {row['PONTUACAO']}
                """
                folium.Marker(
                    location=[row['LAT'], row['LON']],
                    popup=popup_html,
                    tooltip=row['NOME'],
                    icon=folium.Icon(color=cor)
                ).add_to(mapa)
            folium_static(mapa)
        else:
            st.info("Nenhum estabelecimento encontrado para os filtros selecionados.")