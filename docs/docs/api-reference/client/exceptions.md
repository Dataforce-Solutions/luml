<a id="luml_api._exceptions"></a>

# luml_api._exceptions

<a id="luml_api._exceptions.LumlAPIError"></a>

## LumlAPIError Objects

```python
class LumlAPIError(Exception)
```

Base class for every error the LUML API SDK raises.

<a id="luml_api._exceptions.CapabilityNotSupportedError"></a>

## CapabilityNotSupportedError Objects

```python
class CapabilityNotSupportedError(LumlAPIError)
```

A Satellite does not have the capability an operation needs.

Raised before any request is sent: the capability is missing from the
Satellite's `present_capabilities` on the Platform record, or the
deployment has no monitoring URL reported.

<a id="luml_api._exceptions.UnsupportedCapabilityVersionError"></a>

## UnsupportedCapabilityVersionError Objects

```python
class UnsupportedCapabilityVersionError(LumlAPIError)
```

The SDK and the Satellite share no common capability API version.

Carries both sides: `sdk_versions` the SDK implements and
`satellite_versions` the Satellite advertises.

<a id="luml_api._exceptions.NotAvailableInVersionError"></a>

## NotAvailableInVersionError Objects

```python
class NotAvailableInVersionError(LumlAPIError)
```

The selected capability API version does not include this operation.

<a id="luml_api._exceptions.ContractViolationError"></a>

## ContractViolationError Objects

```python
class ContractViolationError(LumlAPIError)
```

A Satellite response is missing the structure its declared API version requires.

Names the Satellite and operation; `missing_fields` lists the required
top-level fields that were absent.

<a id="luml_api._exceptions.ConfigurationError"></a>

## ConfigurationError Objects

```python
class ConfigurationError(LumlAPIError)
```

The client is missing configuration (organization, orbit or collection).

<a id="luml_api._exceptions.MultipleResourcesFoundError"></a>

## MultipleResourcesFoundError Objects

```python
class MultipleResourcesFoundError(LumlAPIError)
```

A name lookup matched more than one resource; use the id instead.

<a id="luml_api._exceptions.ResourceNotFoundError"></a>

## ResourceNotFoundError Objects

```python
class ResourceNotFoundError(Exception)
```

A resource referenced by id or name does not exist.

<a id="luml_api._exceptions.OrbitResourceNotFoundError"></a>

## OrbitResourceNotFoundError Objects

```python
class OrbitResourceNotFoundError(ResourceNotFoundError)
```

The referenced Orbit does not exist.

<a id="luml_api._exceptions.OrganizationResourceNotFoundError"></a>

## OrganizationResourceNotFoundError Objects

```python
class OrganizationResourceNotFoundError(ResourceNotFoundError)
```

The referenced Organization does not exist.

<a id="luml_api._exceptions.CollectionResourceNotFoundError"></a>

## CollectionResourceNotFoundError Objects

```python
class CollectionResourceNotFoundError(ResourceNotFoundError)
```

The referenced Collection does not exist.

<a id="luml_api._exceptions.APIError"></a>

## APIError Objects

```python
class APIError(LumlAPIError)
```

Base class for errors tied to an HTTP request.

<a id="luml_api._exceptions.APIResponseValidationError"></a>

## APIResponseValidationError Objects

```python
class APIResponseValidationError(APIError)
```

The API answered, but the payload did not match the expected schema.

<a id="luml_api._exceptions.APIStatusError"></a>

## APIStatusError Objects

```python
class APIStatusError(APIError)
```

Base class for non-success HTTP status responses.

<a id="luml_api._exceptions.BadRequestError"></a>

## BadRequestError Objects

```python
class BadRequestError(APIStatusError)
```

The request was malformed (HTTP 400).

<a id="luml_api._exceptions.AuthenticationError"></a>

## AuthenticationError Objects

```python
class AuthenticationError(APIStatusError)
```

The API key is missing or invalid (HTTP 401).

<a id="luml_api._exceptions.PermissionDeniedError"></a>

## PermissionDeniedError Objects

```python
class PermissionDeniedError(APIStatusError)
```

The API key lacks access to this resource (HTTP 403).

<a id="luml_api._exceptions.NotFoundError"></a>

## NotFoundError Objects

```python
class NotFoundError(APIStatusError)
```

The requested resource does not exist (HTTP 404).

<a id="luml_api._exceptions.SatelliteOutOfSyncError"></a>

## SatelliteOutOfSyncError Objects

```python
class SatelliteOutOfSyncError(NotFoundError)
```

A Satellite answered `unknown_route` for a path its stored capabilities promise.

The Platform's copy of the Satellite's capabilities no longer matches the
running build; restarting or re-pairing the Satellite refreshes it.

<a id="luml_api._exceptions.ConflictError"></a>

## ConflictError Objects

```python
class ConflictError(APIStatusError)
```

The request conflicts with the resource's current state (HTTP 409).

<a id="luml_api._exceptions.UnprocessableEntityError"></a>

## UnprocessableEntityError Objects

```python
class UnprocessableEntityError(APIStatusError)
```

The server rejected the request's values (HTTP 422).

<a id="luml_api._exceptions.InternalServerError"></a>

## InternalServerError Objects

```python
class InternalServerError(APIStatusError)
```

The server failed to process the request (HTTP 5xx).

<a id="luml_api._exceptions.ArtifactDeleteError"></a>

## ArtifactDeleteError Objects

```python
class ArtifactDeleteError(LumlAPIError)
```

A single artifact stayed in the registry after a deletion attempt.

<a id="luml_api._exceptions.ArtifactBatchDeleteError"></a>

## ArtifactBatchDeleteError Objects

```python
class ArtifactBatchDeleteError(LumlAPIError)
```

A platform request interrupted a batch artifact deletion.

<a id="luml_api._exceptions.FileError"></a>

## FileError Objects

```python
class FileError(Exception)
```

Base class for bucket file transfer errors.

<a id="luml_api._exceptions.FileUploadError"></a>

## FileUploadError Objects

```python
class FileUploadError(FileError)
```

Uploading a file to the bucket failed.

<a id="luml_api._exceptions.FileDownloadError"></a>

## FileDownloadError Objects

```python
class FileDownloadError(FileError)
```

Downloading a file from the bucket failed.

