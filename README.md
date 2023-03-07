# chatsh

Chatsh is a demo project that utilizes ChatGPT to execute commands. This tool accepts inputs and submits them to ChatGPT, which will determine the appropriate action to take, except for built-in commands.

## Usage

To use chatsh, run the following command:
```bash
python chatsh.py [--no-prompt]
```

You can add the optional `--no-prompt` flag to execute commands from ChatGPT without prompt. However, please be aware that this feature should be used at your own risk.

Chatsh comes with the following built-in commands:

- `help`:     Displays this message
- `cd:`       Changes the current directory
- `reset`:    Resets ChatGPT and forgets all command history
- `exit`:     Exits the application

## Get Started
To use chatsh, you can replace the API key and Python script path in the provided wrapper script.

## Notice
Please note that ChatGPT may not always generate the correct command. Therefore, it is important to keep an eye on the suggested commands and verify their accuracy.

## Example
[![asciicast](https://asciinema.org/a/lMbFFOU13YNZXlba2jbytzNu1.svg)](https://asciinema.org/a/lMbFFOU13YNZXlba2jbytzNu1)