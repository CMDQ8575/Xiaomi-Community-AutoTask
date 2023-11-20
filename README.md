# Xiaomi Community AutoTask

A Python script for automatically completing Xiaomi community points tasks

#### Thanks [@mumu-learn](https://github.com/mumu-learn) for testing

# Support environment

The script only support **Python3.10**, or you can use the binary file

# How to use

1. Fill in your account and password in `config.toml`

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Install LibGL (Linux Only)

   ```bash
   apt install libgl1-mesa-glx
   ```

4. Run and enjoy

5. If use binary file, run  `cd /path/to/your/binary && ./xiaomi`  instead of `/path/to/your/binary/xiaomi`

# Change Log

## 2023-11-20

- Fix token acquisition
- Package the functions into a library file
- Package all files into a binary file
- Bug fix

## 2023-11-12

- Token acquisition support
- Multi-account support

## 2023-11-11

- Fixed `check_in` by adding token validation

## 2023-11-09

- First build
