# FastAPI Bootstrap
[![PyPI - Version](https://img.shields.io/pypi/v/fastapi-bootstrap.svg)](https://pypi.org/project/fastapi-bootstrap)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastapi-bootstrap.svg)](https://pypi.org/project/fastapi-bootstrap)
[![Deploy to GHCR](https://github.com/0x6f677548/fastapi-bootstrap/actions/workflows/build-and-publish-to-ghcr.yml/badge.svg)](https://github.com/0x6f677548/fastapi-bootstrap/actions/workflows/build-and-publish-to-ghcr.yml)
[![Deploy](https://github.com/0x6f677548/fastapi-bootstrap/actions/workflows/deploy-to-dockerhost.yml/badge.svg)](https://github.com/0x6f677548/fastapi-bootstrap/actions/workflows/deploy-to-dockerhost.yml)
[![GitHub - Lint](https://github.com/0x6f677548/fastapi-bootstrap/actions/workflows/lint.yml/badge.svg)](https://github.com/0x6f677548/fastapi-bootstrap/actions/workflows/lint.yml)
[![GitHub - Test](https://github.com/0x6f677548/fastapi-bootstrap/actions/workflows/test.yml/badge.svg)](https://github.com/0x6f677548/fastapi-bootstrap/actions/workflows/test.yml)

FastAPI Bootstrap is a project template that includes some best practices that I use on my FastAPI projects. It includes a FastAPI server, an NGINX server acting as a reverse proxy, and an OpenTelemetry collector. 

# Architecture
The project is composed of the following containers:
- **api-proxy**: An NGINX server that acts as a reverse proxy for api-server (FastAPI). 
All inbound requests are limited to cloudflare IPs and forwarded to the api-server, after initial checks. Nginx longs are send through syslog to the otel-collector.
- **api-server**: A FastAPI server that exposes a router through a REST API and is instrumented with OpenTelemetry, sending traces, metrics, and logs to the otel-collector.
- **otel_collector**: An OpenTelemetry collector that exposes syslog and otel endpoints to receive logs, traces, and metrics from the api-proxy and api-server and forwards them to a remote OTEL compliant backend, which may be Jaeger, Prometheus, New Relic, Datadog, or any other backend that supports the OpenTelemetry protocol.
- **jaeger**: A Jaeger server that receives traces from the otel-collector and displays them in a web interface.

## GitHub Actions
Some github actions are also included to lint, test, build, and deploy the project. Deployments are made to a remote server using TailScale, SSH, and Docker.
- **lint**: Lints the code using black and ruff (through hatch).
- **test**: Runs the tests using pytest.
- **lint-super-linter**: Lints the code using super-linter.
- **create-draft-release**: Creates a draft release.
- **build-artifacts**: Builds the artifacts for the project.
- **build-and-publish-to-ghcr**: Builds the Docker images and publishes them to the GitHub Container Registry.
- **build-and-publish-to-pypi**: Builds the Python package and publishes it to PyPI.
- **deploy-to-dockerhost**: Deploys the Docker images to a remote server using TailScale, SSH, and Docker.
- **clear-actions-cache**: Clears the GitHub Actions cache.
- **debug-context**: Prints the GitHub Actions context.


 
## Other components
Some of the tools and libraries used in this project are:
- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
- **Hatch**: A modern project, package, and virtual env manager for Python.
- **NGINX**: A web server that can also be used as a reverse proxy, load balancer, etc.
- **OpenTelemetry**: A set of APIs, libraries, agents, and instrumentation to provide observability.
- **Tailscale**: A ZeroTier alternative that provides a secure, private network for your servers.
- **Docker**: A set of platform as a service products that use OS-level virtualization to deliver software in packages called containers.
