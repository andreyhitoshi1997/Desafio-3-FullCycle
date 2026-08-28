const settings = {
  dbUser: process.env.DB_USER || "admin_master",
  dbPass: process.env.DB_PASS || "",
  dbPath: process.env.DB_PATH || ":memory:",
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
  smtpUser: process.env.SMTP_USER || "",
  adminToken: process.env.ADMIN_TOKEN || "change-me-in-production",
  port: parseInt(process.env.PORT, 10) || 3000,
  bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS, 10) || 10,
};

module.exports = settings;
