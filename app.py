from flask import Flask, render_template, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain.vectorstores import Pinecone
import pinecone
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from src.prompt import *
import os

app = Flask(__name__)

load_dotenv()
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
embeddings = download_hugging_face_embeddings()
index_name="medical-bot"

from langchain_pinecone import PineconeVectorStore

pinecone_store = PineconeVectorStore(embedding=embeddings, pinecone_api_key=PINECONE_API_KEY, index_name=index_name)

docsearch = pinecone_store.from_existing_index(index_name = index_name, embedding=embeddings)

PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
chain_type_kwargs={"prompt": PROMPT}

llm=CTransformers(model="model/llama-2-7b-chat.ggmlv3.q4_0.bin",
model_type="llama",
config={'max_new_tokens':512,
'temperature' :0.8}
)

qa=RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=docsearch.as_retriever(search_kwargs={'k': 2}),
    return_source_documents=True,
    chain_type_kwargs=chain_type_kwargs
)

@app.route("/")
def index():
    return render_template("chat.html")

if __name__ == "__name__":
    app.run(debug=True)


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print(input)
    result=qa({"query": input})
    print("Response : ", result["result"])
    return str(result["result"])

# pinecone_store = PineconeVectorStore(embedding=embeddings, pinecone_api_key=PINECONE_API_KEY, index_name=index_name)
# docsearch=pinecone_store.from_texts(
# [t.page_content for t in text_chunks],


# embeddings,
# index_name=index_name,


# )   
