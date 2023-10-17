from prompts import (
    BOOK_FOREWARD_PROMPT,
    BOOK_NEW_SECTION_PROMPT,
    BOOK_CONTINUING_SECTION_PROMPT,
    BOOK_CHAPTER_SUMMARY_PROMPT,
    BOOK_CHAPTER_INTRODUCTION_PROMPT,
)

import os
import requests


import logging
import time
import json
from tqdm import tqdm

n_tokens = 0
logging.basicConfig(level=logging.INFO)


def with_retry(func, max_retries=3):
    """Attempt to execute the provided function up to max_retries times."""
    for _ in range(max_retries):
        try:
            return func()
        except Exception as e:
            logging.warning(f"Exception encountered: {e}. Retrying...")
            time.sleep(5)
    raise ValueError(f"Failed to execute {func.__name__} after {max_retries} retries.")


def get_completion(prompt, model="gpt-3.5-turbo", temperature=0.1, timeout=60):
    global n_tokens

    messages = [
        {
            "role": "system",
            "content": "You are a prolific, expert mathematics education textbook writer, writing a new book.",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json={"model": model, "messages": messages, "temperature": temperature},
            headers={"Authorization": f'Bearer {os.environ["OPENAI_API_KEY2"]}'},
            timeout=timeout,  # Set the timeout in seconds
        )

        response.raise_for_status()  # Check for HTTP request errors
        n_tokens += response.json()["usage"]["total_tokens"]

        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout as e:
        # Handle a timeout error here (e.g., logging, raising an exception, etc.)
        logging.warning(f"Request timed out {e}")
        return ""


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


def write_book(
    course,
    book_data,
    progress_chapter,
    progress_topic,
    progress_subtopic,
):
    global n_tokens
    current_chapter = progress_chapter
    current_topic = progress_topic
    current_subtopic = progress_subtopic
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

    for configuration in tqdm(book_data, desc=f"{course}|{n_tokens} Tokens"):
        config = configuration

        config_chapter = config["chapter"]
        config_topic = config["topic"]
        config_subtopic = config["subtopic"]
        text_excerpt = ""

        if config_chapter != current_chapter:
            if current_chapter is not None:
                logging.debug(f"Generating chapter summary {current_chapter}")
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

            logging.debug(f"Generating chapter introduction {config_chapter}")
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
            write_to_progress(course, config_chapter, config_topic, config_subtopic)

        if config_topic != current_topic:
            logging.debug(f"Generating section {config_topic}")
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
            logging.debug(f"Generating subsection {current_subtopic}")
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
    for dir_ in ["textbooks-from-jsonl", "rlhf", "progress"]:
        if not os.path.exists(dir_):
            os.makedirs(dir_, exist_ok=True)

    for i, filename in enumerate(os.listdir("jsonl/individual-books")):
        if filename.endswith(".jsonl"):
            course = filename.split(".")[0]

            progress_index = 0
            progress_chapter = None
            progress_topic = None
            progress_subtopic = None
            if os.path.exists(f"textbooks-from-jsonl/{course}.md"):
                if os.path.exists(f"progress/{course}.txt"):
                    with open(f"jsonl/individual-books/{filename}") as f:
                        book_data = [json.loads(line) for line in f.readlines()]

                    with open(f"progress/{course}.txt") as f:
                        last_chapter, last_topic, last_subtopic = [
                            line.strip() for line in f.readlines()
                        ][-1].split(",")

                        logging.warning(
                            f"Resuming from {last_chapter}|{last_topic}|{last_subtopic}"
                        )

                    for configuration_index, configuration in enumerate(book_data):
                        if (
                            configuration["chapter"] == last_chapter
                            and configuration["topic"] == last_topic
                            and configuration["subtopic"] == last_subtopic
                        ):
                            progress_index = configuration_index
                            break

                    if progress_index == len(book_data) - 1:
                        logging.warning(f"Skipping {course} because it already exists")
                        continue

            logging.info(f"Starting {course}")

            with open(f"jsonl/individual-books/{filename}") as f:
                book_data = [json.loads(line) for line in f.readlines()]
                progress_chapter = book_data[progress_index]["chapter"]
                progress_topic = book_data[progress_index]["topic"]
                progress_subtopic = book_data[progress_index]["subtopic"]

                write_book(
                    course,
                    book_data[progress_index:],
                    progress_chapter,
                    progress_topic,
                    progress_subtopic,
                )

                if i > 5:
                    break


write_all_books_from_directory()
