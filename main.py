import pandas as pd
from flask import Flask, jsonify, request, redirect
from flasgger import Swagger
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from datetime import datetime, date

# ----- Etapa 02: CONFIGURAÇÃO INICIAL DA APLICAÇÃO
app = Flask('First API')
swagger = Swagger(app)

#Criar o banco de dados (arquivo em excel)
ARQUIVO_HISTORICO = 'Historico_chat.xlsx'

#Criar as colunas que esperamos em cada arquivo
COLUNAS_HISTORICO = ['id', "mensagem_usuario", 'mensagem_bot', 'data', 'hora']

#chave de api
GROQ_API_KEY = ''

#------ ETAPA03: FUNÇÕES AUXILIARES ------

#Funções para o banco de dados de histórico de chat
def get_historico_df():
    """Tentar ler o dataframe de histórico do excel. Se não exisir, cria um vazio"""
    try:
        return pd.read_excel(ARQUIVO_HISTORICO, sheet_name='Historico')
    except FileNotFoundError:
        return pd.DataFrame(columns=COLUNAS_HISTORICO)

def save_historico_df(df):
    """ Salva o dataframe de pessoas no excel """
    df.to_excel(ARQUIVO_HISTORICO, sheet_name='Historico', index=False)


# ------ ETAPA 04: ROTA DE REDIRECIONAMENTO
@app.route("/")
def index():
    """Redirecionar a rota principal '/' para a documentação '/apidocs/'"""
    #Se alguem acessar a URL Raiz, é redirecionado para a documentação
    return redirect("/apidocs")


#---- ETAPA 05: CRIAÇÃO DO ENDPOINT DE COMUNICAÇÃO COM CHATBOT
@app.route("/chat", methods=['POST'])
def conversar_bot():
    """
        Enviar uma mensagem para o chatbot (groq)
        ---
        tags:
            - Chatbot
        summary: Envia uma mensagem para o chatbot
        parameters:
            - in: body
              name: body
              required: true
              schema:
                id: ChatInput
                required: [mensagem]
                properties:
                    mensagem: {type: string, example: "Olá, qual a capital da França" }
        responses:
            200:
                description: Resposta do chatbot
            400: 
                description: Mensagem do usuário  faltando
            500:
                description: Erro ao conectar com a API            
    """
    
    dados = request.json
    mensagem_usuario = dados.get('mensagem')
    
    if not mensagem_usuario:
        return jsonify({"Erro": "A mensagem do usuário é obrigatória!"}), 400
    
    #1. Conexão com a IA (Groq)
    try:
        chat = ChatGroq(
            temperature=0.7,
            model='llama-3.1-8b-instant',
            api_key=GROQ_API_KEY #ponto de atenção de não funcionar
        )
        
        resposta_ia = chat.invoke([HumanMessage(content=mensagem_usuario)]).content
    except Exception as e:
        return jsonify({"erro": f"erro ao gerar resposta: {str(e)}"}), 500
    

    #2. guardar o historico de conversas (excel)
    # data_atual = datetime.now()
    
    # # df_hist = get_historico_df()
    
    # # novo_id = int(df_hist['id'].max()) + 1 if not df_hist.empty else 1
    
    # nova_linha = {
    #     # 'id': novo_id,
    #     'mensagem_usuario': mensagem_usuario,
    #     'mensagem_bot': resposta_ia,
    #     'data': data_atual.strftime("%d/%m/#Y"),
    #     'hora': data_atual.strftime("%H:%M:%S")
    # }
    
    # #ADICIONAR A NOVA LINHA NO ARQUIVO
    # # df_hist = pd.concat([df_hist, pd.DataFrame([nova_linha])], ignore_index=True)
    # # save_historico_df(df_hist)
    
    #RETORNAR NA API A RESPOSTA
    return jsonify({'Resposta': resposta_ia}),  200     
    
#Execução da aplicação
if __name__ == "__main__":
    app.run(debug=True)