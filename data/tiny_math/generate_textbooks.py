from prompts import (
    BOOK_FOREWARD_PROMPT,
    BOOK_NEW_SECTION_PROMPT,
    BOOK_CONTINUING_SECTION_PROMPT,
    BOOK_CHAPTER_SUMMARY_PROMPT,
    BOOK_CHAPTER_INTRODUCTION_PROMPT,
)

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


def get_completion(prompt):
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
    )

    n_tokens += response["usage"]["total_tokens"]

    print(f"Total tokens used: {n_tokens}")
    return response.choices[0].message.content


def generate_textbook_writing(prompt, max_tokens=512):
    response = with_retry(lambda: get_completion(prompt))
    return response


def write_to_book(course, text_excerpt):
    with open(f"textbooks-from-jsonl/{course}.md", "a") as f:
        f.write(f"{text_excerpt}\n\n")


def write_to_prompts(course, prompt, text_excerpt):
    with open(f"rlhf/{course}.jsonl", "a") as f:
        f.write(json.dumps({"prompt": prompt, "text": text_excerpt}) + "\n")


def write_to_progress(course, chapter, topic, subtopic):
    with open(f"progress/{course}.txt", "a") as f:
        f.write(",".join([chapter, topic, subtopic]) + "\n")


def write_book(course, book_data):
    current_chapter = None
    current_topic = None
    current_subtopic = None
    previous_context = None

    if not os.path.exists(f"textbooks-from-jsonl/{course}.md"):
        prompt = BOOK_FOREWARD_PROMPT.format(title=course)
        text_excerpt = generate_textbook_writing(prompt, max_tokens=512)
        write_to_book(course, text_excerpt)
        write_to_prompts(course, prompt, text_excerpt)
        write_to_progress(course, "foreward", "foreward", "foreward")

        previous_context = text_excerpt

    all_chapters = [configuration["chapter"] for configuration in book_data]
    chapters = []
    [chapters.append(x) for x in all_chapters if x not in chapters]

    for configuration in book_data:
        config = configuration

        config_chapter = config["chapter"]
        config_topic = config["topic"]
        config_subtopic = config["subtopic"]
        text_excerpt = ""

        if config_chapter != current_chapter:
            if current_chapter is not None:
                print("Generating chapter summary")
                prompt = BOOK_CHAPTER_SUMMARY_PROMPT.format(
                    title=course,
                    chapter=current_chapter,
                    book_context=previous_context,
                )
                text_excerpt = generate_textbook_writing(
                    prompt,
                    max_tokens=2048,
                )
                write_to_book(course, text_excerpt)
                write_to_prompts(course, prompt, text_excerpt)

            print("Generating chapter introduction")
            prompt = BOOK_CHAPTER_INTRODUCTION_PROMPT.format(
                title=course,
                chapter=config_chapter,
                book_context=chapters,
            )

            text_excerpt = generate_textbook_writing(
                prompt,
                max_tokens=512,
            )
            write_to_book(course, text_excerpt)
            write_to_prompts(course, prompt, text_excerpt)

        if config_topic != current_topic:
            print("Generating new section")
            prompt = BOOK_NEW_SECTION_PROMPT.format(
                title=course,
                chapter=config_chapter,
                section=config_topic,
                subsection=config_subtopic,
                book_context=previous_context,
            )

            text_excerpt = generate_textbook_writing(
                prompt,
                max_tokens=2048,
            )
            write_to_book(course, text_excerpt)
            write_to_prompts(course, prompt, text_excerpt)

        elif config_subtopic != current_subtopic:
            print("Generating continuing section")
            prompt = BOOK_CONTINUING_SECTION_PROMPT.format(
                title=course,
                chapter=config_chapter,
                section=config_topic,
                subsection=config_subtopic,
                book_context=previous_context,
            )

            text_excerpt = generate_textbook_writing(
                prompt,
                max_tokens=2048,
            )
            write_to_book(course, text_excerpt)
            write_to_prompts(course, prompt, text_excerpt)

        previous_context = text_excerpt
        current_chapter = config_chapter
        current_topic = config_topic
        current_subtopic = config_subtopic

        write_to_progress(course, config_chapter, config_topic, config_subtopic)


def write_all_books_from_directory():
    current_book = None
    for i, filename in enumerate(os.listdir("jsonl/individual-books")):
        if filename.endswith(".jsonl"):
            course = filename.split(".")[0]

            if os.path.exists(f"textbooks-from-jsonl/{course}.md"):
                continue

            print("Generating", course)
            with open(f"jsonl/individual-books/{filename}") as f:
                book_data = [json.loads(line) for line in f.readlines()]
                write_book(course, book_data)
                break


write_all_books_from_directory()
