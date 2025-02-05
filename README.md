# ssh-publish

Publish python packages to VPS via SSH. This project simplifies the process of uploading and managing python packages on your self-hosted package repository.

## Installation

You can install the package via pip:

```
pip install ssh-publish
```

## Usage

```
ssh-publish HOST DIR
```

This commands uploads the latest built whl file from dist directory to `HOST` at `DIR`.

Examples:

```
ssh-publish 192.168.10.100 static/my-pkg
ssh-publish username@192.168.10.100 packages/my-pkg
```

## License

This project is licensed under the terms of the MIT license.
