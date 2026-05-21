from argparse import ArgumentParser
from dataclasses import dataclass


@dataclass
class AgentArgs:
    """Input arguments to be passed to the script to run the Bank Support Agent."""

    cli: bool
    web: bool
    host: str
    port: int


def parse_args() -> AgentArgs:
    """Parse and return input script arguments."""
    parser = ArgumentParser()
    parser.add_argument(
        "-C",
        "--cli",
        default=True,
        action="store_true",
        help="Whether to run the agent in the CLI mode (default: True).",
    )
    parser.add_argument(
        "-W",
        "--web",
        default=False,
        action="store_true",
        help="Whether to run the agent in the WEB mode (default: False).",
    )
    parser.add_argument(
        "-H",
        "--host",
        default="127.0.0.1",
        help="Host address to run the agent on if WEB mode is enabled (default: 127.0.0.1).",
    )
    parser.add_argument(
        "-P",
        "--port",
        default=8000,
        type=int,
        help="Port number to run the agent on if WEB mode is enabled (default: 8000).",
    )
    args = parser.parse_args()
    return AgentArgs(**args.__dict__)
