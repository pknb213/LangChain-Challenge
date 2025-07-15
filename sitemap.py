import streamlit as st
from bs4 import BeautifulSoup
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import SitemapLoader
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

st.set_page_config(
    page_title="Site GPT",
    page_icon="？",
)

# 처음 로딩 시, 세션 상태에 키가 없으면 빈 값 설정
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = ''

# 입력 필드
api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.session_state['openai_api_key'])

# 키가 바뀌었을 때 상태 저장 후 rerun
if api_key and api_key != st.session_state['openai_api_key']:
    st.session_state['openai_api_key'] = api_key
    st.rerun()

# 키가 없으면 에러
if not st.session_state['openai_api_key']:
    st.error("Please enter your OpenAI API Key.")
    st.stop()

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=st.session_state['openai_api_key'],
    temperature=0.1,
    streaming=False,
    callbacks=[StreamingStdOutCallbackHandler()],
)

answers_prompt = ChatPromptTemplate.from_template("""
    Using ONLY the following context answer the user's question. If you can't just say you don't know, don't make anything up.

    Then, give a score to the answer between 0 and 5.
    If the answer answers the user question the score should be high, else it should be low.
    Make sure to always include the answer's score even if it's 0. And Please, Answer write to KOREAN.

    Context: {context}

    Examples:

    Question: How far away is the moon?
    Answer: The moon is 384,400 km away.
    Score: 5

    Question: How far away is the sun?
    Answer: I don't know
    Score: 0

    Your turn!
    Question: {question}
""")


# ua = UserAgent()

def get_answers(inputs):
    docs = inputs["docs"]
    question = inputs["question"]
    answers_chain = answers_prompt | llm
    return {
        "question": question,
        "answers": [
            {
                "answer": answers_chain.invoke(
                    {
                        "question": question,
                        "context": doc.page_content
                    }
                ).content,
                "source": doc.metadata["source"],
                # "date": doc.metadata["lastmod"]
            } for doc in docs
        ]
    }


choose_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Use ONLY the following pre-existing answers to answer the user's question.
            Use the answers that have the highest score (more helpful) and favor the most recent ones.
            Cite sources and return the sources of the answers as they are, do not change them.
            Answers: {answers}
            """,
        ),
        ("human", "{question}"),
    ]
)


def choose_answer(inputs):
    answers = inputs["answers"]
    question = inputs["question"]
    choose_chain = choose_prompt | llm
    condensed = "\n\n".join(
        f"Answer: {answer['answer']}\n"
        f"Source: {answer['source']}\n"
        # f"Date:{answer['date']}\n"
        f"" for answer in answers)
    return choose_chain.invoke({
        "question": question,
        "answers": condensed
    })


def parse_page(soup: BeautifulSoup):
    header = soup.find("header")
    tooter = soup.find("tooter")
    if header:
        header.decompose()
    if tooter:
        tooter.decompose()
    return (
        str(soup.get_text())
        .replace("\n", " ")
        .replace("\xa0", " ")
        .replace("CloseSearch Submit Blog", "")
    )


@st.cache_resource(show_spinner="Loading Website...")
def load_website(url):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000,
        chunk_overlap=200,
    )
    loader = SitemapLoader(
        url,
        filter_urls=[
            r"^(.*\/ai-gateway\/).*",
            r"^(.*\/vectorize\/).*",
            r"^(.*\/workers-ai\/models\/llama-2-7b-chat-fp16\/).*",
        ],
        parsing_function=parse_page,
    )
    loader.requests_per_second = 2
    docs = loader.load_and_split(text_splitter=splitter)
    # st.write(docs)
    vector_store = FAISS.from_documents(
        docs,
        OpenAIEmbeddings(openai_api_key=st.session_state['openai_api_key'])
    )
    return vector_store.as_retriever()


st.title("Site GPT")

if 'url' not in st.session_state:
    st.session_state['url'] = 'https://developers.cloudflare.com/sitemap-0.xml'
    st.rerun()
else:
    url = st.session_state['url']
    if ".xml" not in url:
        with st.sidebar:
            st.error("Please provide a sitemap URL")
    else:
        retriever = load_website(url)
        query = st.text_input("Ask a question to the Cloudflare!")
        if query:
            chain = ({
                         "docs": retriever,
                         "question": RunnablePassthrough(),
                     }
                     | RunnableLambda(get_answers)
                     | RunnableLambda(choose_answer))

            result = chain.invoke(query)
            st.markdown(result.content.replace("$", "\$"))
