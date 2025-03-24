# API_AnaliseEvasao
API interativa para análise de dados educacionais, com ênfase na sub-representação das mulheres na ciência e na tecnologia.

## Tecnologias Usadas

    Streamlit: Para criar a interface interativa da aplicação.
    Pandas: Para manipulação e análise de dados.
    Numpy: Para cálculos numéricos.
    Seaborn: Para visualização estatística e gráficos.
    Matplotlib: Para criação de gráficos personalizados.
    SciPy: Para realizar testes estatísticos, como o teste de qui-quadrado e o coeficiente de correlação de Pearson.

## Instalação
### Pré-requisitos

Você precisa ter o Python 3.x instalado. Para instalar as dependências, siga os passos abaixo.

    git clone https://github.com/usuario/nome-do-repositorio.git

Acesse o diretório do projeto:

    cd nome-do-repositorio

Crie um ambiente virtual:

    python -m venv venv

Ative o ambiente virtual:

  No Windows:

    venv\Scripts\activate

  No Linux/Mac:

    source venv/bin/activate

Instale as dependências:

    pip install -r requirements.txt

    pip install streamlit pandas numpy seaborn matplotlib scipy

## Como Usar

Para rodar o aplicativo Streamlit, utilize o seguinte comando:

    streamlit run app.py

Isso abrirá o aplicativo no seu navegador padrão, geralmente em http://localhost:8501.

No navegados, você poderá:

 - Carregar seus próprios conjuntos de dados (arquivos CSV, por exemplo).

 - Realizar testes estatísticos: Teste de Qui-quadrado e Coeficiente de Correlação de Pearson.
