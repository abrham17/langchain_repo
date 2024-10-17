from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda, RunnableParallel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import os
from langchain.memory import ConversationSummaryBufferMemory

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Initialize model with appropriate context
model = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash', context="You are a programming language expert. Please provide comprehensive and informative responses to questions about programming languages, their features, and their applications.")

# Define prompt templates with clear instructions
base_prompt = ChatPromptTemplate(
    messages=[
        ("system", "You are a programming language expert. Please provide comprehensive and informative responses to questions about programming languages, their features, and their applications."),
        ("user", "{product}"),
        ("assistant", "I will help you with what I can.")
    ]
)

def analyze_pros(product):
    return ChatPromptTemplate(
        messages=[
            ("system", "Please provide a comprehensive list of the advantages and benefits of the given programming language."),
            ("user", "{product}"),
            ("assistant", "I will help you with what I can.")
        ]
    )

def analyze_cons(product):
    return ChatPromptTemplate(
        messages=[
            ("system", "Please provide a comprehensive list of the potential drawbacks and limitations of the given programming language."),
            ("user", "{product}"),
            ("assistant", "I will help you with what I can.")
        ]
    )

def combine_pros_cons(pros, cons):
    return f"Pros:\n{pros}\n\nCons:\n{cons}"

def conversation(product):
    # Initialize memory if needed
    memory = ConversationSummaryBufferMemory(memory_key="history", llm=model, return_messages=True)

    # Create Runnables for pros and cons analysis with clear instructions
    pros = RunnableLambda(
        lambda x: analyze_pros(product) | model | StrOutputParser()
    )
    cons = RunnableLambda(
        lambda x: analyze_cons(product) | model | StrOutputParser()
    )

    # Define the chain for conversation with clear instructions
    chain = (
        base_prompt
        | model
        | StrOutputParser()
        | RunnableParallel(branches={'pros': pros, 'cons': cons})
        | RunnableLambda(lambda x: combine_pros_cons(x['branches']['pros'], x['branches']['cons']))
    )

    # Invoke the chain with the user's question
    response = chain.invoke({'product': product})
    print(response)

def user_question():
    while True:
        product_input = input("Enter your choice product: ") 
        if product_input == "exit":
            break

        conversation(product_input)

if __name__ == "__main__":
    user_question()