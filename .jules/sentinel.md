## 2025-02-14 - Password Policy Improvement
**Vulnerability:** Weak Password Policy (Length Limit)
**Learning:** The application restricted passwords to a maximum of 36 characters. This prevents users from using strong passphrases or generated passwords, which is contrary to NIST SP 800-63B guidelines.
**Prevention:** Always allow long passwords (e.g., up to 128 or more characters) to encourage the use of passphrases. Ensure the hashing algorithm (like Argon2 or Bcrypt) handles long inputs correctly without truncation or DoS risk.
