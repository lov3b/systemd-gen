#!/usr/bin/env python3

import argparse
import os


def create_service_file(working_dir, command, user, description="My custom service"):
    return f"""[Unit]
Description={description}
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={working_dir}
ExecStart={command}
Restart=on-failure

[Install]
WantedBy=default.target
"""


def create_timer_file(name, on_calendar):
    return f"""[Unit]
Description=Timer for {name} service

[Timer]
OnCalendar={on_calendar}
Persistent=true

[Install]
WantedBy=timers.target
"""


def save_file(content, filename):
    with open(filename, "w") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description='Generate a systemd service file and optionally a timer unit. \
Example timer formats: daily at 2 PM -> "*-*-* 14:00:00", every Monday at 1 AM -> "Mon *-*-* 01:00:00".',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-n", "--name", required=True, help="Service name (without .service extension)"
    )
    parser.add_argument(
        "-w", "--working-dir", required=True, help="Working directory for the service"
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
    parser.add_argument(
        "-u",
        "--user",
        default=os.getlogin(),
        help="User to run the service as (defaults to the current user)",
    )

    args = parser.parse_args()

    service_filename = os.path.expanduser(f"~/.config/systemd/user/{args.name}.service")
    os.makedirs(os.path.dirname(service_filename), exist_ok=True)

    service_content = create_service_file(
        args.working_dir, args.command, args.user, args.description
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
