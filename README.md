# Fetch Network Event Poller

Fetch Network Event Poller is a Python application designed to efficiently fetch and filter network events through polling.

## 📑 Table of Contents

- [Fetch Network Event Poller](#fetch-network-event-poller)
  - [📑 Table of Contents](#-table-of-contents)
  - [🌟 Overview](#-overview)
  - [🔥 Features](#-features)
  - [🚀 Technology Stack](#-technology-stack)
  - [⚙️ Requirements](#️-requirements)
  - [📥 Installation](#-installation)
    - [Using Poetry:](#using-poetry)
    - [Using Pip:](#using-pip)
  - [🎮 Getting Started](#-getting-started)
  - [🤝 Contributing](#-contributing)
  - [📜 License](#-license)
  - [📞 Contact](#-contact)

## 🌟 Overview

Fetch Network Event Poller is a Python tool that utilizes gRPC for network connectivity. It allows you to fetch and filter network events related to transactions, providing the ability to specify criteria such as action types and wallet addresses for result refinement.

## 🔥 Features

- Real-time fetching of network events.
- Filtering events based on action types and wallet addresses.
- Well-structured output for easy integration and processing.
- SSL/TLS support through Certifi for secure communication.

## 🚀 Technology Stack

- **[Python](https://www.python.org/)**: A robust and dynamic language that enables fast application development.
- **[gRPC](https://grpc.io/)**: An efficient, open-source framework for handling streaming and non-streaming requests.
- **[Certifi](https://pypi.org/project/certifi/)**: A collection of root certificates used for secure communication via TLS.

## ⚙️ Requirements

- Python 3.8+
- Poetry or Pip

## 📥 Installation

You can install the package using either Poetry or Pip:

### Using Poetry:

```sh
poetry add git+https://github.com/fetchai/fetch-network-event-polling.git
```

### Using Pip:

```sh
pip install git+https://github.com/fetchai/fetch-network-event-polling.git
```

## 🎮 Getting Started

Follow the simple guide below to get started with the Fetch Network Event Poller:

1. Import the required classes:

    ```python
    from eventfetcher import EventRetriever, ActionType
    ```

2. Initialize the `EventRetriever` with the desired contract address and gRPC URL:

    ```python
    fetcher = EventRetriever(contract_address='YOUR_CONTRACT_ADDRESS', grpc_url='YOUR_GRPC_URL')
    ```

3. Invoke the `fetch_events` method to retrieve events:

    ```python
    events = fetcher.fetch_events(discard_processed_events=False, action_type=ActionType.TRANSFER)
    ```

4. Process or print the events according to your needs:

    ```python
    for event in events:
        print(event)
    ```

## 🤝 Contributing

We welcome contributions in various forms, including documentation, examples, bug fixes, or new features. To ensure a welcoming environment for all, please follow our Code of Conduct.

1. Fork the repository on GitHub.

2. Clone the forked repository:

    ```sh
    git clone https://github.com/YOUR-USERNAME/fetch-network-event-polling.git
    ```

3. Navigate to the project directory and install dependencies:

    ```sh
    cd fetch-network-event-polling
    poetry install
    ```

4. Implement your changes and submit a Pull Request!

## 📜 License

This project is licensed under the terms of the [Apache License 2.0](https://github.com/fetchai/fetch-network-event-polling/blob/main/LICENSE).

## 📞 Contact

If you have specific questions or issues, please report them via GitHub issues.