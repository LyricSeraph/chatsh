#!/usr/bin/env python3

import getopt
import os
import platform
import re
import requests
import subprocess
import sys

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
NO_PROMPT = False
SYSTEM_MESSAGE = """
You are a {} terminal with permission to directly execute commands on the user's computer.
Your response beginning with "Execute:" in a single line will be executed directly on the user's computer terminal.
Please keep your responses as concise as possible.
""".format(platform.system())
MESSAGES = []


def print_with_color(color, text: str):
    color_codes = {
        'red': '\033[0;31m',
        'blue': '\033[0;34m',
        'yellow': '\033[0;33m'
    }
    print(color_codes[color] + text + "\033[0m")


def print_help():
    help_message = """
Chatsh is a demo project that utilizes ChatGPT to execute commands. 
This tool accepts inputs and submits them to ChatGPT, which will determine the appropriate action to take, except for built-in commands.

Please note that ChatGPT may not always generate the correct command.
Therefore, it is important to keep an eye on the suggested commands and verify their accuracy.

You can add the optional `--no-prompt` flag to execute commands from ChatGPT without prompt.
However, please be aware that this feature should be used at your own risk.


builtin commands:
    help    Display this message
    cd      Change current directory
    reset   Reset chatGPT, which will forget all the command history
    exit    Exit this application
"""
    print(help_message)


def init(argv):
    global SYSTEM_MESSAGE
    global NO_PROMPT
    try:
        opts, args = getopt.getopt(argv, "", ["no-prompt"])
        for opt, arg in opts:
            if opt == "--no-prompt":
                NO_PROMPT = True
    except getopt.GetoptError:
        print_with_color("red", "Invalid options")
    if OPENAI_API_KEY == "" or OPENAI_API_KEY is None:
        print_with_color("red", "Please provide you OPENAI_API_KEY in system environment")
        sys.exit(1)
    MESSAGES.append({
        "role": "system",
        "content": SYSTEM_MESSAGE
    })


def extract_commands(response_message_content: str):
    command_pattern = re.compile('^Execute:.*$')
    commands = re.findall(command_pattern, response_message_content)
    return [command[8:] for command in commands]


def execute_commands(commands: list[str]):
    for command in commands:
        command = command.strip()
        allow_execute = NO_PROMPT
        if not NO_PROMPT:
            prompt = input("Allow to execute: \033[0;34m{}\033[0m ?[y/n]".format(command))
            allow_execute = (prompt == 'y')
        if allow_execute:
            p = subprocess.Popen(["bash", "-c", command], stdin=sys.stdin, stdout=sys.stdout,
                                 stderr=sys.stderr)
            p.wait()


def handle_builtin_commands(message):
    if message == "help":
        print_help()
    elif message.startswith("cd "):
        try:
            os.chdir(message[3:].replace("~", os.path.expanduser("~")))
        except FileNotFoundError:
            print_with_color("red", "Error: File not found")
    elif message == "reset":
        global MESSAGES
        MESSAGES = [{
            "role": "system",
            "content": SYSTEM_MESSAGE
        }]
    elif message == "exit":
        sys.exit(0)
    else:
        return False
    return True


def handle_message(message: str):
    global MESSAGES
    global OPENAI_API_KEY
    if handle_builtin_commands(message):
        return
    # As chatGPT do not get our cd command, we should let it known the current working directory
    message = "PWD is now '{}'. ".format(os.getcwd()) + message
    MESSAGES.append({
        "role": "user",
        "content": message,
    })
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {'Authorization': 'Bearer ' + OPENAI_API_KEY}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": MESSAGES
    }
    # print("request", str(data))
    response = requests.post(url, json=data, headers=headers, timeout=600)
    # print("response", str(response.text))
    content = response.json()
    if "error" in content:
        MESSAGES.pop()
        print_with_color("red", content["error"]["message"])
        return False
    else:
        response_message = content["choices"][0]
        MESSAGES.append(response_message["message"])
        response_message_content = response_message["message"]["content"]
        print_with_color("yellow", response_message_content)
        commands = extract_commands(response_message_content)
        execute_commands(commands)
        return True


def get_promote():
    return os.getcwd().replace(os.path.expanduser("~"), "~") + "$ "


def main():
    message = ""
    resume = False
    try:
        while True:
            line = input(">> " if resume else (get_promote())).strip()
            message += line
            if line.endswith("\\"):
                message = message[:-1] + "\n"
                resume = True
                continue
            elif message == "":
                continue
            else:
                handle_message(message)
                message = ""
                resume = False
    except EOFError:
        pass


if __name__ == "__main__":
    init(sys.argv[1:])
    print_help()
    main()

