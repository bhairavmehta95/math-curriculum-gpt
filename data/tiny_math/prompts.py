# type: ignore
import textwrap


BOOK_FOREWARD_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are currently writing the foreward for the book:

#  Title: {title}

Notes:
- Keep the tone academic, meaning you should never sign the name or refer to the author.
- The book is being written in the popular Markdown format.
- The context may be truncated and is meant only to provide a starting point. Feel free to expand on it or take the response in any direction that fits the prompt, but keep it in a voice that is appropriate for a math student who is being introducted to the subject.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Begin your response with `## Foreward`

### Response:
"""


BOOK_NEW_SECTION_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are currently writing the chapter and section shown below:

#  Title: {title}

## Chapter: {chapter}

### Section: {section}

### Subsection {subsection}

To assist you in writing the chapter, you have been provided with some recent context from the book below.

### Last textbook section content:
```
{book_context}
```

Notes:
- Keep the tone academic, meaning you should never sign the name or refer to the author.
- The book is being written in the popular Markdown format.
- The context may be truncated and is meant only to provide a starting point. Feel free to expand on it or take the response in any direction that fits the prompt, but keep it in a voice that is appropriate for a math student who is being introducted to the subject.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$
- Since you are starting a new section, include `### [Section Title]` to start, with a brief description of the section.
- To start a new subsection, include `#### [Subsection Title]`
`

### Response:
"""


BOOK_CONTINUING_SECTION_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are currently continuing writing the chapter and section shown below:

#  Title: {title}

## Chapter: {chapter}

### Section: {section}

### Subsection (optional): {subsection}


To assist you in writing the chapter, you have been provided with the last subsection contents bellow:

### Last textbook section content:
```
{book_context}
```

Notes:
- Keep the tone academic, meaning you should never sign the name or refer to the author.
- The book is being written in the popular Markdown format.
- The context may be truncated and is meant only to provide a starting point. Feel free to expand on it or take the response in any direction that fits the prompt, but keep it in a voice that is appropriate for a math student who is being introducted to the subject.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$
- Since you are NOT starting a new section, simply start a new subsection using `#### [Subsection Title]`
`

### Response:
"""

# # Example Usage
# BOOK_BULK_PROMPT.format(
#     title=textbook,
#     chapter=chapter,
#     section=section,
#     subsection=subsection or "",
#     related_context=related_context[
#         : self.max_related_context_to_sample
#     ],
#     book_context=prev_response[: self.max_prev_snippet_to_sample],
# )

# Prompt for the LLM
BOOK_CHAPTER_SUMMARY_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are tasked with writing a several paragraph CONCLUSION FOR THE CHAPTER shown below:

#  Title: {title}

## Chapter: {chapter}

To assist you in this task, you have been provided the context bellow:

### Previously written chapter:
```
{book_context}
```

Following your authoring of the conclusion, write 3 exercises which align with the context of the chapter. Format each with a header `#### Exercise 1` etc.

Notes:
- Keep the tone academic, meaning you should never sign the name or refer to the author.
- The book is being written in the popular Markdown format.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$
- Start the conclusion the Chapter with a header that reads `### Conclusion`, start the exercises with a header that reads `### Exercises`.

`

### Response:
"""

# # Example Usage
# chapter_summary_prompt = BOOK_CHAPTER_SUMMARY_PROMPT.format(
#     title=textbook,
#     chapter=current_chapter,
#     book_context=f"Chapter outline:\n{prev_chapter_config}",  # ToC for Chapter
# )


# Prompt for the LLM
BOOK_CHAPTER_INTRODUCTION_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are currently writing a several paragraph introduction for the chapter shown below (avoid going into too much detail):

#  Title: {title}

## Chapter: {chapter}

To assist you in this task, you have been provided the context which will be covered in this chapter:

### Chapter section topics covered:
```
{book_context}
```

Notes:
- Keep the tone academic, meaning you should never sign the name or refer to the author.
- The book is being written in the popular Markdown format.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$
- Include the chapter title at the top of your output, formatted as  `## Chapter: [Title]`,  `### Introduction` below that.
`

### Response:
"""

# # Example Usage
# chapter_intro_prompt = BOOK_CHAPTER_INTRODUCTION_PROMPT.format(
#     title=textbook,
#     chapter=chapter,
#     book_context=str(prev_chapter_config), # ToC for Chapter
# )
