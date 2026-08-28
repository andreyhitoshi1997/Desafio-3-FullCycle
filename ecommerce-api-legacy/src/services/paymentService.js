const logger = require("../lib/logger");

const APPROVED_PREFIX = "4";

function processPayment(cardNumber, gatewayKey) {
  logger.info("Processing payment", { cardPrefix: cardNumber.substring(0, 4), gateway: "mock" });
  const approved = cardNumber.startsWith(APPROVED_PREFIX);
  return approved ? "PAID" : "DENIED";
}

module.exports = { processPayment };
