import streamlit as st
import langchain 
from langchain_google_genai import ChatGoogleGenerativeAI 
import os 
from PyPDF2 import PdfReader 
from langchain.memory import ConversationBufferMemory 
from langchain_text_splitters import CharacterTextSplitter 
from langchain.vectorstores import FAISS 
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
llm = ChatGoogleGenerativeAI(model = 'models/gemini-1.5-flash')

def get_pdf_text(pdf_files):
    """Extract text from PDF files"""
    text = ""
    for pdf in pdf_files:
        pdfreader = PdfReader(pdf)
        for page in pdfreader.pages:
            text += page.extract_text()
    return text

def split_text_into_chunks(raw_text):
    """Split raw text into manageable chunks"""
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)
    return chunks

def create_vector_database(chunks):
    """Create vector database using Hugging Face embeddings"""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(texts=chunks, embedding=embeddings)
    return vector_store

def create_conversation_chain(vector_store):
    """Create conversation chain with buffer memory and vector store"""
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)
    retriever = vector_store.as_retriever()  # Create retriever from vector store
    conversation_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # You can also use other chain types like "map_reduce"
        retriever=retriever,  # Add retriever
        memory=memory
    )
    return conversation_chain

def handle_user_question(user_question):
    response = st.session_state.conversation_chain({"query": user_question})
    st.session_state.chathistory = response['history']
    
    for i , value in enumerate(st.session_state.chathistory):
        st.write(value.content)

def main():
    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:")
    st.header("Chat with multiple PDFs :books:")

    user_question = st.text_input("Ask a question about your document")

    if 'conversation_chain' not in st.session_state:
        st.session_state.conversation_chain = None 
    if 'chathistory' not in st.session_state:
        st.session_state.chathistory = None

    if user_question:
        handle_user_question(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader("Upload your PDFs here and click 'Process'", accept_multiple_files=True)

        if st.button('Process'):
            if pdf_docs:
                with st.spinner("Processing..."):
                    # Get text from PDFs
                    raw_text = get_pdf_text(pdf_docs)

                    # Create chunks from raw text
                    chunks = split_text_into_chunks(raw_text)

                    # Create a vector store
                    vector_store = create_vector_database(chunks)

                    # Create a conversation chain and store it in session state
                    st.session_state.conversation_chain = create_conversation_chain(vector_store)

if __name__ == "__main__":
    main()