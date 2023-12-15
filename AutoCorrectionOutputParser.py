# %%
from langchain.prompts import PromptTemplate
from langchain.output_parsers.json import parse_and_check_json_markdown
from langchain.schema.language_model import BaseLanguageModel
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.chains import LLMChain
import configparser
from typing import List, Dict, Any

def get_check_config(config_path: str) -> List[Dict[str, Any]]:
    config = configparser.ConfigParser()
    config.read(config_path)

    check_config = []
    sections = config.sections()
    for section in sections:
        typing = config.get(section, 'type')
        candidate_label = [
            label.lstrip().strip() 
            for label in config.get(section, 'candidate').split(',')
        ]
        if typing == 'boolean':
            candidate_label = [True, False]
        check_config.append({
            'check_name': section,
            'check_type': typing,
            'check_value': candidate_label
        })
    return check_config

def get_response_schema(check_config: dict) -> List[ResponseSchema]:
    response_schema = []
    for check_dict in check_config:
        response_schema.append(
            ResponseSchema(
                name        = check_dict['check_name'],
                type        = check_dict['check_type'],
                description = f"candidate label: {check_dict['check_value']}"
            )
        )
    return response_schema

class AutoCorrectionOutputParser(StructuredOutputParser):
    response_schemas: List[ResponseSchema]
    check_list: List[Dict[str, Any]]
    llm: BaseLanguageModel
    verbose: bool = False   
    prompt: str = 'AUTOCORRECTION.txt'
    max_retry: int = 3

    def chain(self, prompt: PromptTemplate) -> LLMChain:
        return LLMChain(llm = self.llm, prompt = prompt, verbose = self.verbose)
    
    def _attr_check(self, result: Dict, check_dict: Dict[str, Any]) -> bool:
        key = check_dict['check_name']
        value = result[key]
        if value not in check_dict['check_value']:
            return f"KeyError! {key} must in {check_dict['check_value']}, but your answer is {value}!\n"
        else:
            return ""
    
    def _fix(self, instructions: str, result: Dict, error: str) -> str:
        prompt = PromptTemplate.from_template(open(f'{self.prompt}', 'r').read())
        response = self.chain(prompt=prompt).run(
            completion   = result,
            instructions = instructions,
            error        = error,
        )
        return response
    
    def parse(self, text: str, instructions: str) -> Any:
        expected_keys = [rs.name for rs in self.response_schemas]
        try:
            result = parse_and_check_json_markdown(text, expected_keys)
        except Exception as e:
            # process format error
            result = self._fix(instructions=instructions, result = text, error = e)
        # check key, value
        retry_number = 0
        while retry_number < self.max_retry:
            error = ""
            for check in self.check_list:
                error += self._attr_check(result=result, check_dict=check)
            if len(error) > 0:
                retry_number += 1
                fix_result = self._fix(instructions=instructions, result = text, error = error)
                # process format error
                try:
                    fix_result = parse_and_check_json_markdown(fix_result, expected_keys)
                except Exception as e:
                    
                    fix_result = self._fix(instructions=instructions, result = fix_result, error = e)
                result.update(fix_result)
            else:
                break
        return result