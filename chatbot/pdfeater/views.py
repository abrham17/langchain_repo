from django.http import JsonResponse
from langchain.memory import ConversationBufferMemory
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import markdown


# Initialize Google API
GOOGLE_API_KEY = "your-api-key"
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(model = 'models/gemini-1.5-flash')
def index(request):
    return render(request, 'pdfeater/index.html')
@csrf_exempt
def upload_and_process(request):
    if request.method == 'POST':
        try:
            files = request.FILES.getlist('files')
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            upload_dir = os.path.join(base_dir, 'uploads')
            
            # Create upload directory if it doesn't exist
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Save and process PDFs
            documents = []
            for file in files:
                if file.name.endswith('.pdf'):
                    file_path = os.path.join(upload_dir, file.name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    
                    # Load PDF
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
            
            if documents:
                # Split documents
                text_splitter = CharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=0
                )
                texts = text_splitter.split_documents(documents)
                
                # Create embeddings
                embedding = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                
                # Store in Chroma
                Chroma.from_documents(
                    documents=texts,
                    embedding=embedding,
                    persist_directory=os.path.join(base_dir, 'Chroma')
                )
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Successfully processed {len(files)} PDFs'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'error': 'No valid PDF files found'
                })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_answer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question')
            language = data.get('language')
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Initialize embedding and load vector store
            embedding = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            vectorstore = Chroma(
                embedding_function=embedding,
                persist_directory=os.path.join(base_dir, 'Chroma')
            )
            
            # Create QA chain
            memory = ConversationBufferMemory( memory_key='chat_history' , return_messages=True)
# Set up the prompt for the retrieval chain
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant. Please answer the following question in {language}."),
                ("human", "{question}")
            ])

            # Initialize the RetrievalQA chain directly with the prompt
            qa_chain = RetrievalQA.from_chain_type(
                llm=model,
                retriever=vectorstore.as_retriever(),
                chain_type="stuff",
                memory=memory
            )

            # Run the query and retrieve the answer
            result = qa_chain.invoke({"query": question})
            print(result)
            # If needed, use markdown formatting
            answer = markdown.markdown(result['result'])
            return JsonResponse({'answer': answer})

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
