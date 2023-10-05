<h1 align="center"> OpenBlue </h1>


---

<p align="center">
    <img src="static/favicon.ico" style="width:48px;height:48px">
</p>

---

OpenBlue is a simple web interface developed in Flask to provide a graphical interface for interacting with the OpenAi API. It allows users to send requests to the OpenAi API and receive generated responses using GPT-3.5 and GPT-4 models.
> OpenBlue is released under the [MIT](./LICENSE) license. 
> I do not take any responsibility for its usage.

## Features

- Text **Chat** using GPT-3.5 and GPT-4 models.
- Include file content in the chat conversation.
- **Translate** text.
- Translate DOCX, PDF, and TXT files.
- Translate only the text in DOCX without affecting the formatting.
- **Transcribe** audio and provide a summary or translation of it.

OpenBlue utilizes **OpenAI APIs** for its operation.
- [Chat completions API](https://platform.openai.com/docs/guides/gpt/chat-completions-api) for chat and translate.
- [Trascription API](https://platform.openai.com/docs/guides/speech-to-text) for Audio trascription (using model [Whisper](https://openai.com/research/whisper))
## Requirements 

OpenBlue requires an OpenAI API key.
You need to store this key as an environment variable in your system with the name **"API-KEY"**.
> The creation of the API key is free through their official [website](https://platform.openai.com/account/api-keys).
> Each request incurs a variable cost (more information [here](https://openai.com/pricing)).

|        | Version        |
|-------:|----------------|
| Python | 3.11 or higher |
|  Redis | 7.2.x or higher |
| ffmpeg | 6.0            |

Without ffmpeg, there might be some issues with transcribing audio and video files, but the rest would function identically.
## Installation

First, ensure that [Redis](https://redis.io/docs/getting-started/installation/) and [ffmpeg](https://ffmpeg.org/download.html) are installed correctly .

- If you are using Arch, you can easily install Redis and Ffmpeg like this:
    ```bash
    sudo pacman -S redis
    sudo pacman -S ffmpeg
    ```
In order to run, you need Redis to be running.
```bash
redis-server
```

Then, download OpenBlue with this command and create a virtual environment:
```bash
git clone https://github.com/GiovanniMenon/OpenBlue.git
cd OpenBlue
python3.11 -m venv .venv
```
Activate Environment and install all the requirements in [requirements.txt](requirements.txt):

- Windows
    ```cmd
    .venv\Scripts\activate
    pip install -r requirements.txt
    ```
- Linux/macOS
    ```bash
    . .venv/bin/activate
    pip install -r requirements.txt
    ```

Now you can start the application correctly.
```bash
python3.11 app.py
```
To create a user, you must have started the application at least once and then execute:
```bash
python3.11 db_config.py
```





