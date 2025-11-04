# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Memoria, please report it by creating a private security advisory on GitHub or by contacting the maintainers directly.

**Please do not report security vulnerabilities through public GitHub issues.**

## Supported Versions

Currently, only the latest version is supported with security updates.

## Security Best Practices

When deploying Memoria:

1. **Environment Variables**: Never commit `.env` files or expose API keys
2. **Database**: Use strong passwords and secure connection strings
3. **JWT Secret**: Generate a strong, random SECRET_KEY (at least 32 characters)
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure CORS to only allow your frontend domain
6. **API Keys**: Rotate API keys regularly and use environment-specific keys
7. **Dependencies**: Keep dependencies up to date

## Known Security Considerations

- This is a portfolio/learning project and may not be suitable for production use without additional security hardening
- Rate limiting is implemented but should be reviewed for production use
- User input validation is basic and should be enhanced for production
