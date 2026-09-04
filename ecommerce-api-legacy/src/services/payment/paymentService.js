const logger = require("../../lib/logger");

const PAYMENT_STATUS = Object.freeze({ PAID: "PAID", DENIED: "DENIED" });

// Port: the controller depends only on this shape. Swapping the simulated
// gateway for a real one later means changing the composition root only.
function createPaymentService({ gateway }) {
  async function processPayment({ cardNumber, amount }) {
    try {
      const result = gateway.authorize({ cardNumber, amount });
      logger.info("Payment processed", { status: result.status, reason: result.reason });
      return result;
    } catch (err) {
      logger.error("Unexpected error processing payment", { message: err.message });
      return { status: PAYMENT_STATUS.DENIED, reason: "internal_error" };
    }
  }

  return { processPayment };
}

module.exports = { createPaymentService, PAYMENT_STATUS };
