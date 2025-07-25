#################################################################################
# Eclipse Tractus-X - Software Development KIT
#
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the
# License for the specific language govern in permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0
#################################################################################

# Part of this content was generated by Co-Pilot and reviewed by a human developer.

from typing import Dict, List

from requests import HTTPError

from tractusx_sdk.industry.models.aas.v3 import (
    AssetKind,
    ShellDescriptor,
    SubModelDescriptor,
    GetAllShellDescriptorsResponse,
    GetSubmodelDescriptorsByAssResponse,
    Result,
    SpecificAssetId,
    ServiceDescription,
)
from tractusx_sdk.dataspace.tools import HttpTools, encode_as_base64_url_safe
from tractusx_sdk.dataspace.managers.oauth2_manager import OAuth2Manager


class AasService:
    """
    Service for interacting with the Digital Twin Registry (DTR).

    This service provides methods for retrieving and creating shell descriptors
    and submodel descriptors in the Digital Twin Registry.
    """

    def __init__(
        self,
        base_url: str,
        base_lookup_url: str,
        api_path: str,
        auth_service: OAuth2Manager = None,
        verify_ssl: bool = True,
    ):
        """
        Initialize the DTR service.

        Args:
            base_url (str): Base URL of the AAS API
            base_lookup_url (str): Base URL for the AAS lookup service
            api_path (str): API endpoint path
            auth_service (OAuth2Manager, optional): Authentication service for obtaining access tokens
            verify_ssl (bool): Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip("/")
        self.base_lookup_url = base_lookup_url.rstrip("/")
        self.api_path = api_path.rstrip("/")
        self.auth_service = auth_service
        self.verify_ssl = verify_ssl

        # Build complete URLs
        self.aas_url = f"{self.base_url}{self.api_path}"
        self.aas_lookup_url = f"{self.base_lookup_url}{self.api_path}"

    def _prepare_headers(
        self, bpn: str | None = None, method: str = "GET"
    ) -> Dict[str, str]:
        """
        Prepare headers for DTR API requests.

        Args:
            bpn (str, optional): Business Partner Number for authorization

        Returns:
            Dict[str, str]: Headers for the request
        """
        headers = {"Accept": "application/json"}

        # Add content type for POST requests
        if method == "POST" or method == "PUT":
            headers["Content-Type"] = "application/json"

        # Add authentication if available
        if self.auth_service:
            headers = self.auth_service.add_auth_header(headers=headers)

        # Add BPN if provided
        if bpn:
            headers["Edc-Bpn"] = bpn

        return headers

    def get_all_asset_administration_shell_descriptors(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        asset_kind: AssetKind | None = None,
        asset_type: str | None = None,
        bpn: str | None = None,
    ) -> GetAllShellDescriptorsResponse | Result:
        """
        Retrieves all Asset Administration Shell (AAS) Descriptors from the Digital Twin Registry.

        This method allows querying the DTR for shell descriptors with optional filtering by
        asset kind and type, as well as pagination support.

        Args:
            limit (int, optional): The maximum number of shell descriptors to return in a single response.
            cursor (str, optional): A server-generated identifier for pagination.
            asset_kind (AssetKind_3_0, optional): Filter by the Asset's kind.
            asset_type (str, optional): Filter by the Asset's type (automatically BASE64-URL-encoded).
            bpn (str, optional): Business Partner Number for authorization.

        Returns:
            GetAllShellDescriptorsResponse: Response containing shell descriptors and pagination metadata.
            Result: The result object if the request returns a non-2XX status code.

        Raises:
            ConnectionError: If there is a network connectivity issue
            TimeoutError: If the request times out
            ValidationError: If the JSON response does not match the expected model.
        """
        # Prepare query parameters
        params = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if asset_kind is not None:
            params["assetKind"] = asset_kind.value
        if asset_type is not None:
            params["assetType"] = encode_as_base64_url_safe(asset_type)

        # Get headers and session
        headers = self._prepare_headers(bpn)

        # Make the request
        url = f"{self.aas_url}/shell-descriptors"
        response = HttpTools.do_get(
            url=url,
            params=params,
            headers=headers,
            verify=self.verify_ssl,
        )

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        # Return the parsed response
        return GetAllShellDescriptorsResponse(**response.json())

    def get_asset_administration_shell_descriptor_by_id(
        self, aas_identifier: str, bpn: str | None = None
    ) -> ShellDescriptor | Result:
        """
        Retrieves a specific Asset Administration Shell (AAS) Descriptor by its identifier.

        This method fetches a single AAS descriptor from the Digital Twin Registry using its unique ID.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            bpn (str, optional): Business Partner Number for authorization purposes. When provided,
                it is added as an Edc-Bpn header to the request.

        Returns:
            ShellDescriptor: The requested Asset Administration Shell Descriptor object.
            Result: The result object if the request returns a non-2XX status code.


        Raises:
            ConnectionError: If there is a network connectivity issue.
            TimeoutError: If the request times out.
            ValidationError: If the JSON response does not match the expected model.
        """
        # Get headers and session
        headers = self._prepare_headers(bpn)

        # Properly encode the AAS identifier as URL-safe Base64
        encoded_identifier = encode_as_base64_url_safe(aas_identifier)

        # Make the request
        url = f"{self.aas_url}/shell-descriptors/{encoded_identifier}"
        response = HttpTools.do_get(url=url, headers=headers, verify=self.verify_ssl)

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        # Return the parsed response
        return ShellDescriptor(**response.json())

    def update_asset_administration_shell_descriptor(
        self,
        aas_identifier: str,
        shell_descriptor: ShellDescriptor,
        bpn: str | None = None,
    ) -> None | Result:
        """
        Updates an existing Asset Administration Shell (AAS) Descriptor.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            bpn (str, optional): Business Partner Number for authorization purposes. When provided,
                it is added as an Edc-Bpn header to the request.

        Returns:
            None: if the request is successful
            Result: if the request returns a non-2XX status code

        Raises:
            ConnectionError: If there is a network connectivity issue.
            TimeoutError: If the request times out.
            ValidationError: If the JSON response does not match the expected model.
        """
        # Get headers and session
        headers = self._prepare_headers(bpn, method="PUT")

        # Properly encode the AAS identifier as URL-safe Base64
        encoded_identifier = encode_as_base64_url_safe(aas_identifier)

        # Convert ShellDescriptor to dictionary(json)
        shell_dict = shell_descriptor.to_dict()

        # Make the request
        url = f"{self.aas_url}/shell-descriptors/{encoded_identifier}"
        response = HttpTools.do_put(
            url=url, headers=headers, json=shell_dict, verify=self.verify_ssl
        )

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        return None

    def delete_asset_administration_shell_descriptor(
        self, aas_identifier: str, bpn: str | None = None
    ) -> None | Result:
        """
        Deletes an existing Asset Administration Shell (AAS) Descriptor.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            bpn (str, optional): Business Partner Number for authorization purposes. When provided,
                it is added as an Edc-Bpn header to the request.

        Raises:
            ConnectionError: If there is a network connectivity issue.
            TimeoutError: If the request times out.
            ValidationError: If the JSON response does not match the expected model.
        """
        # Get headers and session
        headers = self._prepare_headers(bpn)

        # Properly encode the AAS identifier as URL-safe Base64
        encoded_identifier = encode_as_base64_url_safe(aas_identifier)

        # Make the request
        url = f"{self.aas_url}/shell-descriptors/{encoded_identifier}"
        response = HttpTools.do_delete(url=url, headers=headers, verify=self.verify_ssl)

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        return None

    def get_submodel_descriptors_by_aas_id(
        self,
        aas_identifier: str,
        limit: int | None = None,
        cursor: str | None = None,
        bpn: str | None = None,
    ) -> GetSubmodelDescriptorsByAssResponse | Result:
        """
        Retrieves all Submodel Descriptors associated with a specific Asset Administration Shell (AAS).

        This method fetches all submodels belonging to a particular AAS from the Digital Twin Registry,
        with support for pagination.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            limit (int, optional): The maximum number of submodel descriptors to return in a single response.
                Must be a positive integer if provided.
            cursor (str, optional): A server-generated identifier that specifies where to continue
                listing results for pagination purposes. Obtained from a previous response.
            bpn (str, optional): Business Partner Number for authorization purposes. When provided,
                it is added as an Edc-Bpn header to the request.

        Returns:
            GetSubmodelDescriptorsByAssResponse: A response object containing:
                - A list of SubModelDescriptor objects in the 'result' field
                - Pagination metadata in the 'paging_metadata' field
            Result: The result object if the request returns a non-2XX status code.

        Raises:
            ValueError: If the limit parameter is provided but is less than 1.
            ConnectionError: If there is a network connectivity issue.
            TimeoutError: If the request times out.
            ValidationError: If the JSON response does not match the expected model.
        """
        # Validate parameters
        if limit is not None and limit < 1:
            raise ValueError("Limit must be a positive integer")

        # Construct query parameters
        params = {}
        if limit is not None:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor

        # Get headers and session
        headers = self._prepare_headers(bpn)

        # Properly encode the AAS identifier as URL-safe Base64
        encoded_identifier = encode_as_base64_url_safe(aas_identifier)

        # Make the request
        url = f"{self.aas_url}/shell-descriptors/{encoded_identifier}/submodel-descriptors"
        response = HttpTools.do_get(
            url=url,
            params=params,
            headers=headers,
            verify=self.verify_ssl,
        )

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        # Return the parsed response
        return GetSubmodelDescriptorsByAssResponse(**response.json())

    def get_submodel_descriptor_by_ass_and_submodel_id(
        self, aas_identifier: str, submodel_identifier: str, bpn: str | None = None
    ) -> SubModelDescriptor | Result:
        """
        Retrieves a specific Submodel Descriptor by its identifier and parent AAS identifier.

        This method fetches a single Submodel descriptor from the Digital Twin Registry using
        both the Asset Administration Shell ID and Submodel ID.

        Args:
            aas_identifier (str): The unique identifier of the parent Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            submodel_identifier (str): The unique identifier of the Submodel to retrieve.
                This ID will be automatically encoded as URL-safe Base64.
            bpn (str, optional): Business Partner Number for authorization purposes. When provided,
                it is added as an Edc-Bpn header to the request.

        Returns:
            SubModelDescriptor: The requested Submodel Descriptor object.
            Result: The result object if the request returns a non-2XX status code.

        Raises:
            ConnectionError: If there is a network connectivity issue.
            TimeoutError: If the request times out.
            ValidationError: If the JSON response does not match the expected model.
        """
        # Get headers and session
        headers = self._prepare_headers(bpn)

        # Properly encode the AAS and Submodel identifiers as URL-safe Base64
        encoded_aas_identifier = encode_as_base64_url_safe(aas_identifier)
        encoded_submodel_identifier = encode_as_base64_url_safe(submodel_identifier)

        # Make the request
        url = f"{self.aas_url}/shell-descriptors/{encoded_aas_identifier}/submodel-descriptors/{encoded_submodel_identifier}"
        response = HttpTools.do_get(url=url, headers=headers, verify=self.verify_ssl)

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        # Return the parsed response
        return SubModelDescriptor(**response.json())

    def create_asset_administration_shell_descriptor(
        self, shell_descriptor: ShellDescriptor, bpn: str | None = None
    ) -> ShellDescriptor | Result:
        """
        Creates a new Asset Administration Shell (AAS) Descriptor in the Digital Twin Registry.

        Args:
            shell_descriptor (ShellDescriptor): The shell descriptor to create
            bpn (str, optional): Business Partner Number for authorization purposes.
                When provided, it is added as an Edc-Bpn header to the request.

        Returns:
            ShellDescriptor: The created Asset Administration Shell Descriptor object
            with server-assigned fields.
            Result: The result object if the request returns a non-2XX status code.

        Raises:
            ConnectionError: If there is a network connectivity issue
            TimeoutError: If the request times out
            ValidationError: If the JSON response does not match the expected model
        """
        # Get headers with content type added
        headers = self._prepare_headers(bpn, method="POST")

        # Convert ShellDescriptor_3_0 to dictionary with proper handling of empty lists
        shell_descriptor_dict = shell_descriptor.to_dict()

        # Make the request
        url = f"{self.aas_url}/shell-descriptors"
        response = HttpTools.do_post(
            url=url,
            json=shell_descriptor_dict,
            headers=headers,
            verify=self.verify_ssl,
        )

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        # Return the parsed response
        return ShellDescriptor(**response.json())

    def create_submodel_descriptor(
        self,
        aas_identifier: str,
        submodel_descriptor: SubModelDescriptor,
        bpn: str | None = None,
    ) -> SubModelDescriptor | Result:
        """
        Creates a new Submodel Descriptor in the Digital Twin Registry.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            submodel_descriptor (SubModelDescriptor): The submodel descriptor to create
            bpn (str, optional): Business Partner Number for authorization purposes.
                When provided, it is added as an Edc-Bpn header to the request.

        Returns:
            SubModelDescriptor: The created Submodel Descriptor object with server-assigned fields.
            Result: The result object if the request returns a non-2XX status code.

        Raises:
            ConnectionError: If there is a network connectivity issue
            TimeoutError: If the request times out
            ValidationError: If the JSON response does not match the expected model
        """
        # Get headers with content type added
        headers = self._prepare_headers(bpn, method="POST")

        # Convert submodel to dictionary(json)
        submodel_dict = submodel_descriptor.to_dict()

        # Properly encode the AAS identifier as URL-safe Base64
        encoded_aas_id = encode_as_base64_url_safe(aas_identifier)

        # Make the request
        url = f"{self.aas_url}/shell-descriptors/{encoded_aas_id}/submodel-descriptors"
        response = HttpTools.do_post(
            url=url,
            json=submodel_dict,
            headers=headers,
            verify=self.verify_ssl,
        )

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        # Return the parsed response
        return SubModelDescriptor(**response.json())

    def update_submodel_descriptor(
        self,
        aas_identifier: str,
        submodel_identifier: str,
        submodel_descriptor: SubModelDescriptor,
        bpn: str | None = None,
    ) -> None | Result:
        """Updates an existing Submodel Descriptor.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            submodel_identifier (str): The unique identifier of the Submodel to update.
                This ID will be automatically encoded as URL-safe Base64.
            bpn (str | None, optional): Business Partner Number for authorization purposes.
                When provided, it is added as an Edc-Bpn header to the request.

        Returns:
            None | Result: None if the request is successful, Result if the request returns a non-2XX status code.

        Raises:
            ConnectionError: If there is a network connectivity issue
            TimeoutError: If the request times out
            ValidationError: If the JSON response does not match the expected model
        """
        # Get headers with content type added
        headers = self._prepare_headers(bpn, method="PUT")

        # Convert submodel to dictionary(json)
        submodel_dict = submodel_descriptor.to_dict()

        # Properly encode the identifiers as URL-safe Base64
        encoded_aas_identifier = encode_as_base64_url_safe(aas_identifier)
        encoded_submodel_identifier = encode_as_base64_url_safe(submodel_identifier)

        # Make the request
        url = f"{self.aas_url}/shell-descriptors/{encoded_aas_identifier}/submodel-descriptors/{encoded_submodel_identifier}"
        response = HttpTools.do_put(
            url=url,
            json=submodel_dict,
            headers=headers,
            verify=self.verify_ssl,
        )

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        return None

    def delete_submodel_descriptor(
        self,
        aas_identifier: str,
        submodel_identifier: str,
        bpn: str | None = None,
    ) -> None | Result:
        """
        Deletes an existing Submodel Descriptor.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            submodel_identifier (str): The unique identifier of the Submodel to delete.
                This ID will be automatically encoded as URL-safe Base64.
            bpn (str | None, optional): Business Partner Number for authorization purposes.
                When provided, it is added as an Edc-Bpn header to the request.

        Returns:
            None | Result: None if the request is successful, Result if the request returns a non-2XX status code.

        Raises:
            ConnectionError: If there is a network connectivity issue
            TimeoutError: If the request times out
            ValidationError: If the JSON response does not match the expected model
        """
        # Get headers and session
        headers = self._prepare_headers(bpn)

        # Properly encode the identifiers as URL-safe Base64
        encoded_aas_identifier = encode_as_base64_url_safe(aas_identifier)
        encoded_submodel_identifier = encode_as_base64_url_safe(submodel_identifier)

        # Make the request
        url = f"{self.aas_url}/shell-descriptors/{encoded_aas_identifier}/submodel-descriptors/{encoded_submodel_identifier}"
        response = HttpTools.do_delete(url=url, headers=headers, verify=self.verify_ssl)

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        return None

    def get_description(self) -> ServiceDescription | Result:
        """
        Retrieves the service description, which presents the capabilities of the server, in particular which profiles they implement.

        Returns:
            ServiceDescription | Result: A ServiceDescription object if the request is successful,
                or a Result object if the request returns a non-2XX status code

        Raises:
            ConnectionError: If there is a network connectivity issue
            TimeoutError: If the request times out
            ValidationError: If the JSON response does not match the expected model
        """
        headers = self._prepare_headers()

        # Make the request
        url = f"{self.aas_url}/description"
        response = HttpTools.do_get(url=url, headers=headers, verify=self.verify_ssl)

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        # Return the parsed response
        return ServiceDescription(**response.json())

    def get_assets_ids_by_asset_administration_shell_id(
        self,
        aas_identifier: str,
        bpn: str | None = None,
    ) -> List[SpecificAssetId] | Result:
        """
        Retrieves all asset IDs associated with a specific Asset Administration Shell (AAS).

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
            bpn (str | None, optional): Business Partner Number for authorization purposes.
                When provided, it is added as an Edc-Bpn header to the request

        Returns:
            List[SpecificAssetId] | Result: A list of SpecificAssetId objects if the request is successful,
                or a Result object if the request returns a non-2XX status code

        Raises:
            ConnectionError: If there is a network connectivity issue
            TimeoutError: If the request times out
            ValidationError: If the JSON response does not match the expected model.
        """
        # Get headers
        headers = self._prepare_headers(bpn)

        # Properly encode the identifiers as URL-safe Base64
        encoded_aas_identifier = encode_as_base64_url_safe(aas_identifier)

        # Make the request
        url = f"{self.aas_lookup_url}/lookup/shells/{encoded_aas_identifier}"
        response = HttpTools.do_get(url=url, headers=headers, verify=self.verify_ssl)

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        parsed_response: List[SpecificAssetId] = [
            SpecificAssetId(**specific_asset_id)
            for specific_asset_id in response.json()
        ]

        # Return the parsed response
        return parsed_response

    def create_all_asset_ids_links_by_asset_administration_shell_id(
        self,
        aas_identifier: str,
        list_of_asset_ids: List[SpecificAssetId],
        bpn: str | None = None,
    ) -> List[SpecificAssetId] | Result:
        """
        Creates links between an Asset Administration Shell (AAS) and a list of assets IDs.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
            list_of_asset_ids (List[SpecificAssetId]): A list of asset IDs to link to the AAS.
            bpn (str | None, optional): Business Partner Number for authorization purposes.
                When provided, it is added as an Edc-Bpn header to the request

        Returns:
            List[SpecificAssetId] | Result: A list of SpecificAssetId objects if the request is successful,
                or a Result object if the request returns a non-2XX status code

        Raises:
            ConnectionError: If there is a network connectivity issue
            TimeoutError: If the request times outs
            ValidationError: If the JSON response does not match the expected model.
        """
        # Get headers
        headers = self._prepare_headers(bpn)

        # Properly encode the identifiers as URL-safe Base64
        encoded_aas_identifier = encode_as_base64_url_safe(aas_identifier)

        # Transform list of asset IDs to JSON
        list_of_asset_ids = [asset_id.to_dict() for asset_id in list_of_asset_ids]

        # Make the request
        url = f"{self.aas_lookup_url}/lookup/shells/{encoded_aas_identifier}"
        response = HttpTools.do_post(
            url=url, headers=headers, json=list_of_asset_ids, verify=self.verify_ssl
        )

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        parsed_response: List[SpecificAssetId] = [
            SpecificAssetId(**specific_asset_id)
            for specific_asset_id in response.json()
        ]

        # Return the parsed response
        return parsed_response

    def delete_all_asset_ids_links_by_asset_administration_shell_id(
        self,
        aas_identifier: str,
        bpn: str | None = None,
    ) -> None | Result:
        """
        Deletes all links between an Asset Administration Shell (AAS) and its associated asset IDs.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
            bpn (str | None, optional): Business Partner Number for authorization purposes.
                When provided, it is added as an Edc-Bpn header to the request

        Returns:
            None | Result: None if the request is successful, Result if the request returns a non-2XX status code

        Raises:
            ConnectionError: If there is a network connectivity issue
            TimeoutError: If the request times out
            ValidationError: If the JSON response does not match the expected model.
        """
        # Get headers
        headers = self._prepare_headers(bpn)

        # Properly encode the identifiers as URL-safe Base64
        encoded_aas_identifier = encode_as_base64_url_safe(aas_identifier)

        # Make the request
        url = f"{self.aas_lookup_url}/lookup/shells/{encoded_aas_identifier}"
        response = HttpTools.do_delete(url=url, headers=headers, verify=self.verify_ssl)

        try:
            # Check for errors
            response.raise_for_status()
        except HTTPError as _:
            # Return the parsed response
            return Result(**response.json())

        # Return the parsed response
        return None
