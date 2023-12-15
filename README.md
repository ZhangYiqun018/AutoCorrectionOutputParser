# 🏹AutoCorrectionOutputParser for LangChain

简介: `AutoCorrectionOutputParser`旨在解决在使用语言模型时遇到的json格式化输出和分类任务脱靶的问题。它能够自动处理语言模型的输出结果，使其符合特定的格式要求，并通过分类候选项对输出进行校正，确保输出结果在候选项范围内。

Desc: `AutoCorrectionOutputParser` is an open-source script designed to address the issues of formatting output and off-target classification in the use of language models. It automates the processing of language model output to meet specific formatting requirements and corrects the output based on a set of candidate options, ensuring that the output falls within the candidate range.

## 📋使用指南
1. 将预备格式化输出的属性以及候选项添入配置文件中(default: CHECK_CONFIG.ini)
2. 使用`get_check_config`函数读取配置文件
3. 使用`get_response_schema`函数根据配置文件获取任务配置列表(建议自定义实现，因为在实际应用中，并不是所有的json输出都需要被检验是否脱靶)
4. 定义`AutoCorrectionOutputParser`对象, 获取`format_instructions`,将解析器与prompt联动(可以参考`example.py`)
5. 使用`AutoCorrectionOutputParser.parse`方法解析语言模型生成的结果


## 📌Use Case
`example.py`中提供了一个句子级别同时进行情感(7选1)、动作(6选1)、主题(8选1)的分类任务样例。

使用chatgpt-3.5-turbo在解决此类较为复杂的分类问题时，偶尔会出现脱靶问题:

输入:
```markdown
Please analysis the sentence's emotion, action and topic.
sentence: Despite feeling a mix of excitement and anxiety, I confidently approached the stage, took a deep breath, and delivered a heartfelt speech about the importance of mental health awareness in today's society.

The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "```json" and "```":

```json
{
	"emotion": string  // candidate label: ['joyful', 'sad', 'neutral', 'excited', 'content', 'surprised', 'anxious']
	"action": string  // candidate label: ['asking', 'explaining', 'requesting', 'discussing', 'sharing', 'others']
	"topic": string  // candidate label: ['sports', 'technology', 'entertainment', 'health', 'business', 'history', 'political', 'others']
}
```
输出:
```json
{
	"emotion": "excited",
	"action" : "delivering",  # 脱靶
	"topic"  : "mental health awareness" # 脱靶
}
```

使用`AutoCorrectionOutputParser`自动解析:
```markdown
Above, the Completion did not satisfy the constraints given in the Instructions.
Error: 
--------------
KeyError! action must in ['asking', 'explaining', 'requesting', 'discussing', 'sharing', 'others'], but your answer is delivering!
KeyError! topic must in ['sports', 'technology', 'entertainment', 'health', 'business', 'history', 'political', 'others'], but your answer is mental health awareness!
--------------
Please try again. Please only responsd with an answer that satisfies the contraints laid out in the Instructions:
```
output:
```json
{
    "emotion": "excited",
    "action" : "sharing",
    "topic"  : "health"
}
```

## ⛔声明
本脚本只能在很大程度上缓解脱靶现象，由于语言模型的幻觉和上下文记忆问题，脱靶现象在现阶段并不可能完全解决。

经作者简单测试，使用ChatGLM3-6B等小尺寸sft模型作为基座模型时，使用本脚本也可以有效的缓解脱靶问题。