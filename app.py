import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain

from htmlTemplates import css, user_template, bot_template

# ============================================================
# PDF TEXT EXTRACTION
# Extracts text from multiple PDFs and calculates page count
# ============================================================
def load_documents(files):
    document_text=""
    page_count=0
    for file in files:
        pdf_reader=PdfReader(file)
        page_count+=len(pdf_reader.pages)
        for page in pdf_reader.pages:
            text=page.extract_text()
            if text:
                document_text+=text+"\n"
    return document_text,page_count

# ============================================================
# DOCUMENT CHUNKING
# Splits large documents into smaller overlapping text chunks
# ============================================================
def create_chunks(text):
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks=splitter.split_text(text)
    return chunks

# ============================================================
# VECTOR DATABASE
# Creates embeddings and stores them in FAISS vector database
# ============================================================
def create_vector_database(chunks):
    embeddings=HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store=FAISS.from_texts(
        texts=chunks,
        embedding=embeddings
    )
    return vector_store

# ============================================================
# RAG PIPELINE
# Connects Gemini LLM with FAISS similarity retriever
# ============================================================
def create_rag_chain(vector_store):
    llm=ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.2
    )
    memory=ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    retriever=vector_store.as_retriever(
        search_kwargs={"k":5}
    )
    rag_chain=ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )
    return rag_chain

# ============================================================
# CHAT HANDLER
# Processes user queries and displays AI responses
# ============================================================
def handle_query(question):
    response=st.session_state.chatbot(
        {"question":question}
    )
    chat_history=response["chat_history"]
    for index,message in enumerate(chat_history):
        if index%2==0:
            st.write(
                user_template.replace(
                    "{{MSG}}",
                    message.content
                ),
                unsafe_allow_html=True
            )
        else:
            st.write(
                bot_template.replace(
                    "{{MSG}}",
                    message.content
                ),
                unsafe_allow_html=True
            )

# ============================================================
# SESSION MANAGEMENT
# Stores chatbot state during application runtime
# ============================================================
def initialize_session():
    if "chatbot" not in st.session_state:
        st.session_state.chatbot=None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history=[]

# ============================================================
# STREAMLIT APPLICATION
# Handles UI, upload, processing and conversation workflow
# ============================================================
def main():
    load_dotenv()
    st.set_page_config(
        page_title="DocuMind AI",
        page_icon="📚"
    )
    st.write(css,unsafe_allow_html=True)
    initialize_session()
    st.title("📚 DocuMind AI")
    st.caption(
        "RAG-based Multi-PDF Assistant using Gemini + FAISS + LangChain"
    )
    question=st.text_input(
        "Ask anything from your PDFs"
    )
    if question:
        if st.session_state.chatbot:
            handle_query(question)
        else:
            st.warning(
                "Upload and process PDFs first"
            )
    with st.sidebar:
        st.header("Knowledge Base")
        uploaded_files=st.file_uploader(
            "Upload PDF documents",
            type=["pdf"],
            accept_multiple_files=True
        )
        if st.button("Process Documents"):
            if uploaded_files:
                with st.spinner("Building RAG pipeline..."):
                    # Extract PDF content
                    raw_text,pages=load_documents(uploaded_files)
                    # Create chunks
                    chunks=create_chunks(raw_text)
                    # Store embeddings in FAISS
                    vector_store=create_vector_database(chunks)
                    # Create Gemini RAG chatbot
                    st.session_state.chatbot=create_rag_chain(
                        vector_store
                    )
                st.success(
                    "Documents processed successfully"
                )
                st.info(
                    f"""
                    PDFs Processed: {len(uploaded_files)}
                    Pages Indexed: {pages}
                    Text Chunks Created: {len(chunks)}
                    """
                )
            else:
                st.error(
                    "Please upload PDFs first"
                )

# ============================================================
# APPLICATION START
# ============================================================
if __name__=="__main__":
    main()