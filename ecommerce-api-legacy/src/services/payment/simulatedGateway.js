const logger = require("../../lib/logger");
const cardValidator = require("./cardValidator");

const INSUFFICIENT_FUNDS_LAST4 = "0000";

// Simulated gateway: no real processor is called. Kept as an isolated adapter
// so a real gateway can implement the same `authorize` contract later without
// touching paymentService or the controller.
function createSimulatedGateway({ gatewayKey }) {
  if (!gatewayKey) {
    logger.warn("Simulated payment gateway created without a gateway key; all payments will be denied");
  }

  function authorize({ cardNumber, amount }) {
    if (!gatewayKey) {
      return { status: "DENIED", reason: "gateway_unconfigured" };
    }

    const card = cardValidator.validate(cardNumber);
    if (!card.valid) {
      return { status: "DENIED", reason: card.reason };
    }

    if (card.last4 === INSUFFICIENT_FUNDS_LAST4) {
      return { status: "DENIED", reason: "insufficient_funds" };
    }

    return { status: "PAID", reason: "approved" };
  }

  return { authorize };
}

module.exports = { createSimulatedGateway };
