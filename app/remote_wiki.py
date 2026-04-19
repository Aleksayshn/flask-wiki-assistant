"""
Remote Wikipedia service.

This module contains the SSH integration used by the Flask application to
execute `wiki.py` on a remote Ubuntu EC2 instance through Paramiko.
"""

from __future__ import annotations

import os
import re
import shlex
from typing import Dict

import paramiko


class RemoteWikiService:
    """
    Execute the remote Wikipedia helper script over SSH.

    The service returns a predictable dictionary so the Flask route can
    render either a successful result or a user-friendly error message.
    """

    def __init__(
        self,
        enabled: bool,
        host: str,
        port: int,
        username: str,
        key_path: str,
        script_path: str,
    ) -> None:
        self.enabled = enabled
        self.host = host
        self.port = port
        self.username = username
        self.key_path = key_path
        self.script_path = script_path

    def search(self, search_term: str) -> Dict[str, str | bool]:
        """
        Run the remote wiki script and parse its plain-text response.

        Expected output from the remote script:
        TITLE: ...
        URL: ...
        SUMMARY: ...
        """
        if not self.enabled:
            return self._build_response(
                success=False,
                raw_output="",
                error="Remote execution is disabled. Set REMOTE_EXECUTION_ENABLED=true to enable SSH lookup.",
            )

        if not search_term:
            return self._build_response(
                success=False,
                raw_output="",
                error="No search term was provided to the remote search service.",
            )

        if not self.host or not self.username or not self.key_path or not self.script_path:
            return self._build_response(
                success=False,
                raw_output="",
                error="Remote EC2 configuration is incomplete. Check the environment variables before running the app.",
            )

        expanded_key_path = os.path.expanduser(self.key_path)

        if not os.path.exists(expanded_key_path):
            return self._build_response(
                success=False,
                raw_output="",
                error=f"The SSH private key file was not found at {expanded_key_path}.",
            )

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        command = f"python3 {shlex.quote(self.script_path)} {shlex.quote(search_term)}"

        try:
            # Private key authentication is used here instead of a password so
            # credentials are not hardcoded in the source code.
            client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                key_filename=expanded_key_path,
                timeout=15,
                look_for_keys=False,
                allow_agent=False,
            )

            stdin, stdout, stderr = client.exec_command(command)
            stdin.close()

            stdout_text = stdout.read().decode("utf-8", errors="replace").strip()
            stderr_text = stderr.read().decode("utf-8", errors="replace").strip()
            exit_status = stdout.channel.recv_exit_status()

            raw_output = stdout_text if stdout_text else stderr_text

            if exit_status != 0:
                return self._build_response(
                    success=False,
                    raw_output=raw_output,
                    error=(
                        "The remote wiki script returned an error. "
                        f"SSH command exit status: {exit_status}."
                    ),
                )

            parsed_result = self._parse_output(stdout_text)
            parsed_result["raw_output"] = raw_output

            if not parsed_result["success"] and stderr_text:
                parsed_result["error"] = (
                    f"{parsed_result['error']} Remote stderr: {stderr_text}"
                )

            return parsed_result
        except paramiko.AuthenticationException:
            return self._build_response(
                success=False,
                raw_output="",
                error="SSH authentication failed. Verify the EC2 username and private key path.",
            )
        except paramiko.SSHException as error:
            return self._build_response(
                success=False,
                raw_output="",
                error=f"An SSH error occurred while contacting the EC2 instance: {error}",
            )
        except OSError as error:
            return self._build_response(
                success=False,
                raw_output="",
                error=f"A network or file system error occurred during remote execution: {error}",
            )
        finally:
            client.close()

    def _parse_output(self, output_text: str) -> Dict[str, str | bool]:
        """
        Convert the remote script output into a dictionary for Flask.

        The remote script prints labelled lines in this format:
        TITLE: ...
        URL: ...
        SUMMARY: ...

        The parser is defensive because real remote command output can also
        contain blank lines or warnings. Summary text may span multiple lines,
        so once SUMMARY starts, additional related lines are appended until a
        new recognised label appears.
        """
        parsed_data = {"TITLE": "", "URL": "", "SUMMARY": ""}
        current_field = ""

        # Only these labels are part of the supported structured format.
        known_labels = {"TITLE", "URL", "SUMMARY"}

        for raw_line in output_text.splitlines():
            line = raw_line.strip()

            # Empty lines do not contribute useful structured data.
            if not line:
                continue

            labelled_match = re.match(r"^(TITLE|URL|SUMMARY):\s*(.*)$", line, re.IGNORECASE)
            if labelled_match:
                current_field = labelled_match.group(1).upper()
                parsed_data[current_field] = labelled_match.group(2).strip()
                continue

            # Ignore unrelated warnings or noise before the structured output.
            if self._is_unrelated_output(line, known_labels):
                continue

            # Support multi-line SUMMARY output by appending additional lines
            # after the initial SUMMARY label.
            if current_field == "SUMMARY":
                if parsed_data["SUMMARY"]:
                    parsed_data["SUMMARY"] = f"{parsed_data['SUMMARY']} {line}"
                else:
                    parsed_data["SUMMARY"] = line

        title = parsed_data["TITLE"]
        url = parsed_data["URL"]
        summary = parsed_data["SUMMARY"]

        if not title and not summary:
            return self._build_response(
                success=False,
                raw_output=output_text,
                error="The remote script did not return the expected structured output.",
            )

        return self._build_response(
            success=True,
            title=title,
            url=url,
            summary=summary,
            raw_output=output_text,
            error="",
        )

    def _is_unrelated_output(self, line: str, known_labels: set[str]) -> bool:
        """
        Detect warnings or unrelated output that should not break parsing.

        This keeps the parser tolerant of SSH banners, Python warnings, or
        third-party library messages that may appear around the real data.
        """
        upper_line = line.upper()

        if upper_line.startswith(("WARNING:", "WARN:", "NOTICE:", "INFO:", "DEBUG:")):
            return True

        # If a line contains a colon but does not start with one of the known
        # labels, treat it as unrelated output rather than structured data.
        if ":" in line:
            possible_label = line.split(":", 1)[0].strip().upper()
            if possible_label not in known_labels:
                return True

        return False

    def _build_response(
        self,
        success: bool,
        title: str = "",
        url: str = "",
        summary: str = "",
        raw_output: str = "",
        error: str = "",
    ) -> Dict[str, str | bool]:
        """Create a consistent dictionary structure for all outcomes."""
        return {
            "success": success,
            "title": title,
            "url": url,
            "summary": summary,
            "raw_output": raw_output,
            "error": error,
        }
