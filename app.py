from flask import Flask, jsonify, render_template, request
import requests
from pinecone.grpc import PineconeGRPC as Pinecone

################################################################################################
# Import necessary libraries

PINECONE_API_KEY="ef7da690-c8fa-4156-8bfe-16292e8c7b5d"

from langchain_groq import ChatGroq

llm = ChatGroq(
    temperature=0, 
    groq_api_key='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', 
    model_name="llama-3.1-70b-versatile"
)

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "sharia-compliant"

# Define function to get query embedding
def get_query_embedding(query: str):
    query_embedding = pc.inference.embed(
    model="multilingual-e5-large",
    inputs=[query],
    parameters={
        "input_type": "query"
    }
)
    return query_embedding

def filter_results(query_embedding):
    index = pc.Index(index_name)

    results = index.query(
    namespace="sharia-namespace",
    vector=query_embedding[0].values,
    top_k=1,
    include_values=True,
    include_metadata=True
)
    return results['matches'][0]['metadata']['text']

# Define function to search Pinecone index
def search_results(question):
    query_embedding=get_query_embedding(question)

    return filter_results(query_embedding)


# Function to ask a question based on file content
def ask_question(question):
    
    final_data=search_results(question)
    new_prompt=f"""
You are a knowledgeable Islamic chatbot that provides accurate and respectful answers about Islamic principles and practices. Always start responses with appropriate Arabic phrases when answering questions about Islam. and if need to use my given data.
Data: {final_data[3:]} 
Question: ${question}

Please provide a response that:
1. Starts with relevant Arabic phrases in Arabic font.(for Islamic topics) 
2. Gives clear, accurate information about the topic. 
3. Cites Islamic sources when appropriate . 
4. Is respectful and helpful to the user. 
5. Keep responses concise but informative . 
6. If question is qbout gretting so reply only gretting. 
7. If question is not about Islamic topics so reply only that --> this is not related to Islamic topics <--.
8. use \\n for new line
    """
    response = llm.invoke(new_prompt)
    return response.content

   
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask_question', methods=['POST'])
def answer():
    data = request.get_json()
    question = data.get('question', '')
    
    # Example response; replace with your logic
    response =ask_question(question)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)

