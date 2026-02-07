"""ForwardEmail API Client.

This module provides an async HTTP client for the ForwardEmail API,
enabling domain management, alias creation, outbound email, and more.

Typical usage example:

    from forwardemail_mcp.client import ForwardEmailClient

    async with ForwardEmailClient(api_key) as client:
        domains, pagination = await client.list_domains()
        for domain in domains:
            print(domain["name"])

Attributes:
    BASE_URL: The ForwardEmail API base URL (https://api.forwardemail.net).
"""

import httpx
from typing import Any, Optional
from pydantic import BaseModel


class PaginationInfo(BaseModel):
    """Pagination information from API response headers.

    Attributes:
        page_count: Total number of pages available.
        page_current: Current page number (1-indexed).
        page_size: Number of items per page.
        item_count: Total number of items across all pages.
    """

    page_count: int = 0
    page_current: int = 1
    page_size: int = 10
    item_count: int = 0


class ForwardEmailClient:
    """Async HTTP client for ForwardEmail API.

    Uses HTTP Basic Authentication with API token as username and empty password.
    All methods are async and should be used with await.

    Attributes:
        BASE_URL: The ForwardEmail API base URL.
        api_key: The API token used for authentication.

    Example:
        >>> async with ForwardEmailClient("your_api_key") as client:
        ...     account = await client.get_account()
        ...     print(account["email"])
    """

    BASE_URL = "https://api.forwardemail.net"

    def __init__(self, api_key: str):
        """Initialize the client with an API key.

        Args:
            api_key: ForwardEmail API token from
                https://forwardemail.net/my-account/security
        """
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client.

        Returns:
            The httpx.AsyncClient instance configured for ForwardEmail API.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                auth=(self.api_key, ""),  # Basic auth with empty password
                timeout=30.0,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client.

        Should be called when done using the client to release resources.
        Automatically called when using the client as an async context manager.
        """
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "ForwardEmailClient":
        """Enter async context manager.

        Returns:
            The client instance.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager and close the client."""
        await self.close()

    def _extract_pagination(self, response: httpx.Response) -> PaginationInfo:
        """Extract pagination info from response headers.

        Args:
            response: The HTTP response containing pagination headers.

        Returns:
            PaginationInfo with page counts and item totals.
        """
        return PaginationInfo(
            page_count=int(response.headers.get("X-Page-Count", 0)),
            page_current=int(response.headers.get("X-Page-Current", 1)),
            page_size=int(response.headers.get("X-Page-Size", 10)),
            item_count=int(response.headers.get("X-Item-Count", 0)),
        )

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        json_body: Optional[dict] = None,
    ) -> tuple[Any, Optional[PaginationInfo]]:
        """Make an API request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            path: API path (e.g., "/v1/domains").
            params: Query parameters to include in the URL.
            data: Form data for POST/PUT requests.
            json_body: JSON body for POST/PUT requests.

        Returns:
            Tuple of (response_data, pagination_info). pagination_info is None
            if the response doesn't include pagination headers.

        Raises:
            httpx.HTTPStatusError: If the request fails with a non-2xx status.
        """
        # Filter out None values from params and data
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        if data:
            data = {k: v for k, v in data.items() if v is not None}

        response = await self.client.request(
            method=method,
            url=path,
            params=params,
            data=data,
            json=json_body,
        )

        # Raise for non-2xx status codes
        response.raise_for_status()

        # Extract pagination if present
        pagination = None
        if "X-Page-Count" in response.headers:
            pagination = self._extract_pagination(response)

        # Parse JSON response
        try:
            result = response.json()
        except Exception:
            result = {"message": response.text}

        return result, pagination

    # ==================== Account Endpoints ====================

    async def get_account(self) -> dict:
        """Retrieve account information.

        Returns:
            Dict containing account details including email, plan, and settings.

        Raises:
            httpx.HTTPStatusError: If authentication fails or request errors.
        """
        result, _ = await self._request("GET", "/v1/account")
        return result

    async def create_account(self, email: str, password: Optional[str] = None) -> dict:
        """Create a new account.

        Args:
            email: Email address for the new account.
            password: Optional password. If not provided, one will be generated.

        Returns:
            Dict containing the created account details.

        Raises:
            httpx.HTTPStatusError: If account creation fails.
        """
        data = {"email": email}
        if password:
            data["password"] = password
        result, _ = await self._request("POST", "/v1/account", data=data)
        return result

    async def update_account(
        self,
        email: Optional[str] = None,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> dict:
        """Update account information.

        Args:
            email: New email address for the account.
            given_name: First name to set.
            family_name: Last name to set.
            avatar_url: URL to avatar image.

        Returns:
            Dict containing the updated account details.

        Raises:
            httpx.HTTPStatusError: If update fails.
        """
        data = {
            "email": email,
            "given_name": given_name,
            "family_name": family_name,
            "avatar_url": avatar_url,
        }
        result, _ = await self._request("PUT", "/v1/account", data=data)
        return result

    # ==================== Domain Endpoints ====================

    async def list_domains(
        self,
        query: Optional[str] = None,
        sort: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> tuple[list[dict], Optional[PaginationInfo]]:
        """List all domains.

        Args:
            query: Search query to filter domains by name.
            sort: Sort field, prefix with - for descending (e.g., "-created_at").
            page: Page number (1-indexed).
            limit: Results per page (10-50).

        Returns:
            Tuple of (list of domain dicts, pagination info).

        Raises:
            httpx.HTTPStatusError: If request fails.
        """
        params = {
            "q": query,
            "sort": sort,
            "page": page,
            "limit": limit,
            "paginate": "true",
        }
        return await self._request("GET", "/v1/domains", params=params)

    async def create_domain(
        self,
        domain: str,
        plan: str = "free",
        catchall: Optional[bool] = None,
        has_adult_content_protection: Optional[bool] = None,
        has_phishing_protection: Optional[bool] = None,
        has_executable_protection: Optional[bool] = None,
        has_virus_protection: Optional[bool] = None,
        has_recipient_verification: Optional[bool] = None,
        retention_days: Optional[int] = None,
        bounce_webhook: Optional[str] = None,
        max_quota_per_alias: Optional[str] = None,
    ) -> dict:
        """Create a new domain.

        Args:
            domain: Domain name to add (e.g., "example.com").
            plan: Plan type: "free", "enhanced_protection", or "team".
            catchall: Enable catch-all for unmatched addresses.
            has_adult_content_protection: Enable adult content filtering.
            has_phishing_protection: Enable phishing protection.
            has_executable_protection: Enable executable attachment blocking.
            has_virus_protection: Enable virus scanning.
            has_recipient_verification: Enable recipient verification.
            retention_days: Log retention days (0-30).
            bounce_webhook: Webhook URL for bounce notifications.
            max_quota_per_alias: Maximum storage quota per alias.

        Returns:
            Dict containing the created domain details.

        Raises:
            httpx.HTTPStatusError: If domain creation fails.
        """
        data = {
            "domain": domain,
            "plan": plan,
            "catchall": str(catchall).lower() if catchall is not None else None,
            "has_adult_content_protection": (
                str(has_adult_content_protection).lower()
                if has_adult_content_protection is not None
                else None
            ),
            "has_phishing_protection": (
                str(has_phishing_protection).lower()
                if has_phishing_protection is not None
                else None
            ),
            "has_executable_protection": (
                str(has_executable_protection).lower()
                if has_executable_protection is not None
                else None
            ),
            "has_virus_protection": (
                str(has_virus_protection).lower()
                if has_virus_protection is not None
                else None
            ),
            "has_recipient_verification": (
                str(has_recipient_verification).lower()
                if has_recipient_verification is not None
                else None
            ),
            "retention_days": str(retention_days) if retention_days is not None else None,
            "bounce_webhook": bounce_webhook,
            "max_quota_per_alias": max_quota_per_alias,
        }
        result, _ = await self._request("POST", "/v1/domains", data=data)
        return result

    async def get_domain(self, domain: str) -> dict:
        """Retrieve domain details.

        Args:
            domain: Domain name or ID to retrieve.

        Returns:
            Dict containing domain details including settings and verification status.

        Raises:
            httpx.HTTPStatusError: If domain not found or request fails.
        """
        result, _ = await self._request("GET", f"/v1/domains/{domain}")
        return result

    async def update_domain(
        self,
        domain: str,
        smtp_port: Optional[str] = None,
        has_adult_content_protection: Optional[bool] = None,
        has_phishing_protection: Optional[bool] = None,
        has_executable_protection: Optional[bool] = None,
        has_virus_protection: Optional[bool] = None,
        has_recipient_verification: Optional[bool] = None,
        retention_days: Optional[int] = None,
        bounce_webhook: Optional[str] = None,
        max_quota_per_alias: Optional[str] = None,
    ) -> dict:
        """Update domain settings.

        Args:
            domain: Domain name or ID to update.
            smtp_port: SMTP port (default: "25").
            has_adult_content_protection: Enable adult content filtering.
            has_phishing_protection: Enable phishing protection.
            has_executable_protection: Enable executable attachment blocking.
            has_virus_protection: Enable virus scanning.
            has_recipient_verification: Enable recipient verification.
            retention_days: Log retention days (0-30).
            bounce_webhook: Webhook URL for bounce notifications.
            max_quota_per_alias: Maximum storage quota per alias.

        Returns:
            Dict containing the updated domain details.

        Raises:
            httpx.HTTPStatusError: If update fails.
        """
        data = {
            "smtp_port": smtp_port,
            "has_adult_content_protection": (
                str(has_adult_content_protection).lower()
                if has_adult_content_protection is not None
                else None
            ),
            "has_phishing_protection": (
                str(has_phishing_protection).lower()
                if has_phishing_protection is not None
                else None
            ),
            "has_executable_protection": (
                str(has_executable_protection).lower()
                if has_executable_protection is not None
                else None
            ),
            "has_virus_protection": (
                str(has_virus_protection).lower()
                if has_virus_protection is not None
                else None
            ),
            "has_recipient_verification": (
                str(has_recipient_verification).lower()
                if has_recipient_verification is not None
                else None
            ),
            "retention_days": str(retention_days) if retention_days is not None else None,
            "bounce_webhook": bounce_webhook,
            "max_quota_per_alias": max_quota_per_alias,
        }
        result, _ = await self._request("PUT", f"/v1/domains/{domain}", data=data)
        return result

    async def delete_domain(self, domain: str) -> dict:
        """Delete a domain.

        Args:
            domain: Domain name or ID to delete.

        Returns:
            Dict containing deletion confirmation.

        Raises:
            httpx.HTTPStatusError: If deletion fails.
        """
        result, _ = await self._request("DELETE", f"/v1/domains/{domain}")
        return result

    async def verify_domain_records(self, domain: str) -> dict:
        """Verify domain DNS records (MX, TXT).

        Args:
            domain: Domain name to verify.

        Returns:
            Dict containing verification results for each record type.

        Raises:
            httpx.HTTPStatusError: If verification request fails.
        """
        result, _ = await self._request("GET", f"/v1/domains/{domain}/verify-records")
        return result

    async def verify_domain_smtp(self, domain: str) -> dict:
        """Verify domain SMTP records (DKIM, Return-Path, DMARC).

        Args:
            domain: Domain name to verify.

        Returns:
            Dict containing SMTP verification results.

        Raises:
            httpx.HTTPStatusError: If verification request fails.
        """
        result, _ = await self._request("GET", f"/v1/domains/{domain}/verify-smtp")
        return result

    async def list_catchall_passwords(self, domain: str) -> list[dict]:
        """List domain-wide catch-all passwords.

        Args:
            domain: Domain name.

        Returns:
            List of password token dicts with ID and description.

        Raises:
            httpx.HTTPStatusError: If request fails.
        """
        result, _ = await self._request(
            "GET", f"/v1/domains/{domain}/catch-all-passwords"
        )
        return result if isinstance(result, list) else []

    async def create_catchall_password(
        self,
        domain: str,
        new_password: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict:
        """Create a domain-wide catch-all password.

        Args:
            domain: Domain name.
            new_password: Specific password to use. Auto-generated if not provided.
            description: Description for this password.

        Returns:
            Dict containing the created password details.

        Raises:
            httpx.HTTPStatusError: If creation fails.
        """
        data = {"new_password": new_password, "description": description}
        result, _ = await self._request(
            "POST", f"/v1/domains/{domain}/catch-all-passwords", data=data
        )
        return result

    async def delete_catchall_password(self, domain: str, token_id: str) -> dict:
        """Delete a domain-wide catch-all password.

        Args:
            domain: Domain name.
            token_id: Password token ID to delete.

        Returns:
            Dict containing deletion confirmation.

        Raises:
            httpx.HTTPStatusError: If deletion fails.
        """
        result, _ = await self._request(
            "DELETE", f"/v1/domains/{domain}/catch-all-passwords/{token_id}"
        )
        return result

    # ==================== Alias Endpoints ====================

    async def list_aliases(
        self,
        domain: str,
        query: Optional[str] = None,
        sort: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> tuple[list[dict], Optional[PaginationInfo]]:
        """List domain aliases.

        Args:
            domain: Domain name.
            query: Search query to filter aliases by name or recipient.
            sort: Sort field, prefix with - for descending.
            page: Page number (1-indexed).
            limit: Results per page (10-50).

        Returns:
            Tuple of (list of alias dicts, pagination info).

        Raises:
            httpx.HTTPStatusError: If request fails.
        """
        params = {
            "q": query,
            "sort": sort,
            "page": page,
            "limit": limit,
            "paginate": "true",
        }
        return await self._request("GET", f"/v1/domains/{domain}/aliases", params=params)

    async def create_alias(
        self,
        domain: str,
        name: str,
        recipients: Optional[list[str]] = None,
        description: Optional[str] = None,
        labels: Optional[list[str]] = None,
        has_recipient_verification: Optional[bool] = None,
        is_enabled: Optional[bool] = None,
        has_imap: Optional[bool] = None,
        has_pgp: Optional[bool] = None,
        public_key: Optional[str] = None,
        max_quota: Optional[str] = None,
    ) -> dict:
        """Create a new alias.

        Args:
            domain: Domain name.
            name: Alias name (the part before @domain).
            recipients: List of recipient email addresses to forward to.
            description: Description of this alias.
            labels: Labels for organizing aliases.
            has_recipient_verification: Enable recipient verification.
            is_enabled: Whether the alias is enabled.
            has_imap: Enable IMAP storage for this alias.
            has_pgp: Enable PGP encryption.
            public_key: PGP public key for encryption.
            max_quota: Maximum storage quota.

        Returns:
            Dict containing the created alias details.

        Raises:
            httpx.HTTPStatusError: If creation fails.
        """
        data = {
            "name": name,
            "recipients": ",".join(recipients) if recipients else None,
            "description": description,
            "labels": ",".join(labels) if labels else None,
            "has_recipient_verification": (
                str(has_recipient_verification).lower()
                if has_recipient_verification is not None
                else None
            ),
            "is_enabled": str(is_enabled).lower() if is_enabled is not None else None,
            "has_imap": str(has_imap).lower() if has_imap is not None else None,
            "has_pgp": str(has_pgp).lower() if has_pgp is not None else None,
            "public_key": public_key,
            "max_quota": max_quota,
        }
        result, _ = await self._request(
            "POST", f"/v1/domains/{domain}/aliases", data=data
        )
        return result

    async def get_alias(self, domain: str, alias_id: str) -> dict:
        """Retrieve alias details.

        Args:
            domain: Domain name.
            alias_id: Alias ID or name.

        Returns:
            Dict containing alias details including recipients and settings.

        Raises:
            httpx.HTTPStatusError: If alias not found or request fails.
        """
        result, _ = await self._request(
            "GET", f"/v1/domains/{domain}/aliases/{alias_id}"
        )
        return result

    async def update_alias(
        self,
        domain: str,
        alias_id: str,
        name: Optional[str] = None,
        recipients: Optional[list[str]] = None,
        description: Optional[str] = None,
        labels: Optional[list[str]] = None,
        has_recipient_verification: Optional[bool] = None,
        is_enabled: Optional[bool] = None,
        has_imap: Optional[bool] = None,
        has_pgp: Optional[bool] = None,
        public_key: Optional[str] = None,
        max_quota: Optional[str] = None,
    ) -> dict:
        """Update an alias.

        Args:
            domain: Domain name.
            alias_id: Alias ID or name.
            name: New alias name.
            recipients: New list of recipient email addresses.
            description: New description.
            labels: New labels.
            has_recipient_verification: Enable recipient verification.
            is_enabled: Whether the alias is enabled.
            has_imap: Enable IMAP storage.
            has_pgp: Enable PGP encryption.
            public_key: PGP public key.
            max_quota: Maximum storage quota.

        Returns:
            Dict containing the updated alias details.

        Raises:
            httpx.HTTPStatusError: If update fails.
        """
        data = {
            "name": name,
            "recipients": ",".join(recipients) if recipients else None,
            "description": description,
            "labels": ",".join(labels) if labels else None,
            "has_recipient_verification": (
                str(has_recipient_verification).lower()
                if has_recipient_verification is not None
                else None
            ),
            "is_enabled": str(is_enabled).lower() if is_enabled is not None else None,
            "has_imap": str(has_imap).lower() if has_imap is not None else None,
            "has_pgp": str(has_pgp).lower() if has_pgp is not None else None,
            "public_key": public_key,
            "max_quota": max_quota,
        }
        result, _ = await self._request(
            "PUT", f"/v1/domains/{domain}/aliases/{alias_id}", data=data
        )
        return result

    async def delete_alias(self, domain: str, alias_id: str) -> dict:
        """Delete an alias.

        Args:
            domain: Domain name.
            alias_id: Alias ID or name to delete.

        Returns:
            Dict containing deletion confirmation.

        Raises:
            httpx.HTTPStatusError: If deletion fails.
        """
        result, _ = await self._request(
            "DELETE", f"/v1/domains/{domain}/aliases/{alias_id}"
        )
        return result

    async def generate_alias_password(
        self,
        domain: str,
        alias_id: str,
        new_password: Optional[str] = None,
        is_override: Optional[bool] = None,
        emailed_instructions: Optional[bool] = None,
    ) -> dict:
        """Generate an alias password for IMAP/SMTP access.

        Args:
            domain: Domain name.
            alias_id: Alias ID or name.
            new_password: Specific password to use. Auto-generated if not provided.
            is_override: Override existing password if one exists.
            emailed_instructions: Email setup instructions to the alias.

        Returns:
            Dict containing the generated password and IMAP/SMTP settings.

        Raises:
            httpx.HTTPStatusError: If generation fails.
        """
        data = {
            "new_password": new_password,
            "is_override": str(is_override).lower() if is_override is not None else None,
            "emailed_instructions": (
                str(emailed_instructions).lower()
                if emailed_instructions is not None
                else None
            ),
        }
        result, _ = await self._request(
            "POST", f"/v1/domains/{domain}/aliases/{alias_id}/generate-password", data=data
        )
        return result

    # ==================== Outbound Email Endpoints ====================

    async def get_email_limit(self) -> dict:
        """Get daily outbound SMTP email limit and count.

        Returns:
            Dict containing "limit" (daily max) and "count" (sent today).

        Raises:
            httpx.HTTPStatusError: If request fails.
        """
        result, _ = await self._request("GET", "/v1/emails/limit")
        return result

    async def list_emails(
        self,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        sort: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> tuple[list[dict], Optional[PaginationInfo]]:
        """List outbound SMTP emails.

        Note: Does not include message body. Use get_email for full details.

        Args:
            query: Search query.
            domain: Filter by domain.
            sort: Sort field, prefix with - for descending.
            page: Page number (1-indexed).
            limit: Results per page (10-50).

        Returns:
            Tuple of (list of email dicts, pagination info).

        Raises:
            httpx.HTTPStatusError: If request fails.
        """
        params = {
            "q": query,
            "domain": domain,
            "sort": sort,
            "page": page,
            "limit": limit,
        }
        return await self._request("GET", "/v1/emails", params=params)

    async def create_email(
        self,
        from_addr: str,
        to: str,
        subject: Optional[str] = None,
        text: Optional[str] = None,
        html: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        reply_to: Optional[str] = None,
        raw: Optional[str] = None,
    ) -> dict:
        """Create and send an outbound email.

        Args:
            from_addr: Sender email address (must be an alias you control).
            to: Recipient email address(es), comma-separated for multiple.
            subject: Email subject line.
            text: Plain text body of the email.
            html: HTML body of the email.
            cc: CC recipients, comma-separated.
            bcc: BCC recipients, comma-separated.
            reply_to: Reply-To address.
            raw: Raw email content including headers (alternative to other fields).

        Returns:
            Dict containing the created email details including ID and status.

        Raises:
            httpx.HTTPStatusError: If sending fails.
        """
        data = {
            "from": from_addr,
            "to": to,
            "subject": subject,
            "text": text,
            "html": html,
            "cc": cc,
            "bcc": bcc,
            "replyTo": reply_to,
            "raw": raw,
        }
        result, _ = await self._request("POST", "/v1/emails", data=data)
        return result

    async def get_email(self, email_id: str) -> dict:
        """Retrieve outbound email details.

        Args:
            email_id: Email ID to retrieve.

        Returns:
            Dict containing full email details including body and headers.

        Raises:
            httpx.HTTPStatusError: If email not found or request fails.
        """
        result, _ = await self._request("GET", f"/v1/emails/{email_id}")
        return result

    async def delete_email(self, email_id: str) -> dict:
        """Delete/cancel an outbound email.

        Only works for emails with status "pending", "queued", or "deferred".

        Args:
            email_id: Email ID to delete.

        Returns:
            Dict containing deletion confirmation.

        Raises:
            httpx.HTTPStatusError: If deletion fails or email already sent.
        """
        result, _ = await self._request("DELETE", f"/v1/emails/{email_id}")
        return result

    # ==================== Invite Endpoints ====================

    async def accept_invite(self, domain: str) -> dict:
        """Accept a domain invite.

        Args:
            domain: Domain name to accept invite for.

        Returns:
            Dict containing acceptance confirmation.

        Raises:
            httpx.HTTPStatusError: If no invite exists or request fails.
        """
        result, _ = await self._request("GET", f"/v1/domains/{domain}/invites")
        return result

    async def create_invite(self, domain: str, email: str, group: str = "user") -> dict:
        """Create a domain invite.

        Args:
            domain: Domain name.
            email: Email address to invite.
            group: Role to assign: "admin" or "user".

        Returns:
            Dict containing the created invite details.

        Raises:
            httpx.HTTPStatusError: If invite creation fails.
        """
        data = {"email": email, "group": group}
        result, _ = await self._request(
            "POST", f"/v1/domains/{domain}/invites", data=data
        )
        return result

    async def delete_invite(self, domain: str, email: str) -> dict:
        """Remove a domain invite.

        Args:
            domain: Domain name.
            email: Email address of the invite to remove.

        Returns:
            Dict containing deletion confirmation.

        Raises:
            httpx.HTTPStatusError: If deletion fails.
        """
        data = {"email": email}
        result, _ = await self._request(
            "DELETE", f"/v1/domains/{domain}/invites", data=data
        )
        return result

    # ==================== Member Endpoints ====================

    async def update_member(self, domain: str, member_id: str, group: str) -> dict:
        """Update domain member role.

        Args:
            domain: Domain name.
            member_id: Member ID.
            group: New role: "admin" or "user".

        Returns:
            Dict containing the updated member details.

        Raises:
            httpx.HTTPStatusError: If update fails.
        """
        data = {"group": group}
        result, _ = await self._request(
            "PUT", f"/v1/domains/{domain}/members/{member_id}", data=data
        )
        return result

    async def delete_member(self, domain: str, member_id: str) -> dict:
        """Remove a domain member.

        Args:
            domain: Domain name.
            member_id: Member ID to remove.

        Returns:
            Dict containing deletion confirmation.

        Raises:
            httpx.HTTPStatusError: If deletion fails.
        """
        result, _ = await self._request(
            "DELETE", f"/v1/domains/{domain}/members/{member_id}"
        )
        return result

    # ==================== Log Endpoints ====================

    async def download_logs(
        self,
        domain: Optional[str] = None,
        query: Optional[str] = None,
    ) -> dict:
        """Request log download.

        Logs will be emailed as a gzip-compressed CSV attachment.
        Limited to 10 requests per day.

        Args:
            domain: Filter logs by domain.
            query: Search query or date filter (e.g., "M/D/YY" format).

        Returns:
            Dict containing confirmation that logs will be emailed.

        Raises:
            httpx.HTTPStatusError: If request fails or rate limit exceeded.
        """
        params = {"domain": domain, "q": query}
        result, _ = await self._request("GET", "/v1/logs/download", params=params)
        return result

    # ==================== Encrypt Endpoints ====================

    async def encrypt_txt_record(self, input_text: str) -> dict:
        """Encrypt a TXT record value.

        Useful for encrypting forwarding addresses in DNS TXT records.

        Args:
            input_text: The value to encrypt (e.g., an email address).

        Returns:
            Dict containing the encrypted value.

        Raises:
            httpx.HTTPStatusError: If encryption fails.
        """
        data = {"input": input_text}
        result, _ = await self._request("POST", "/v1/encrypt", data=data)
        return result
