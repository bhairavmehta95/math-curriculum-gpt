import os
import yaml
import random
import tiktoken

import openai
import logging
import time
import re
import json

openai.api_key = os.environ["OPENAI_API_KEY2"]

n_tokens = 0


def with_retry(func, max_retries=3):
    """Attempt to execute the provided function up to max_retries times."""
    for _ in range(max_retries):
        try:
            return func()
        except Exception as e:
            logging.warning(f"Exception encountered: {e}. Retrying...")
            time.sleep(5)
    raise ValueError(f"Failed to execute {func.__name__} after {max_retries} retries.")


def get_subtopics(prompt):
    global n_tokens
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {
                "role": "system",
                "content": "You are a prolific, expert mathematics education textbook writer, writing a new book.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=1.0,
        max_tokens=50,
    )

    n_tokens += response["usage"]["total_tokens"]
    return response.choices[0].message.content


prompt = """Take a deep breath, and think step by step.\nImagine you are math educational textbook expert, writing a math textbook on the subject of "{course}". You are looking to expand the table of contents in the book titled: {course}, and are writing a chapter on {topic}. In the subsection for {subtopic}, what are {number} key subsections that you would include in the subtopic on {subtopic}, that might be representative in helping a math student grasp the subject completely? Write them down below in a list format, with each item on a new line. Include no extra commentary, and do not number the list, but instead, separate them on new lines.
"""


tokenizer = tiktoken.get_encoding("cl100k_base")


def generate_toc():
    for i, file in enumerate(os.listdir("raw")):
        print(f'{i}/{len(os.listdir("raw"))}, Tokens Used=', n_tokens)

        if not file.endswith(".yaml") or (
            file.endswith(".yaml")
            and file.replace(".yaml", ".md") in os.listdir("generated")
        ):
            continue

        if os.path.exists(os.path.join("jsonl", file.replace(".yaml", ".jsonl"))):
            continue

        else:
            try:
                yaml_data = open(os.path.join("raw", file), "r").read()
                data = yaml.safe_load(yaml_data)
            except Exception as e:
                print("Error reading file", file, e)
                continue
            course = list(data["course"].keys())[0].strip()

            for topics in data["course"][course]["topics"]:
                for topic in topics.keys():
                    for subtopic in topics[topic]["subtopics"]:
                        formatted_prompt = prompt.format(
                            course=course,
                            topic=topic,
                            subtopic=subtopic,
                            number=random.randint(2, 5),
                        )

                        subsubtopics_string = with_retry(
                            lambda: get_subtopics(formatted_prompt)
                        )
                        subsubtopics = subsubtopics_string.split("\n")

                        with open(
                            os.path.join("jsonl", file.replace(".yaml", ".jsonl")), "a"
                        ) as f:
                            for subsubtopic in subsubtopics:
                                f.write(
                                    json.dumps(
                                        {
                                            "course": course.strip(),
                                            "chapter": topic.strip(),
                                            "topic": subtopic.strip(),
                                            "subtopic": re.sub(
                                                r"[^a-zA-Z0-9\s,]+", "", subsubtopic
                                            ).strip(),
                                        }
                                    )
                                    + "\n"
                                )

                        with open(
                            os.path.join("jsonl", "all_textbooks.jsonl"), "a"
                        ) as f:
                            for subsubtopic in subsubtopics:
                                f.write(
                                    json.dumps(
                                        {
                                            "course": course.strip(),
                                            "chapter": topic.strip(),
                                            "topic": subtopic.strip(),
                                            "subtopic": re.sub(
                                                r"[^a-zA-Z0-9\s,]+", "", subsubtopic
                                            ).strip(),
                                        }
                                    )
                                    + "\n"
                                )


def separate_into_individual():
    current_book = None
    file_append_or_write = None
    with open("jsonl/all_textbooks.jsonl"):
        for line in open("jsonl/all_textbooks.jsonl"):
            data = json.loads(line)
            if data["course"] != current_book:
                current_book = re.sub(r"[^a-zA-Z0-9\s,]+", "", data["course"]).strip()

            with open(f"jsonl/individual-books/{current_book}.jsonl", "a") as f:
                f.write(json.dumps(data) + "\n")


separate_into_individual()
