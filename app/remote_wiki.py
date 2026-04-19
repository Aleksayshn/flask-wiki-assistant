"""
Remote Wikipedia service abstraction.

This module is responsible for the future distributed part of the project,
where a remote machine can execute a script through Paramiko.
"""

from __future__ import annotations

from typing import Optional


class RemoteWikiService:
    """
    Placeholder service for remote execution.

    In future work, this class can establish an SSH connection with Paramiko
    and invoke a remote Python script that performs the wiki search.
    """

    def __init__(
        self,
        enabled: bool,
        host: str,
        port: int,
        username: str,
        password: str,
        script_path: str,
    ) -> None:
        self.enabled = enabled
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.script_path = script_path

    def search(self, search_term: str) -> Optional[str]:
        """
        Search for a term using a remote script.

        The starter project returns `None` because remote execution has not
        yet been implemented.
        """
        if not self.enabled or not search_term:
            return None

        # Future implementation with Paramiko:
        # 1. Create an SSH client.
        # 2. Connect to the remote host.
        # 3. Execute the remote wiki script with the search term.
        # 4. Read stdout/stderr and return the result.
        return None
