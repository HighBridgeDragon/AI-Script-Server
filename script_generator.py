import argparse
import json
import os
import random
import time

import pya3rt
import requests
from dotenv import load_dotenv
from tqdm import trange

load_dotenv(dotenv_path=r".env")


def a3rt_response(text):
    api_key = os.getenv(r"A3RT_API_KEY")
    client = pya3rt.TalkClient(api_key)
    response = client.talk(text)
    return ((response[r"results"])[0])[r"reply"]


def noby_response(text):
    api_key = os.getenv(r"COTOGOTO_API_KEY")
    endpoint = os.getenv(r"COTOGOT_API_ENDPOINT")

    payload = {r"text": text, r"app_key": api_key}
    r = requests.get(endpoint, params=payload)
    data = r.json()
    return data[r"text"]


def main(args: argparse.Namespace):
    query = args.query
    conversation_steps = args.conversation_steps
    post_flag = args.post_to_webhook
    current_response = query
    current_speeker = r""
    target_webhook_url = r""
    scripts = []

    actor_a_url = os.getenv(r"ACTOR_A_WEBHOOK_URL")
    actor_b_url = os.getenv(r"ACTOR_B_WEBHOOK_URL")

    actor_converter = {r'a3rt': actor_a_url, r'noby': actor_b_url}

    for cs_idx in trange(conversation_steps, desc=r"会話生成中..."):
        if cs_idx % 2 == 0:
            current_response = noby_response(current_response)
            current_speeker = r"a3rt"
        else:
            current_response = a3rt_response(current_response)
            current_speeker = r"noby"

        scripts.append(
            {
                r"actor": current_speeker,
                r"dialogue": current_response,
            }
        )

    print(r"--台本--")
    print(r"クエリ: ", query)

    if post_flag:
        requests.post(actor_b_url, data=json.dumps({r"text": query}))

    for item in scripts:
        print("{0}:{1}".format(item[r"actor"], item[r"dialogue"]))

        if post_flag:
            requests.post(
                actor_converter[item[r'actor']], data=json.dumps({r"text": item[r"dialogue"]})
            )
        time.sleep(1.5 + (random.randint(0, 10) - 5) * 0.1)


if __name__ == r"__main__":
    parser = argparse.ArgumentParser(
        prog=r"Script Generator",
        usage=r"python script-generator.py -q 文章",
        add_help=True,
    )

    parser.add_argument(r"-q", r"--query", help=r"会話の起点となる文章", type=str, required=True)
    parser.add_argument(
        r"-cs", r"--conversation_steps", help=r"会話のやり取り数", type=int, default=5
    )
    parser.add_argument(
        r"-p", r"--post_to_webhook", help=r"webhookへ投稿するフラグ", action=r"store_true"
    )

    args = parser.parse_args()

    main(args)
