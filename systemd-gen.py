#!/usr/bin/env python3

import argparse
import os
from typing import Optional


def create_service_file(
    working_dir: str, command: str, description: str = "My custom service"
):
    return f"""[Unit]
Description={description}
After=network.target

[Service]
Type=simple
WorkingDirectory={working_dir}
ExecStart={command}
Restart=on-failure

[Install]
WantedBy=default.target
"""


def create_timer_file(name: str, on_calendar: str):
    return f"""[Unit]
Description=Timer for {name} service

[Timer]
OnCalendar={on_calendar}
Persistent=true

[Install]
WantedBy=timers.target
"""


def save_file(content: str, filename: str):
    with open(filename, "w") as f:
        f.write(content)


class Colors:
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    RESET = "\033[0m"

    @staticmethod
    def color_text(text, color):
        return f"{color}{text}{Colors.RESET}"


class ColoredFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog)

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = Colors.color_text("Usage:", Colors.MAGENTA)
        return super().add_usage(usage, actions, groups, prefix)

    def start_section(self, heading):
        super().start_section(Colors.color_text(heading.capitalize(), Colors.CYAN))

    def add_argument(self, action):
        if action.help is not argparse.SUPPRESS:
            if action.required:
                action.help = f"{Colors.RED}[REQUIRED]{Colors.RESET} {action.help}"
            elif action.option_strings:
                action.help = f"{Colors.CYAN}[OPTION]{Colors.RESET} {action.help}"
            else:
                action.help = f"{Colors.GREEN}[POSITIONAL]{Colors.RESET} {action.help}"
        super().add_argument(action)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            return super()._format_action_invocation(action)

        parts = []
        for option_string in action.option_strings:
            parts.append(Colors.color_text(option_string, Colors.YELLOW))
        return ", ".join(parts)


class Args:
    name: str
    working_dir: str
    command: str
    timer: Optional[str]
    description: str

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Generate a user systemd service file and optionally a timer unit. \
    Example timer formats: daily at 2 PM -> "*-*-* 14:00:00", every Monday at 1 AM -> "Mon *-*-* 01:00:00".',
            formatter_class=ColoredFormatter,
        )
        parser.add_argument(
            "-n",
            "--name",
            required=True,
            help="Service name (without .service extension)",
        )
        parser.add_argument(
            "-w",
            "--working-dir",
            required=True,
            help="Working directory for the service",
        )
        parser.add_argument(
            "-c",
            "--command",
            required=True,
            help="Command to execute (ensure it is correctly quoted)",
        )
        parser.add_argument(
            "-t",
            "--timer",
            help='Timer specification in systemd calendar time formats, e.g., daily at 2 PM would be "*-*-* 14:00:00". See systemd.time(7) for more info.',
        )
        parser.add_argument(
            "-d",
            "--description",
            default="A custom systemd service",
            help="Description of the service",
        )

        args = parser.parse_args()
        self.working_dir = args.working_dir
        self.command = args.command
        self.description = args.description
        self.name = args.name
        self.timer = args.timer


def main():
    args = Args()

    service_filename = os.path.expanduser(f"~/.config/systemd/user/{args.name}.service")
    os.makedirs(os.path.dirname(service_filename), exist_ok=True)

    service_content = create_service_file(
        os.path.realpath(args.working_dir), args.command, args.description
    )
    save_file(service_content, service_filename)
    print(f"Service file saved to {service_filename}")

    if args.timer:
        if not os.path.exists(service_filename):
            print(
                f"Error: Service file {args.name}.service does not exist. Please create the service first."
            )
            return

        timer_filename = os.path.expanduser(f"~/.config/systemd/user/{args.name}.timer")
        timer_content = create_timer_file(args.name, args.timer)
        save_file(timer_content, timer_filename)
        print(f"Timer file saved to {timer_filename}")


if __name__ == "__main__":
    main()
