# Xiaomi Community AutoTask

A Python script for automatically completing Xiaomi community points tasks

### 目前遇到将validate发送至小米验证服务器后无法返回token的问题，由于近期工作繁忙暂无法及时查错修复，故开源。欢迎各位下载源码进行调试修复并Pull requests

# How to use

1. Fill in your account and password in `config.toml`

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Install node.js

   ```bash
   apt/yum install nodejs
   ```

4. Run and enjoy

# Thanks

1. [@mumu-learn](https://github.com/mumu-learn) for testing
2. [@sijiyo](https://github.com/sijiyo) for geetest_slide function
3. [@LorenzTesch](https://github.com/LorenzTesch) for getting slide distance function with JS

# Change Log

## 2023-11-23

- Add getting slide distance with JS
- Add some error messages
- Create config file when it not exists
- Reopen source

## 2023-11-20

- Fix token acquisition
- Package the functions into a library file
- Package all files into a binary file
- Bug fix

## 2023-11-12

- Token acquisition support
- Multi-account support

## 2023-11-11

- Fix `check_in` by adding token validation

## 2023-11-09

- First build
