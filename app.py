# Bring in deps
import os 
apikey = os.getenv('OPENAI_API_KEY')

import streamlit as st 
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain 
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper 

os.environ['OPENAI_API_KEY'] = apikey

# App framework
st.title('🦜🔗 YouTube GPT Creator')
prompt = st.text_input('Plug in your prompt here') 

# Prompt templates
title_template = PromptTemplate(
    input_variables = ['topic'], 
    template='write me a youtube video title about {topic}'
)
"""
Act as an Expert Humanitarian Aid Expert and Policymaker regarding food security and food waste as a sustainability development goal based on the most recent research statistics for food wastage and the bottom line of Malaysian societal layers. With an exceptional grasp of communicating the dynamics of food wastage and the cause and effects of it to the general public, with focused efforts and expertise into a sort of comprehensive and convincing design challenge. Being imbued with a full spectrum of innovation with a human-centered design ethos, create a comprehensive 6 question survey with 5 closed ended questions and 1 select all that apply question based on collecting data of the 4-5 main topics including but not limited to

1. Do you support the Menu Rahmah initiative (the idea of giving away food for a lower price to the community)? (clarify this better, like what the origins of menu rahmah was, how it was a social media trend and the bigger picture of the need for cheaper foodstuff) (Thoughts on the sustainability of this type of trend)

2. Do you think Food delivery apps are the reason why companies or restaurants pre-cook the food? (How would you measure the impact e-hailing food delivery services have made on your willingness to purchase groceries - Towards community, friends and family)

3. Would you be more likely to dine at a restaurant if you knew they had a program to donate excess food to underprivileged people?

4. Do you think this method is profitable for the company? (Identifying the consumer propensity to continue utilizing the goods and services of e-hailing and food delivery companies. + Providing grabfood and similar motorists a way to earn a living.

5. Do you think food delivery apps are the reason why grocery stores have extra food or products.

6. If you are to witness extra food being made in a restaurant, and the idea of Menu Rahmah seems like a good idea, how much would you charge the underprivileged for this food.
"""
script_template = PromptTemplate(
    input_variables = ['title', 'wikipedia_research'], 
    template='write me a youtube video script based on this title TITLE: {title} while leveraging this wikipedia reserch:{wikipedia_research} '
)

# Memory 
title_memory = ConversationBufferMemory(input_key='topic', memory_key='chat_history')
script_memory = ConversationBufferMemory(input_key='title', memory_key='chat_history')


# Llms
llm = OpenAI(temperature=0.9) 
title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True, output_key='title', memory=title_memory)
script_chain = LLMChain(llm=llm, prompt=script_template, verbose=True, output_key='script', memory=script_memory)

wiki = WikipediaAPIWrapper()

# Show stuff to the screen if there's a prompt
if prompt: 
    title = title_chain.run(prompt)
    wiki_research = wiki.run(prompt) 
    script = script_chain.run(title=title, wikipedia_research=wiki_research)

    st.write(title) 
    st.write(script) 

    with st.expander('Title History'): 
        st.info(title_memory.buffer)

    with st.expander('Script History'): 
        st.info(script_memory.buffer)

    with st.expander('Wikipedia Research'): 
        st.info(wiki_research)