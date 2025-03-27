import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, pearsonr

st.title("Análise de Evasão por Gênero")

# Upload do arquivo
uploaded_file = st.file_uploader("Faça o upload de uma planilha Excel:", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl") if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file, encoding="utf-8")

        # Agrupando por curso - Etapa de Seleção de Dados
        dfAgrupadoCurso = df.groupby(["COD_CURSO", "NOME_CURSO"], as_index=False)[
            ["QTDE SEXO MASCULINO", "QTDE SEXO FEMININO", "QTDE SEXO NÃO INFORMADO"]
        ].sum()

        dfAgrupadoCurso['QTD_ALUNOS'] = dfAgrupadoCurso[
            ["QTDE SEXO MASCULINO", "QTDE SEXO FEMININO", "QTDE SEXO NÃO INFORMADO"]
        ].sum(axis=1)

        dfAgrupadoCursoTotal = dfAgrupadoCurso[["COD_CURSO", "NOME_CURSO", "QTD_ALUNOS"]]
        st.write("Cursos do banco de dados:")
        st.dataframe(dfAgrupadoCursoTotal)

        # Exclui cursos no DataFrame
        cursos_para_excluir = st.multiselect("Selecione os cursos para excluir", options=dfAgrupadoCursoTotal["NOME_CURSO"].unique())
        if cursos_para_excluir:
            df = df[~df["NOME_CURSO"].isin(cursos_para_excluir)]
            st.write(f"Cursos excluídos: {', '.join(cursos_para_excluir)}")
            
        # Etapa de Pré-Processamento
        # Boxplot para "ANO_INGRESSO"
        plt.figure(figsize=(8, 6))
        sns.boxplot(x=df["ANO_INGRESSO"])
        plt.title("Boxplot do Ano de Ingresso")
        plt.show()

        # Calculo do IQR para identificar os outliers de "ANO_INGRESSO"
        Q1_INGRESSO = df["ANO_INGRESSO"].quantile(0.25)
        Q3_INGRESSO = df["ANO_INGRESSO"].quantile(0.75)
        IQR_INGRESSO = Q3_INGRESSO - Q1_INGRESSO

        # Limites inferior e superior para "ANO_INGRESSO"
        limite_inferior_INGRESSO = Q1_INGRESSO - 1.5 * IQR_INGRESSO
        limite_superior_INGRESSO = Q3_INGRESSO + 1.5 * IQR_INGRESSO

        # Filtra os dados excluindo os outliers de "ANO_INGRESSO"
        df_sem_outliers_INGRESSO = df[(df["ANO_INGRESSO"] >= limite_inferior_INGRESSO) & (df["ANO_INGRESSO"] <= limite_superior_INGRESSO)]

        # Boxplot para "ANO_EVASAO"
        plt.figure(figsize=(8, 6))
        sns.boxplot(x=df["ANO_EVASAO"])
        plt.title("Boxplot do Ano de Evasão")
        plt.show()

        # Calculo do IQR para identificar os outliers de "ANO_EVASAO"
        Q1_EVASAO = df["ANO_EVASAO"].quantile(0.25)
        Q3_EVASAO = df["ANO_EVASAO"].quantile(0.75)
        IQR_EVASAO = Q3_EVASAO - Q1_EVASAO

        # Limites inferior e superior para "ANO_EVASAO"
        limite_inferior_EVASAO = Q1_EVASAO - 1.5 * IQR_EVASAO
        limite_superior_EVASAO = Q3_EVASAO + 1.5 * IQR_EVASAO

        # Filtra os dados excluindo os outliers de "ANO_EVASAO"
        df_sem_outliers = df_sem_outliers_INGRESSO[(df_sem_outliers_INGRESSO["ANO_EVASAO"] >= limite_inferior_EVASAO) & (df_sem_outliers_INGRESSO["ANO_EVASAO"] <= limite_superior_EVASAO)]

        # Segue o processamento com os dados filtrados - sem os outliers
        if "ANO_INGRESSO" not in df_sem_outliers.columns or "ANO_EVASAO" not in df_sem_outliers.columns:
            st.error("O arquivo precisa conter as colunas 'ANO_INGRESSO' e 'ANO_EVASAO' para calcular o tempo de formação.")
        else:
            df_sem_outliers["TEMPO_FORMACAO"] = df_sem_outliers["ANO_EVASAO"] - df_sem_outliers["ANO_INGRESSO"]
            st.write("### Dados após remoção de outliers")
            st.dataframe(df_sem_outliers)
        
        # Criar coluna com o total de alunos em cada linha
        df_sem_outliers["QTD_ALUNOS"] = df_sem_outliers[["QTDE SEXO MASCULINO", "QTDE SEXO FEMININO", "QTDE SEXO NÃO INFORMADO"]].sum(axis=1)

        # Agrupar quantidade de alunos que ingressaram por ano (somando todas as colunas de gênero)
        dfIngressantes = df_sem_outliers.groupby("ANO_INGRESSO", as_index=False)["QTD_ALUNOS"].sum()

        # Exibir tabela com a quantidade de ingressantes por ano antes da seleção
        st.write("### Quantidade de alunos ingressantes por ano (dados completos):")
        st.dataframe(dfIngressantes)

        # Criar um filtro para selecionar um intervalo de anos
        min_ano, max_ano = int(dfIngressantes["ANO_INGRESSO"].min()), int(dfIngressantes["ANO_INGRESSO"].max())
        anos_selecionados = st.slider(
            "Selecione o intervalo de anos de ingresso:",
            min_ano, max_ano, (min_ano, max_ano)
        )
        
        # Exibir tabela filtrada com a quantidade de ingressantes por ano
        st.write("### Dados filtrados de ingressantes por ano:")
        st.dataframe(df_sem_outliers)

        # Filtrar os dados com base no intervalo selecionado
        df_sem_outliers = df_sem_outliers[
            (df_sem_outliers["ANO_INGRESSO"] >= anos_selecionados[0]) & 
            (df_sem_outliers["ANO_INGRESSO"] <= anos_selecionados[1])
        ]
        
        # Exibir tabela filtrada com a quantidade de ingressantes por ano
        st.write("### Dados filtrados de ingressantes por ano:")
        st.dataframe(df_sem_outliers)

        # Criar gráfico de barras para visualizar os ingressantes por ano
        #plt.figure(figsize=(10, 5))
        #sns.barplot(data=df_sem_outliers, x="ANO_INGRESSO", y="QTD_ALUNOS", palette="Blues_r")
        #plt.xlabel("Ano de Ingresso")
        #plt.ylabel("Quantidade de Alunos")
        #plt.title("Ingressantes por Ano")
        #plt.xticks(rotation=45)
        #st.pyplot(plt)
        
        # Em caso de necessidade, tire a # para exibir o tamanho do DataFrame antes e depois da filtragem para analisar se os outliers foram removidos            
        #st.write(f"Antes da remoção dos outliers: {len(df)} linhas")
        #st.write(f"Depois da remoção dos outliers: {len(df_sem_outliers)} linhas")
           
        # Etapa de Transformação
        # Agrupando por forma de evasão
        dfAgrupadoEvasao = df_sem_outliers.groupby(["FORMA_EVASAO"], as_index=False)[
            ["QTDE SEXO MASCULINO", "QTDE SEXO FEMININO", "QTDE SEXO NÃO INFORMADO"]
        ].sum()

        dfAgrupadoEvasao["QTD_ALUNOS"] = dfAgrupadoEvasao[
            ["QTDE SEXO MASCULINO", "QTDE SEXO FEMININO", "QTDE SEXO NÃO INFORMADO"]
        ].sum(axis=1)

        st.write("Dados agrupados por forma de evasão:")
        st.dataframe(dfAgrupadoEvasao[["FORMA_EVASAO", "QTD_ALUNOS"]])

        # Seleciona as formas de evasão para os grupos "Formados" e "Evasão"
        evasoes_disponiveis = dfAgrupadoEvasao["FORMA_EVASAO"].unique()

        formados_selecionados = st.multiselect(
            "Selecione as formas de evasão para o grupo 'Formados'",
            options=evasoes_disponiveis,
            default=[]
        )

        evasao_selecionada = st.multiselect(
            "Selecione as formas de evasão para o grupo 'Evasão'",
            options=evasoes_disponiveis,
            default=[]
        )
        
        def categorizar_evasao(row):
            if row["FORMA_EVASAO"] in formados_selecionados:
                return "Formados"
            elif row["FORMA_EVASAO"] in evasao_selecionada:
                return "Evasão"
            else:
                return "Outros"  # Para as formas de evasão não agrupadas

        df_sem_outliers["FORMA_EVASAO_AGRUPADA"] = df_sem_outliers.apply(categorizar_evasao, axis=1)

        # Excluir todas as outras formas de evasão que não estão nos grupos "Formados" ou "Evasão"
        formas_inclusas = set(formados_selecionados + evasao_selecionada)

        # Filtrar o DataFrame para incluir apenas as formas de evasão selecionadas nos grupos "Formados" e "Evasão"
        dfAgrupadoEvasaoFiltrado = dfAgrupadoEvasao[dfAgrupadoEvasao["FORMA_EVASAO"].isin(formas_inclusas)]

        # Exibir o DataFrame filtrado para o usuário
        st.write("Dados filtrados para os grupos 'Formados' e 'Evasão':")
        st.dataframe(dfAgrupadoEvasaoFiltrado)

        # Apresentar a soma das colunas conforme os grupos "Formados" e "Evasão"
        dfGrupos = pd.DataFrame(columns=["EVASAO_CLASSIFICADA", "QTDE SEXO MASCULINO", "QTDE SEXO FEMININO", "QTDE SEXO NÃO INFORMADO", "QTD_ALUNOS"])

        # Agrupar os dados de acordo com as formas de evasão selecionadas
        for grupo_nome, formas in [("Formados", formados_selecionados), ("Evasão", evasao_selecionada)]:
            if formas:
                dfGrupo = dfAgrupadoEvasaoFiltrado[dfAgrupadoEvasaoFiltrado["FORMA_EVASAO"].isin(formas)]
                if not dfGrupo.empty:
                    dfGrupos = pd.concat([
                        dfGrupos,
                        pd.DataFrame([{
                            "EVASAO_CLASSIFICADA": grupo_nome,
                            "QTDE SEXO MASCULINO": dfGrupo["QTDE SEXO MASCULINO"].sum(),
                            "QTDE SEXO FEMININO": dfGrupo["QTDE SEXO FEMININO"].sum(),
                            "QTDE SEXO NÃO INFORMADO": dfGrupo["QTDE SEXO NÃO INFORMADO"].sum(),
                            "QTD_ALUNOS": dfGrupo["QTD_ALUNOS"].sum(),
                        }])
                    ], ignore_index=True)
        
        # Exibir os dados consolidados após agrupamento
        st.write("Dados consolidados por grupo 'Formados' e 'Evasão':")
        st.dataframe(dfGrupos[["EVASAO_CLASSIFICADA", "QTDE SEXO MASCULINO", "QTDE SEXO FEMININO", "QTDE SEXO NÃO INFORMADO", "QTD_ALUNOS"]])

        # Etapa de Mineração
        # Tabela de Contingência (relaciona os grupos "Formados" e "Evasão" por gênero)
        tabela_contingencia = pd.DataFrame({
            "Evasão": [
                dfGrupos[dfGrupos["EVASAO_CLASSIFICADA"] == "Evasão"]["QTDE SEXO MASCULINO"].sum(), 
                dfGrupos[dfGrupos["EVASAO_CLASSIFICADA"] == "Evasão"]["QTDE SEXO FEMININO"].sum()
            ],
            "Formação": [
                dfGrupos[dfGrupos["EVASAO_CLASSIFICADA"] == "Formados"]["QTDE SEXO MASCULINO"].sum(),
                dfGrupos[dfGrupos["EVASAO_CLASSIFICADA"] == "Formados"]["QTDE SEXO FEMININO"].sum()
            ]
        }, index=["Masculino", "Feminino"])

        # Verifica se a tabela de contingência contém zeros
        if (tabela_contingencia == 0).any().any():
            st.warning("A tabela de contingência contém células com valor zero. Aplicando suavização (adicionando 1 a cada célula).")
            tabela_contingencia_suavizada = tabela_contingencia + 1  # Suavização (adicionar 1 a todas as células)
        else:
            tabela_contingencia_suavizada = tabela_contingencia

        # Exibição da tabela suavizada
        st.write("### Tabela de Contingência após suavização:")
        st.dataframe(tabela_contingencia_suavizada)

        # Teste de Qui-Quadrado
        qui2, p_valor, graus_liberdade, frequencias_esperadas = chi2_contingency(tabela_contingencia_suavizada)

        frequencias_esperadas_suavizadas = np.where(frequencias_esperadas == 0, 1, frequencias_esperadas)

        # Exibição dos resultados
        st.write("### Teste de Qui-Quadrado: evasão vs gênero")
        st.write(f"**Estatística Qui-Quadrado: ** {qui2:.4f}")
        st.write(f"**P-valor: ** {p_valor:.4f}")
        st.write(f"**Graus de Liberdade: ** {graus_liberdade}")
        st.write("**Frequências Esperadas: **")
        st.dataframe(pd.DataFrame(frequencias_esperadas_suavizadas, index=["Masculino", "Feminino"], columns=["Evasão", "Formação"]))

        # Interpretação do p-valor
        if p_valor < 0.05:
            st.write("🔴 Existe uma relação estatisticamente significativa entre gênero e evasão.")
        else:
            st.write("🟢 Não há evidências estatísticas suficientes para afirmar que gênero influencia a evasão.")

        df_formados = df_sem_outliers[df_sem_outliers["FORMA_EVASAO_AGRUPADA"] == "Formados"]

        # Correlação de Pearson
        if "ANO_INGRESSO" not in df_sem_outliers.columns or "ANO_EVASAO" not in df_sem_outliers.columns:
            st.error("O arquivo precisa conter as colunas 'ANO_INGRESSO' e 'ANO_EVASAO' para calcular o tempo de formação.")
        elif df_formados.empty:
            st.warning("Não há dados para a forma de evasão 'Formados'.")
        else:
            # Criação de uma coluna de tempo de formação (ANO_EVASAO - ANO_INGRESSO)
            df_formados["TEMPO_FORMACAO"] = df_formados["ANO_EVASAO"] - df_formados["ANO_INGRESSO"]

            # Calcula o tempo total ponderado para cada gênero
            df_formados["TEMPO_FORMACAO_MASCULINO"] = df_formados["TEMPO_FORMACAO"] * df_formados["QTDE SEXO MASCULINO"]
            df_formados["TEMPO_FORMACAO_FEMININO"] = df_formados["TEMPO_FORMACAO"] * df_formados["QTDE SEXO FEMININO"]

            # Somamos os valores ponderados para obter o tempo total para cada gênero
            tempo_total_masculino = df_formados["TEMPO_FORMACAO_MASCULINO"].sum()
            tempo_total_feminino = df_formados["TEMPO_FORMACAO_FEMININO"].sum()

            # Em caso de necessidade, tire a # para exibir o tempo total de demora para a formação dos alunos de cada gênero            
            #st.text(f"Tempo total de formação (masculino): {tempo_total_masculino:.2f} anos")
            #st.text(f"Tempo total de formação (feminino): {tempo_total_feminino:.2f} anos")

            # Soma do total de alunos em cada gênero
            total_masculino = df_formados["QTDE SEXO MASCULINO"].sum()
            total_feminino = df_formados["QTDE SEXO FEMININO"].sum()

            # Calcula a média do tempo de formação para cada gênero
            media_tempo_masculino = tempo_total_masculino / total_masculino if total_masculino != 0 else 0
            media_tempo_feminino = tempo_total_feminino / total_feminino if total_feminino != 0 else 0

            st.write(f"### Média do tempo de formação: ")
            st.write(f"**Masculino:** {media_tempo_masculino:.2f} anos")
            st.write(f"**Feminino:** {media_tempo_feminino:.2f} anos")

            # Criação de uma coluna numérica para o gênero (0 = Masculino, 1 = Feminino)
            df_formados["SEXO_NUMERICO"] = df_formados.apply(lambda row: 0 if row["QTDE SEXO MASCULINO"] > 0 else 1, axis=1)

            # Calcula a correlação de Pearson entre o tempo de formação e o gênero
            corr_pearson, p_valor_pearson = pearsonr(df_formados["TEMPO_FORMACAO"], df_formados["SEXO_NUMERICO"])

            # Exibição dos resultados
            st.write(f"### Correlação de Pearson entre tempo de formação e gênero")
            st.write(f"**Correlação de Pearson:** {corr_pearson:.4f}")
            st.write(f"**P-valor:** {p_valor_pearson:.4f}")

            # Interpretação do p-valor
            if p_valor_pearson < 0.05:
                st.write("🔴 Existe uma relação estatisticamente significativa entre o tempo de formação e o gênero.")
            else:
                st.write("🟢Não há evidências estatísticas suficientes para afirmar que o tempo de formação é influenciado pelo gênero.")

    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")

