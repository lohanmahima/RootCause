FROM python:3.10-slim

# Install necessary tools and Ollama
RUN apt-get update && apt-get install -y curl procps && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://ollama.com/install.sh | sh

# Hugging Face Spaces requires running as a non-root user
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    OLLAMA_HOST=0.0.0.0

WORKDIR $HOME/app

# Install Python requirements
COPY --chown=user requirements.txt $HOME/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=user . $HOME/app/

# Setup entrypoint script
RUN chmod +x $HOME/app/entrypoint.sh

# Expose port for Streamlit in HF Spaces
EXPOSE 7860

CMD ["./entrypoint.sh"]
