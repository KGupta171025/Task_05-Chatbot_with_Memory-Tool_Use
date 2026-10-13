"""
Main Entrypoint for Nexoramind Task 05 Chatbot.
"""

import argparse
import subprocess
import sys


def run_api(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    import uvicorn
    uvicorn.run("api.app:app", host=host, port=port, reload=reload)


def run_frontend(port: int = 8501):
    cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", str(port)]
    subprocess.run(cmd)


def run_evaluate():
    from evaluation.evaluate_chatbot import run_benchmark
    run_benchmark()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nexoramind Chatbot with Memory & Tool Use")
    parser.add_argument("--mode", type=str, default="api",
                        choices=["api", "frontend", "evaluate"])
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.mode == "api":
        run_api(host=args.host, port=args.port)
    elif args.mode == "frontend":
        run_frontend(port=8501)
    elif args.mode == "evaluate":
        run_evaluate()
