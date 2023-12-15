# %%
from AutoCorrectionOutputParser import AutoCorrectionOutputParser, get_check_config, get_response_schema
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

check_list = get_check_config(config_path="CHECK_CONFIG.ini")

response_schema = get_response_schema(check_config=check_list)

llm = ChatOpenAI(
    model_name      = "gpt-3.5-turbo-1106",
    openai_api_base = "your openai base url here",
    api_key         = "you openai api here"
)


prompt = PromptTemplate.from_template(
    "Please analysis the sentence's emotion, action and topic."
    "sentence: {sentence}"
    "\n\n{format_instructions}"
)

auto_parser = AutoCorrectionOutputParser(
    check_list       = check_list,
    response_schemas = response_schema,
    llm              = llm,
    verbose          = True,
    max_retry        = 3
)

chain = LLMChain(
    llm     = llm,
    prompt  = prompt,
    verbose = True
)

kwargs = {
    "sentence": "Despite feeling a mix of excitement and anxiety, I confidently approached the stage, took a deep breath, and delivered a heartfelt speech about the importance of mental health awareness in today's society.",
    "format_instructions": auto_parser.get_format_instructions()
}
res = chain.run(**kwargs)

auto_parser.parse(text = res, instructions=prompt.format_prompt(**kwargs).text)
# %%
