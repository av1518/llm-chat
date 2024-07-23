# Conversational AI: an LLM-based end-to-end voice AI system

This is a small project of building an end-to-end conversational AI assistant. It uses a Llama3 LLM, and Deepgram for speech-to-text and text-to-speech capabilities.



## Dependencies
To install the necessary Conda environment from these dependencies, run:
```bash
conda env create -f environment.yml
```

Once the environment is created, activate it using:

```bash
conda activate llm
```

We use [Ollama](https://github.com/ollama/ollama/tree/main) to run LLMs, which serves as the "backend" for the chat interface. Ollama comes with a ready-to-go bare bones command line interface for chatting with local LLMs as well as a local API that we can request from our script to generate responses. 

We use the preview version for windows, found [here](https://ollama.com/download/windows). The first time the API is called it will download LLama3 (around 8GB). 

To transcribe the audio, we first export it into a wav file and then use deepgram’s python sdk to transcribe the local file. In order to use Deepgram’s API, create an API key from the dashboard [page](https://deepgram.com/product/text-to-speech). 

## Creating a chat
We use Streamlit to create the web-based front-end UI. It is an open source python tool for ML applications. To begin a chat session simply run the following from the root of the repository:

```bash
streamlit run src/main.py
```
This will open the web UI on the browser. To quit a chat session use `Ctrl+C` on the terminal.

## Contributing

Contributions are welcome. Please open an issue to discuss significant changes and update tests as appropriate.

## License
This project is open-sourced under the [MIT](https://choosealicense.com/licenses/mit/) License.



